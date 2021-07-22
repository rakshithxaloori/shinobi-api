from django.db import models
from django.utils import timezone

from profiles.models import Profile


class Notification(models.Model):
    FOLLOW = "f"

    NOTIFICATION_CHOICES = [(FOLLOW, "follow")]

    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=1,
        choices=NOTIFICATION_CHOICES,
        default=FOLLOW,
        blank=False,
        null=False,
    )
    sent_at = models.DateTimeField(default=timezone.now)
