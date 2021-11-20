from django.utils import timezone
from celery.schedules import crontab

from shinobi.celery import app as celery_app

from authentication.models import User
from analytics.models import DailyAnalytics


@celery_app.task(queue="celery")
def new_user_analytics():
    old_analytics = DailyAnalytics.objects.order_by("-date").first()
    old_analytics.active_users += 1
    old_analytics.new_users += 1
    old_analytics.save(update_fields=["active_users", "new_users"])


@celery_app.task(queue="celery")
def update_active_user(last_open_str):
    last_open_date = timezone.datetime.fromisoformat(last_open_str).date()

    # Daily Analytics
    da_instance = DailyAnalytics.objects.order_by("-date").first()
    if da_instance is None:
        # Happens when the db is first created
        da_instance = DailyAnalytics.objects.create(date=timezone.now())
        da_instance.save()

    elif last_open_date < da_instance.date:
        # If last opened before today
        da_instance.active_users += 1
        da_instance.save(update_fields=["active_users"])


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes everyday
    sender.add_periodic_task(
        crontab(minute=0, hour=0),
        daily_analytics.s(),
    )


@celery_app.task
def daily_analytics():
    """Creates a DailyAnalytics object."""
    old_analytics = DailyAnalytics.objects.order_by("-date").first()
    old_analytics.total_users = User.objects.count()
    old_analytics.save(update_fields=["total_users"])

    new_analytics = DailyAnalytics.objects.create(date=timezone.now())
    new_analytics.save()
