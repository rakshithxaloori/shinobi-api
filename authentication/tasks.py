from celery.app import shared_task
from celery import shared_task

from django.utils import timezone

from authentication.models import User
from analytics.tasks import update_active_user


@shared_task
def user_online(user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return
    update_active_user.delay(user.last_open.date().isoformat())
    # update_active_user(user.last_open.date().isoformat())
    user.last_open = timezone.now()
    user.online = True
    user.save(update_fields=["last_open", "online"])


@shared_task
def user_offline(user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return
    user.last_close = timezone.now()
    user.online = False
    user.save(update_fields=["last_close", "online"])
