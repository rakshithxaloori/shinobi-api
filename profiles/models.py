from django.db import models

from authentication.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.PROTECT)
    following = models.ManyToManyField(User, related_name="follower", blank=True)
    bio = models.TextField(max_length=260)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        ordering = ["-created"]
