from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed

from authentication.models import User
from profiles.models import Profile, Following
from profiles import tasks as p_tasks
from chat import tasks as c_tasks
from notification import tasks as n_tasks
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
            c_tasks.create_chat.delay(being_followed_user, follower_user)

            # Increase the trend count
            p_tasks.after_follow.delay(being_followed_user.profile)

            # Send a notification
            n_tasks.create_notification.delay(
                Notification.FOLLOW, follower_user, being_followed_user
            )

        elif action == "post_remove":
            # Delete chat
            c_tasks.delete_chat.delay(being_followed_user, follower_user)

            # Decrease trend count
            p_tasks.after_unfollow.delay(being_followed_user.profile)

    except Exception as e:
        print(e)
