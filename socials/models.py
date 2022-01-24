from django.db import models


def random_twitch_secret():
    return None


class Socials(models.Model):
    youtube = models.CharField(null=True, blank=True, max_length=24)
    instagram = models.CharField(null=True, blank=True, max_length=30)
    twitch = models.CharField(null=True, blank=True, max_length=15)

    def __str__(self) -> str:
        return "{} || YT: {} || IG: {} || TW: {}".format(
            self.profile.user.username, self.youtube, self.instagram, self.twitch
        )
