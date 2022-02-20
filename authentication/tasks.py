from django.utils import timezone

from shinobi.celery import app as celery_app

from authentication.models import User
from analytics.tasks import update_active_user_task
from shinobi.utils import get_country_code


@celery_app.task(queue="celery")
def user_online(user_pk, ip):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return
    update_active_user_task.delay(user.last_open.date().isoformat())

    user.last_open = timezone.now()
    user.online = True
    c_code = get_country_code(ip)
    if c_code != "":
        user.country_code = c_code
        user.save(update_fields=["last_open", "online", "country_code"])
    else:
        user.save(update_fields=["last_open", "online"])


@celery_app.task(queue="celery")
def user_offline(user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return
    user.last_close = timezone.now()
    user.online = False
    user.save(update_fields=["last_close", "online"])
