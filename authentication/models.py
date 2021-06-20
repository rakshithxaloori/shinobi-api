from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    is_banned = models.BooleanField(default=False)
    picture = models.URLField(null=True, blank=True)

    def __str__(self):
        return "{} || {}".format(self.username, self.email)

    class Meta:
        ordering = ["username"]
