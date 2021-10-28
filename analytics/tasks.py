from datetime import date
from celery.schedules import crontab

from shinobi.celery import app as celery_app

from authentication.models import User
from analytics.models import DailyAnalytics, WeeklyAnalytics, MonthlyAnalytics


@celery_app.task(queue="celery")
def new_user_analytics():
    old_analytics = DailyAnalytics.objects.order_by("-date").first()
    old_analytics.active_users += 1
    old_analytics.new_users += 1
    old_analytics.save(update_fields=["active_users", "new_users"])

    old_analytics = WeeklyAnalytics.objects.order_by("-date").first()
    old_analytics.active_users += 1
    old_analytics.new_users += 1
    old_analytics.save(update_fields=["active_users", "new_users"])

    old_analytics = MonthlyAnalytics.objects.order_by("-date").first()
    old_analytics.active_users += 1
    old_analytics.new_users += 1
    old_analytics.save(update_fields=["active_users", "new_users"])


@celery_app.task(queue="celery")
def update_active_user(last_open_str):
    last_open_date = date.fromisoformat(last_open_str)

    # Daily Analytics
    da_instance = DailyAnalytics.objects.order_by("-date").first()
    if da_instance is None:
        # Happens when the db is first created
        da_instance = DailyAnalytics.objects.create(date=date.today())
        da_instance.save()

    elif last_open_date < da_instance.date:
        # If last opened before today
        da_instance.active_users += 1
        da_instance.save(update_fields=["active_users"])

    # Weekly Analytics
    wa_instance = WeeklyAnalytics.objects.order_by("-date").first()
    if wa_instance is None:
        wa_instance = WeeklyAnalytics.objects.create(date=date.today())
        wa_instance.save()

    elif last_open_date < wa_instance.date:
        # if not (last.open >= wa_instance.date)
        # If last not today or later this week
        wa_instance.active_users += 1
        wa_instance.save(update_fields=["active_users"])

    # Monthly Analytics
    ma_instance = MonthlyAnalytics.objects.order_by("-date").first()
    if ma_instance is None:
        ma_instance = MonthlyAnalytics.objects.create(date=date.today())
        ma_instance.save()

    elif last_open_date < ma_instance.date:
        # if not (last.open >= ma_instance.date)
        # If last not today or later this month
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
    old_analytics = DailyAnalytics.objects.order_by("-date").first()
    old_analytics.total_users = User.objects.count()
    old_analytics.save(update_fields=["total_users"])

    new_analytics = DailyAnalytics.objects.create(date=date.today())
    new_analytics.save()


@celery_app.task
def weekly_analytics():
    """Creates a WeeklyAnalytics object."""
    old_analytics = WeeklyAnalytics.objects.order_by("-date").first()
    old_analytics.total_users = User.objects.count()
    old_analytics.save(update_fields=["total_users"])

    new_analytics = WeeklyAnalytics.objects.create(date=date.today())
    new_analytics.save()


@celery_app.task
def monthly_analytics():
    """Creates a MonthlyAnalytics object."""
    old_analytics = MonthlyAnalytics.objects.order_by("-date").first()
    old_analytics.total_users = User.objects.count()
    old_analytics.save(update_fields=["total_users"])

    new_analytics = MonthlyAnalytics.objects.create(date=date.today())
    new_analytics.save()
