from datetime import date
from celery import shared_task
from celery.schedules import crontab

from proeliumx.celery import app as celery_app

from analytics.models import DailyAnalytics, WeeklyAnalytics, MonthlyAnalytics


@shared_task
def update_active_user(last_open_str):
    last_open_date = date.fromisoformat(last_open_str)
    da_instance = DailyAnalytics.objects.order_by("-date").first()

    if last_open_date < da_instance.date:
        # If last opened before today
        da_instance.active_users += 1
        da_instance.save(update_fields=["active_users"])

    wa_instance = WeeklyAnalytics.objects.order_by("-date").first()
    if (
        last_open_date < wa_instance.date
    ):  # if not (last.open >= wa_instance.date) # If last not today or later this week
        wa_instance.active_users += 1
        wa_instance.save(update_fields=["active_users"])

    ma_instance = MonthlyAnalytics.objects.order_by("-date").first()
    if (
        last_open_date < ma_instance.date
    ):  # if not (last.open >= ma_instance.date) # If last not today or later this month
        # If last opened before this month
        ma_instance.active_users += 1
        ma_instance.save(update_fields=["active_users"])


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes everyday
    sender.add_periodic_task(
        crontab(minute=0, hour=0),
        daily_analytics.s(),
    )

    # Executes on the first of every month
    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_week="1"),
        weekly_analytics.s(),
    )

    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_month="1"),
        monthly_analytics.s(),
    )


@celery_app.task
def daily_analytics():
    """Creates a DailyAnalytics object."""
    # TODO update old_analytics.total with Users.objects.all().count()
    new_analytics = DailyAnalytics.objects.create(date=date.today())
    new_analytics.save()


@celery_app.task
def weekly_analytics():
    """Creates a WeeklyAnalytics object."""
    # TODO update old_analytics.total with Users.objects.all().count()
    new_analytics = WeeklyAnalytics.objects.create(date=date.today())
    new_analytics.save()


@celery_app.task
def monthly_analytics():
    """Creates a MonthlyAnalytics object."""
    # TODO update old_analytics.total with Users.objects.all().count()
    new_analytics = MonthlyAnalytics.objects.create(date=date.today())
    new_analytics.save()
