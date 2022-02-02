from django.db import models
from django.utils import timezone

# Create your models here.
class GameRequest(models.Model):
    created = models.DateTimeField(default=timezone.now)
    game_name = models.CharField(max_length=140)

    def __str__(self) -> str:
        return self.game_name
