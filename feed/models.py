from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.validators import MinLengthValidator


from authentication.models import User
from clips.models import Clip
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
        Clip, related_name="clip_post", on_delete=models.CASCADE
    )
    uploader = models.ForeignKey(User, related_name="posts", on_delete=models.PROTECT)
    game = models.ForeignKey(Game, related_name="game_posts", on_delete=models.PROTECT)
    title = models.CharField(max_length=80)
    liked_by = models.ManyToManyField(
        User, related_name="liked_posts", blank=True, through="Like"
    )
    share_count = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return "{}'s {} post".format(self.uploader.username, self.id)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "{} liked {} post".format(self.user.username, self.post.id)


class Report(models.Model):
    reported_by = models.ForeignKey(
        User, related_name="post_reports", on_delete=models.PROTECT
    )
    post = models.ForeignKey(Post, related_name="reports", on_delete=models.CASCADE)
    is_not_playing = models.BooleanField(default=False)
    is_not_game_clip = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "{} reported {} post".format(self.reported_by.username, self.post.id)
