from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.validators import MinLengthValidator

from authentication.models import User
from profiles.models import Game
from shinobi.utils import now_date


def generate_random_id():
    id_str = get_random_string(length=12)
    while Clip.objects.filter(pk=id_str).exists():
        id_str = get_random_string(length=12)
    return id_str


class Clip(models.Model):
    MOBILE = "M"
    WEB = "W"
    UPLOADED_FROM_CHOICES = [(MOBILE, "Mobile"), (WEB, "Web")]

    id = models.CharField(
        max_length=12,
        primary_key=True,
        default=generate_random_id,
        validators=[MinLengthValidator(limit_value=12)],
    )
    created_date = models.DateField(default=now_date)
    created_datetime = models.DateTimeField(default=timezone.now)
    upload_verified = models.BooleanField(default=False)
    compressed_verified = models.BooleanField(default=False)
    uploader = models.ForeignKey(User, related_name="clips", on_delete=models.PROTECT)
    game = models.ForeignKey(Game, related_name="game_clips", on_delete=models.PROTECT)
    uploaded_from = models.CharField(max_length=1, choices=UPLOADED_FROM_CHOICES)
    title = models.CharField(max_length=80)
    liked_by = models.ManyToManyField(
        User, related_name="liked_clips", blank=True, through="Like"
    )
    viewed_by = models.ManyToManyField(
        User, related_name="viewed_clips", blank=True, through="View"
    )
    share_count = models.PositiveIntegerField(default=0)
    height = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()
    url = models.URLField(unique=True)

    def __str__(self) -> str:
        return "{} || {} || {}".format(
            self.id, self.uploader.username, self.game.game_code
        )


class View(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    clip = models.ForeignKey(Clip, on_delete=models.CASCADE)
    created_date = models.DateField(default=now_date)
    created_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return "{} viewed {} || {}".format(
            self.user.username, self.clip.id, self.clip.game.game_code
        )


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    clip = models.ForeignKey(Clip, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "{} liked {}".format(self.user.username, self.clip.id)


class Report(models.Model):
    reported_by = models.ForeignKey(
        User, related_name="clip_reports", on_delete=models.PROTECT
    )
    clip = models.ForeignKey(Clip, related_name="reports", on_delete=models.CASCADE)
    is_not_playing = models.BooleanField(default=False)
    is_not_game_clip = models.BooleanField(default=False)
