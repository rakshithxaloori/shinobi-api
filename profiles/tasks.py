import os
import uuid
import pickle

from django.core.cache import cache
from django.conf import settings
from django.core.files.storage import default_storage

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


def get_picture_path(picture_url):
    if picture_url is None or picture_url is "":
        return None

    if settings.CI_CD_STAGE == "development":
        media_url = os.environ["BASE_URL"] + settings.MEDIA_URL
        return picture_url.split(media_url)[1]
    elif settings.CI_CD_STAGE == "testing" or settings.CI_CD_STAGE == "production":
        return picture_url.split(settings.MEDIA_URL)[1]


def get_picture_url(picture_path):
    if settings.CI_CD_STAGE == "development":
        return "{base_url}{path}".format(
            base_url=os.environ["BASE_URL"], path=default_storage.url(picture_path)
        )
    elif settings.CI_CD_STAGE == "testing" or settings.CI_CD_STAGE == "production":
        return default_storage.url(picture_path)


@celery_app.task(queue="celery")
def update_profile_picture(user_pk, picture_cache_key, picture_name, picture_type):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return

    picture_pickle = cache.get(picture_cache_key)
    if picture_pickle is None:
        return
    picture_obj = pickle.loads(picture_pickle)

    # organize a path for the file in bucket
    file_directory_within_bucket = "profile_pictures/{username}".format(
        username=user.username
    )

    # synthesize a full file path; note that we included the filename
    new_picture_path = os.path.join(
        file_directory_within_bucket,
        "{uuid}.{type}".format(uuid=uuid.uuid4(), type=picture_type.split("/")[1]),
    )

    # Delete previous file
    ex_picture_path = get_picture_path(user.picture)
    if (
        ex_picture_path is not None
        and ex_picture_path is not ""
        and default_storage.exists(ex_picture_path)
    ):
        default_storage.delete(ex_picture_path)
    default_storage.save(new_picture_path, picture_obj)

    new_picture_url = get_picture_url(new_picture_path)
    print("URL", new_picture_url)
    user.picture = new_picture_url
    user.save()
    cache.delete(picture_cache_key)
