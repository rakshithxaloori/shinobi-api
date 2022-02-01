from django.utils import timezone
from celery.schedules import crontab

from shinobi.celery import app as celery_app

from authentication.models import User
from clips.models import Clip
from analytics.models import DailyAnalytics, MonthlyAnalytics, WeeklyAnalytics
from shinobi.utils import now_date


def get_da_instance():
    try:
        analytics = DailyAnalytics.objects.order_by("-date").first()

    except (AttributeError, DailyAnalytics.DoesNotExist):
        pk = create_new_da()
        analytics = DailyAnalytics.objects.get(pk=pk)

    return analytics


def get_wa_instance():
    try:
        analytics = WeeklyAnalytics.objects.order_by("-date").first()

    except (AttributeError, WeeklyAnalytics.DoesNotExist):
        pk = create_new_wa()
        analytics = WeeklyAnalytics.objects.get(pk=pk)

    return analytics


def get_ma_instance():
    try:
        analytics = MonthlyAnalytics.objects.order_by("-date").first()

    except (AttributeError, MonthlyAnalytics.DoesNotExist):
        pk = create_new_ma()
        analytics = MonthlyAnalytics.objects.get(pk=pk)

    return analytics


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=0, hour=0), create_new_da.s(), name="create daily analytics"
    )

    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_week="mon"),
        create_new_wa.s(),
        name="create weekly analytics",
    )

    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_week="mon"),
        check_new_ma.s(),
        name="create monthly analytics",
    )


@celery_app.task(queue="celery")
def update_active_user_task(last_open_str):
    last_open_date = timezone.datetime.fromisoformat(last_open_str).date()

    ## Daily Analytics
    da_instance = get_da_instance()
    if last_open_date < da_instance.date:
        # If last opened before today
        da_instance.active_users += 1
        da_instance.save(update_fields=["active_users"])

    ## Weekly Analytics
    wa_instance = get_wa_instance()
    if last_open_date < wa_instance.date:
        # If last opened before this week
        wa_instance.active_users += 1
        wa_instance.save(update_fields=["active_users"])

    ## Monthly Analytics
    ma_instance = get_ma_instance()
    if last_open_date < ma_instance.date:
        # If last opened before this month
        ma_instance.active_users += 1
        ma_instance.save(update_fields=["active_users"])


@celery_app.task(queue="celery")
def new_user_joined_task():
    da = get_da_instance()
    da.active_users += 1
    da.new_users += 1
    da.save(update_fields=["active_users", "new_users"])

    wa = get_wa_instance()
    wa.active_users += 1
    wa.new_users += 1
    wa.save(update_fields=["active_users", "new_users"])

    ma = get_ma_instance()
    ma.active_users += 1
    ma.new_users += 1
    ma.save(update_fields=["active_users", "new_users"])


@celery_app.task(queue="celery")
def add_view_analytics_task():
    da = get_da_instance()
    da.total_views += 1
    da.save(update_fields=["total_views"])

    wa = get_wa_instance()
    wa.total_views += 1
    wa.save(update_fields=["total_views"])

    ma = get_ma_instance()
    ma.total_views += 1
    ma.save(update_fields=["total_views"])


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
def create_new_wa():
    old_analytics = WeeklyAnalytics.objects.order_by("-date").first()
    old_analytics.total_users = User.objects.filter(is_staff=False).count()
    old_analytics.total_clips_m = Clip.objects.filter(
        created_date__gte=old_analytics.date, uploaded_from=Clip.MOBILE
    ).count()
    old_analytics.total_clips_w = Clip.objects.filter(
        created_date__gte=old_analytics.date, uploaded_from=Clip.WEB
    ).count()
    old_analytics.save(
        update_fields=[
            "total_users",
            "total_clips_m",
            "total_clips_w",
        ]
    )

    # Create new analytics instance
    analytics = WeeklyAnalytics.objects.create()
    analytics.save()
    return analytics.pk


@celery_app.task(queue="celery")
def check_new_ma():
    old_analytics = MonthlyAnalytics.objects.order_by("-date").first()
    if (now_date() - old_analytics.date).days >= 4 * 7:
        create_new_ma()


@celery_app.task(queue="celery")
def create_new_ma():
    old_analytics = MonthlyAnalytics.objects.order_by("-date").first()
    old_analytics.total_users = User.objects.filter(is_staff=False).count()
    old_analytics.total_clips_m = Clip.objects.filter(
        created_date__gte=old_analytics.date, uploaded_from=Clip.MOBILE
    ).count()
    old_analytics.total_clips_w = Clip.objects.filter(
        created_date__gte=old_analytics.date, uploaded_from=Clip.WEB
    ).count()
    old_analytics.save(
        update_fields=[
            "total_users",
            "total_clips_m",
            "total_clips_w",
        ]
    )

    # Create new analytics instance
    analytics = MonthlyAnalytics.objects.create()
    analytics.save()
    return analytics.pk
