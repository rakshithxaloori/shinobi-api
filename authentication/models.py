from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


def today_date():
    return timezone.now().date()


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
    last_action_date = models.DateField(default=today_date)
    action_count = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        days_diff = (timezone.now() - self.last_open).days
        return "{} || {} || {} days ago".format(self.username, self.email, days_diff)

    class Meta:
        ordering = ["username"]
