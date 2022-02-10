from django.db import models

from socials.utils import CUSTOM_LINK_TITLE_LENGTH


def random_twitch_secret():
    return None


class Socials(models.Model):
    youtube = models.CharField(null=True, blank=True, max_length=24)
    instagram = models.CharField(null=True, blank=True, max_length=30)
    twitch = models.CharField(null=True, blank=True, max_length=15)
    custom_title = models.CharField(
        null=True, blank=True, max_length=CUSTOM_LINK_TITLE_LENGTH
    )
    custom_url = models.URLField(null=True, blank=True)

    def __str__(self) -> str:
        return_val = "{} ".format(self.profile.user.username)
        if self.youtube is not None and self.youtube != "":
            return_val += "| YT: {} ".format(self.youtube)
        if self.instagram is not None and self.instagram != "":
            return_val += "| IG: {} ".format(self.instagram)
        if self.twitch is not None and self.twitch != "":
            return_val += "| TW: {} ".format(self.twitch)
        if self.custom_url is not None and self.custom_url != "":
            return_val += "| {}: {}".format(self.custom_title, self.custom_url)

        return return_val
