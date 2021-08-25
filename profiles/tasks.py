from celery import shared_task

trend_score = 1


@shared_task
def add_profile_picture(user, picture):
    """Add the picture to user if a picture doesn't exist."""
    if user.picture is None or user.picture == "":
        user.picture = picture
        user.save()


@shared_task
def after_follow(user_profile):
    user_profile.trend_score += trend_score
    user_profile.save(update_fields=["trend_score"])


@shared_task
def after_unfollow(user_profile):
    user_profile.trend_score -= trend_score
    user_profile.save(update_fields=["trend_score"])
