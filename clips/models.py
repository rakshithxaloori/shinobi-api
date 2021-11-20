from django.db import models
from django.utils import timezone

from authentication.models import User
from profiles.models import Game
from shinobi.utils import now_date

# Create your models here.
class ClipToUpload(models.Model):
    created_date = models.DateField(default=now_date)
    created_datetime = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(
        User, related_name="clip_uploads", on_delete=models.PROTECT
    )
    game = models.ForeignKey(
        Game, related_name="game_clip_uploads", on_delete=models.PROTECT
    )
    url = models.URLField(null=False, blank=False, unique=True)

    def __str__(self) -> str:
        return "{} || {} || {}".format(self.created_date, self.uploaded_by, self.game)


class Clip(models.Model):
    created_date = models.DateField(default=now_date)
    created_datetime = models.DateTimeField(default=timezone.now)
    uploader = models.ForeignKey(User, related_name="clips", on_delete=models.PROTECT)
    game = models.ForeignKey(Game, related_name="game_clips", on_delete=models.PROTECT)
    title = models.CharField(max_length=80, blank=False, null=False)
    url = models.URLField(null=False, blank=False, unique=True)

    def __str__(self) -> str:
        return "{} || {} || {}".format(self.created_datetime, self.uploader, self.game)
