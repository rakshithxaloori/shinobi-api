from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.validators import MinLengthValidator


from authentication.models import User
from clips.models import Clip
from feed.utils import POST_TITLE_LENGTH
from profiles.models import Game


def generate_random_id():
    id_str = get_random_string(length=12)
    while Post.objects.filter(pk=id_str).exists():
        id_str = get_random_string(length=12)
    return id_str


class Post(models.Model):
    # A post is a clip or a screenshot
    id = models.CharField(
        max_length=12,
        primary_key=True,
        default=generate_random_id,
        validators=[MinLengthValidator(limit_value=12)],
    )
    created_datetime = models.DateTimeField(default=timezone.now)

    clip = models.OneToOneField(
        Clip, related_name="clip_post", blank=True, null=True, on_delete=models.CASCADE
    )
    posted_by = models.ForeignKey(User, related_name="posts", on_delete=models.PROTECT)
    game = models.ForeignKey(
        Game, related_name="game_posts", blank=True, null=True, on_delete=models.PROTECT
    )
    title = models.CharField(max_length=POST_TITLE_LENGTH, blank=True, null=True)
    tags = models.ManyToManyField(
        User, related_name="tegged_in", blank=True, through="Tag"
    )
    # ISO alpha_2 code
    country_code = models.CharField(max_length=2, null=True, blank=True)
    liked_by = models.ManyToManyField(
        User, related_name="liked_posts", blank=True, through="Like"
    )
    share_count = models.PositiveIntegerField(default=0)

    # REPOST
    is_repost = models.BooleanField(default=False)
    repost = models.ForeignKey(
        "Post", related_name="reposts", blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return "{}'s {} {} || {} days ago".format(
            self.posted_by.username,
            self.id,
            "REPOST" if self.is_repost else "POST",
            (timezone.now() - self.created_datetime).days,
        )

    class Meta:
        ordering = ["-created_datetime"]


class Like(models.Model):
    created_datetime = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "{} liked {} post".format(self.user.username, self.post.id)


class Tag(models.Model):
    created_datetime = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "{} tagged in {} post".format(self.user.username, self.post.id)


class Report(models.Model):
    created_datetime = models.DateTimeField(default=timezone.now)

    reported_by = models.ForeignKey(
        User, related_name="post_reports", on_delete=models.PROTECT
    )
    post = models.ForeignKey(Post, related_name="reports", on_delete=models.CASCADE)
    is_not_playing = models.BooleanField(default=False)
    is_not_game_clip = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "{} reported {} post".format(self.reported_by.username, self.post.id)

    class Meta:
        ordering = ["-created_datetime"]
