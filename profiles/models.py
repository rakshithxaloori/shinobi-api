from random import choice

from django.db import models
from django.utils.crypto import get_random_string

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


def random_twitch_secret():
    return get_random_string(length=10)


# Create your models here.
class Game(models.Model):
    # {
    #     "id": "21779",
    #     "name": "League of Legends",
    #     "box_art_url": "https://static-cdn.jtvnw.net/ttv-boxart/League%20of%20Legends-{width}x{height}.jpg",
    # }
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    logo_url = models.URLField()

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.PROTECT)
    followings = models.ManyToManyField(
        User, related_name="follower", blank=True, through="Following"
    )
    bio = models.TextField(max_length=150, default=random_bio)
    trend_score = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        ordering = ["-created"]


class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "{} follows {}".format(self.profile.user.username, self.user.username)


class TwitchProfile(models.Model):
    profile = models.OneToOneField(
        Profile, related_name="twitch_profile", on_delete=models.PROTECT
    )
    user_id = models.CharField(max_length=20, blank=False, null=False)
    login = models.CharField(max_length=25, blank=False, null=False)
    display_name = models.CharField(max_length=25, blank=False, null=False)
    view_count = models.PositiveBigIntegerField(default=0)
    secret = models.CharField(max_length=10, default=random_twitch_secret)
    stream_online_subscription_id = models.CharField(
        max_length=100, blank=True, null=True
    )
    stream_offline_subscription_id = models.CharField(
        max_length=100, blank=True, null=True
    )

    def __str__(self):
        return "t/{} || {}".format(self.login, self.profile.user.username)


class TwitchStream(models.Model):
    twitch_profile = models.OneToOneField(
        TwitchProfile, related_name="twitch_stream", on_delete=models.PROTECT
    )
    game = models.ForeignKey(
        Game,
        related_name="twitch_streams",
        on_delete=models.PROTECT,
    )
    stream_id = models.CharField(max_length=100, blank=False, null=False)
    title = models.CharField(max_length=140, blank=False, null=False)
    thumbnail_url = models.URLField(null=True, blank=True)
    is_streaming = models.BooleanField(default=True)

    def __str__(self):
        return "t/{} || {}".format(self.twitch_profile.login, self.stream_id)


class YouTubeProfile(models.Model):
    profile = models.OneToOneField(
        Profile, related_name="youtube_profile", on_delete=models.PROTECT
    )
    channel_id = models.CharField(max_length=24, blank=False, null=False)
    channel_image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return "{} || {}".format(self.channel_id, self.profile.user.username)
