from django.db import models
from django.utils import timezone

from authentication.models import User
from profiles.models import Game

# Create your models here.
class Clip(models.Model):
    created_date = models.DateField(default=timezone.now)
    created_datetime = models.DateTimeField(default=timezone.now)
    uploader = models.ForeignKey(
        User, related_name="clip_uploads", on_delete=models.PROTECT
    )
    game = models.ForeignKey(Game, related_name="clips", on_delete=models.PROTECT)
    title = models.CharField(max_length=80, blank=False, null=False)
    url = models.URLField(null=False, blank=False)
