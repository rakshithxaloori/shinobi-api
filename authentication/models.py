from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    is_banned = models.BooleanField(default=False)
    picture = models.URLField(null=True, blank=True)
    last_open = models.DateTimeField(
        default=timezone.now
    )  # The last time the user opened the app
    last_close = models.DateTimeField(
        default=timezone.now
    )  # The last time the user closed the app
    online = models.BooleanField(default=False)

    def __str__(self):
        return "{} || {}".format(self.username, self.email)

    class Meta:
        ordering = ["username"]
