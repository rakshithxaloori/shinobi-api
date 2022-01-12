from django.db import models
from django.utils import timezone

from authentication.models import User

# TODO notif preferences
# fields - new follower (True/False)


class Notification(models.Model):
    FOLLOW = "f"
    CLIP = "c"
    LIKE = "l"
    REPOST = "rp"

    NOTIFICATION_CHOICES = [
        (FOLLOW, "follow"),
        (CLIP, "clip"),
        (LIKE, "like"),
        (REPOST, "repost"),
    ]

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # Never access notifications with sender
    receiver = models.ForeignKey(
        User, related_name="notifications", on_delete=models.PROTECT
    )
    type = models.CharField(max_length=2, choices=NOTIFICATION_CHOICES)
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} | {} | {} | {}".format(
            self.type, self.sender.username, self.receiver.username, self.sent_at
        )


class ExponentPushToken(models.Model):
    # Is this token unique per device?
    #     Yes. No two devices should have the same Expo push token.
    # If the user uninstall and re-installs the app does the token change?
    #     Yes, the Expo push token will change if the app is re-installed. The native device token may or may not change (totally up to the OS).
    # What if the user resets the device?
    #     Yes, the Expo push token will change if the device is reset. But if it's restored from a backup, the Expo push token should be restored.

    user = models.ForeignKey(
        User, related_name="exponent_push_tokens", on_delete=models.PROTECT
    )
    token = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{}".format(self.user.username)
