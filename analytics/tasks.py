from django.utils import timezone
from celery.schedules import crontab

from shinobi.celery import app as celery_app

from authentication.models import User
from clips.models import Clip, View
from analytics.models import DailyAnalytics
from shinobi.utils import now_date


def get_da_instance():
    try:
        analytics = DailyAnalytics.objects.get(date=now_date())

    except DailyAnalytics.DoesNotExist:
        analytics = DailyAnalytics.objects.get(pk=create_new_da())

    return analytics


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=0, hour=0), create_new_da.s(), name="create daily analytics"
    )


@celery_app.task(queue="celery")
def create_new_da():
    # Update old analytics instance
    old_analytics = DailyAnalytics.objects.order_by("-date").first()
    old_analytics.total_users = User.objects.filter(is_staff=False).count()
    old_analytics.total_clips_m = Clip.objects.filter(
        created_date=old_analytics.date, uploaded_from=Clip.MOBILE
    ).count()
    old_analytics.total_clips_w = Clip.objects.filter(
        created_date=old_analytics.date, uploaded_from=Clip.WEB
    ).count()
    old_analytics.save(
        update_fields=[
            "total_users",
            "total_clips_m",
            "total_clips_w",
        ]
    )

    # Create new analytics instance
    analytics = DailyAnalytics.objects.create()
    analytics.save()
    return analytics.pk


@celery_app.task(queue="celery")
def new_user_joined():
    analytics = get_da_instance()
    analytics.active_users += 1
    analytics.new_users += 1
    analytics.save(update_fields=["active_users", "new_users"])


@celery_app.task(queue="celery")
def update_active_user(last_open_str):
    last_open_date = timezone.datetime.fromisoformat(last_open_str).date()

    # Daily Analytics
    da_instance = get_da_instance()
    if da_instance is None:
        # Happens when the db is first created
        da_instance = DailyAnalytics.objects.create(date=timezone.now())
        da_instance.save()

    elif last_open_date < da_instance.date:
        # If last opened before today
        da_instance.active_users += 1
        da_instance.save(update_fields=["active_users"])


@celery_app.task(queue="celery")
def add_view_analytics_task():
    analytics = get_da_instance()
    analytics.total_views += 1
    analytics.save()
