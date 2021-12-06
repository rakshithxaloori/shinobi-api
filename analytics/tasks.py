from django.utils import timezone
from celery.schedules import crontab

from shinobi.celery import app as celery_app

from authentication.models import User
from clips.models import Clip, View
from analytics.models import DailyAnalytics
from shinobi.utils import now_date


def get_analytics_instance():
    try:
        analytics = DailyAnalytics.objects.get(date=now_date())

    except DailyAnalytics.DoesNotExist:
        # Update old analytics instance
        old_analytics = DailyAnalytics.objects.order_by("-date").first()
        old_analytics.total_users = User.objects.all().count()
        old_analytics.total_clips = Clip.objects.filter(
            created_date=old_analytics.date
        ).count()
        old_analytics.total_views = View.objects.filter(
            created_date=old_analytics.date
        ).count()
        old_analytics.save(update_fields=["total_users", "total_clips", "total_views"])

        # Create new analytics instance
        analytics = DailyAnalytics.objects.create()
        analytics.save()

    return analytics


@celery_app.task(queue="celery")
def new_user_joined():
    analytics = get_analytics_instance()
    analytics.active_users += 1
    analytics.new_users += 1
    analytics.save(update_fields=["active_users", "new_users"])


@celery_app.task(queue="celery")
def update_active_user(last_open_str):
    last_open_date = timezone.datetime.fromisoformat(last_open_str).date()

    # Daily Analytics
    da_instance = get_analytics_instance()
    if da_instance is None:
        # Happens when the db is first created
        da_instance = DailyAnalytics.objects.create(date=timezone.now())
        da_instance.save()

    elif last_open_date < da_instance.date:
        # If last opened before today
        da_instance.active_users += 1
        da_instance.save(update_fields=["active_users"])
