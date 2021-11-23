from django.db import models
from django.utils import timezone

from authentication.models import User
from profiles.models import Game
from shinobi.utils import now_date


class Clip(models.Model):
    created_date = models.DateField(default=now_date)
    created_datetime = models.DateTimeField(default=timezone.now)
    upload_verified = models.BooleanField(default=False)
    uploader = models.ForeignKey(User, related_name="clips", on_delete=models.PROTECT)
    game = models.ForeignKey(Game, related_name="game_clips", on_delete=models.PROTECT)
    height_to_width_ratio = models.FloatField(null=False, blank=False)
    url = models.URLField(null=False, blank=False, unique=True)

    def __str__(self) -> str:
        return "{} || {} || {}".format(self.created_datetime, self.uploader, self.game)
