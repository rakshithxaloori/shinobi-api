from django.dispatch import receiver
from django.db.models.signals import m2m_changed

from authentication.models import User
from profiles.models import Following
from profiles import tasks as p_tasks
from chat import tasks as c_tasks
from notification import tasks as n_tasks
from notification.models import Notification


@receiver(m2m_changed, sender=Following)
def post_change_follow_status(sender, instance, action, model, pk_set, **kwargs):
    try:
        print("M2M_CHANGED", sender)
        follower_user_pk = instance.user.pk
        being_followed_user = User.objects.get(pk__in=pk_set)
        being_followed_user_pk = being_followed_user.pk
        if action == "post_add":
            # Create chat
            c_tasks.create_chat.delay(being_followed_user_pk, follower_user_pk)

            # Increase stuff
            p_tasks.after_follow.delay(being_followed_user.profile.pk)

            # Send a notification
            n_tasks.create_notification.delay(
                Notification.FOLLOW, follower_user_pk, being_followed_user_pk
            )

        elif action == "post_remove":
            # Delete chat
            c_tasks.delete_chat.delay(being_followed_user_pk, follower_user_pk)

            # Decrease stuff
            p_tasks.after_unfollow.delay(being_followed_user.profile.pk)

    except Exception as e:
        print(e)
