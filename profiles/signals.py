from typing import Sequence
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed

from authentication.models import User
from profiles.models import Profile, Following
from profiles import utils as p_utils
from chat import utils as c_utils
from notification import utils as n_utils
from notification.models import Notification


@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(m2m_changed, sender=Following)
def post_change_follow_status(sender, instance, action, model, pk_set, **kwargs):
    try:
        print("M2M_CHANGED", sender)
        follower_user = instance.user
        being_followed_user = User.objects.get(pk__in=pk_set)
        if action == "post_add":
            # Create chat
            c_utils.create_chat(being_followed_user, follower_user)

            # Increase the trend count
            p_utils.after_follow(being_followed_user.profile)

            # Send a notification
            n_utils.create_notification(
                Notification.FOLLOW, follower_user, being_followed_user
            )

        elif action == "post_remove":
            # Delete chat
            c_utils.delete_chat(being_followed_user, follower_user)

            # Decrease trend count
            p_utils.after_unfollow(being_followed_user.profile)

    except Exception as e:
        print(e)
