from django.utils import timezone
from league_of_legends.utils import get_lol_profile

from shinobi.celery import app as celery_app

from authentication.models import User
from analytics.tasks import update_active_user
from league_of_legends.tasks import check_new_matches


@celery_app.task(queue="celery")
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

    # UPDATE MATCH HISTORY
    lol_profile = get_lol_profile(user.username)
    if lol_profile is not None:
        check_new_matches.delay(lol_profile.pk)


@celery_app.task(queue="celery")
def user_offline(user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return
    user.last_close = timezone.now()
    user.online = False
    user.save(update_fields=["last_close", "online"])
