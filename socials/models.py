from django.db import models
from django.utils.crypto import get_random_string

from profiles.models import Profile, Game


def random_twitch_secret():
    return get_random_string(length=10)


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
        TwitchProfile, related_name="twitch_stream", on_delete=models.CASCADE
    )
    game = models.ForeignKey(
        Game,
        related_name="twitch_streams",
        on_delete=models.PROTECT,
    )
    stream_id = models.CharField(max_length=100, blank=False, null=False)
    title = models.CharField(max_length=140, blank=True, null=True)
    thumbnail_url = models.URLField(null=True, blank=True)
    is_streaming = models.BooleanField(default=True)

    def __str__(self):
        return "t/{} || {} || {}".format(
            self.twitch_profile.login,
            self.game.name,
            "Streaming" if self.is_streaming else "NOT Streaming",
        )


class YouTubeProfile(models.Model):
    profile = models.OneToOneField(
        Profile, related_name="youtube_profile", on_delete=models.PROTECT
    )
    channel_id = models.CharField(max_length=24, blank=False, null=False)
    channel_image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return "{} || {}".format(self.channel_id, self.profile.user.username)
