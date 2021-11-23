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
    id = models.CharField(
        max_length=12,
        primary_key=True,
        default=generate_random_id,
        validators=[MinLengthValidator(limit_value=12)],
    )
    created_date = models.DateField(default=now_date)
    created_datetime = models.DateTimeField(default=timezone.now)
    upload_verified = models.BooleanField(default=False)
    uploader = models.ForeignKey(User, related_name="clips", on_delete=models.PROTECT)
    game = models.ForeignKey(Game, related_name="game_clips", on_delete=models.PROTECT)
    height_to_width_ratio = models.FloatField(null=False, blank=False)
    url = models.URLField(null=False, blank=False, unique=True)

    def __str__(self) -> str:
        return "{} || {} || {}".format(self.created_datetime, self.uploader, self.game)
