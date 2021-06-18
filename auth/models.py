from django.db import models
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.
class User(AbstractBaseUser):
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return "{} || {}".format(self.username, self.email)
