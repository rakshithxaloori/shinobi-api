from shinobi.celery import app as celery_app

from authentication.models import User
from profiles.models import Profile


@celery_app.task(queue="celery")
def add_profile_picture(user_pk, picture):
    """Add the picture to user if a picture doesn't exist."""
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return
    if user.picture is None or user.picture == "":
        user.picture = picture
        user.save()


@celery_app.task(queue="celery")
def after_follow(user_profile_pk):
    try:
        user_profile = Profile.objects.get(pk=user_profile_pk)
    except Profile.DoesNotExist:
        return
    user_profile.follower_count = user_profile.user.follower.count()
    user_profile.save(update_fields=["follower_count"])


@celery_app.task(queue="celery")
def after_unfollow(user_profile_pk):
    try:
        user_profile = Profile.objects.get(pk=user_profile_pk)
    except Profile.DoesNotExist:
        return
    user_profile.follower_count = user_profile.user.follower.count()
    user_profile.save(update_fields=["follower_count"])
