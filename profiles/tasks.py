from celery import shared_task

from authentication.models import User
from profiles.models import Profile

trend_score = 1


@shared_task
def add_profile_picture(user_pk, picture):
    """Add the picture to user if a picture doesn't exist."""
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return
    if user.picture is None or user.picture == "":
        user.picture = picture
        user.save()


@shared_task
def after_follow(user_profile_pk):
    try:
        user_profile = Profile.objects.get(pk=user_profile_pk)
    except Profile.DoesNotExist:
        return
    user_profile.trend_score += trend_score
    user_profile.save(update_fields=["trend_score"])


@shared_task
def after_unfollow(user_profile_pk):
    try:
        user_profile = Profile.objects.get(pk=user_profile_pk)
    except Profile.DoesNotExist:
        return
    user_profile.trend_score -= trend_score
    user_profile.save(update_fields=["trend_score"])
