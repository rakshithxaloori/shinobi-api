from django.db import models

from profiles.models import Profile


class PrivacySettings(models.Model):
    profile = models.OneToOneField(
        Profile, related_name="privacy_settings", on_delete=models.PROTECT
    )
    show_flag = models.BooleanField(default=True)

    def __str__(self) -> str:
        return "{}".format(self.profile.user.username)
