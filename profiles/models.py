from random import choice

from django.db import models

from authentication.models import User


def random_bio():
    bios = [
        "May the Force be with you.",
        "Carpe diem. Seize the day, boys. Make your lives extraordinary.",
        "My mama always said life was like a box of chocolates. You never know what you're gonna get.",
        "Hasta la vista, baby.",
        "I am Groot.",
        "This is Sparta!",
        "Wilsoooooooon!",
        "Why so serious?",
        "Is this your king?",
        "I live my life a quarter mile at a time.",
        "How you doin'?",
        "It's gonna be legen — wait for it — dary.",
    ]

    return choice(bios)


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.PROTECT)
    following = models.ManyToManyField(User, related_name="follower", blank=True)
    bio = models.TextField(max_length=150, default=random_bio)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        ordering = ["-created"]


class TwitchProfile(models.Model):
    profile = models.OneToOneField(
        Profile, related_name="twitch_profile", on_delete=models.PROTECT
    )
    user_id = models.CharField(max_length=20, blank=False, null=False)
    login = models.CharField(max_length=25, blank=False, null=False)
    display_name = models.CharField(max_length=25, blank=False, null=False)
    profile_image_url = models.URLField(null=True, blank=True)
    view_count = models.PositiveBigIntegerField(default=0)
    access_token = models.CharField(max_length=100, null=False, blank=False)
    refresh_token = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return "{} || {}".format(self.login, self.profile.user.username)


class YouTubeProfile(models.Model):
    profile = models.OneToOneField(
        Profile, related_name="youtube_profile", on_delete=models.PROTECT
    )
    channel_id = models.CharField(max_length=24, blank=False, null=False)
    channel_image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return "{} || {}".format(self.channel_id, self.profile.user.username)
