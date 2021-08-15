trend_score = 1


def add_profile_picture(user, picture):
    """Add the picture to user if a picture doesn't exist."""
    if user.picture is None or user.picture == "":
        user.picture = picture
        user.save()


def after_follow(user_profile):
    user_profile.trend_score += trend_score
    user_profile.save(update_fields=["trend_score"])


def after_unfollow(user_profile):
    user_profile.trend_score -= trend_score
    user_profile.save(update_fields=["trend_score"])
