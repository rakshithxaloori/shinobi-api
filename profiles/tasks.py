import os
import uuid
import pickle

from django.core.cache import cache
from django.core.files.storage import default_storage

from shinobi.celery import app as celery_app

from authentication.models import User
from profiles.models import Profile
from shinobi.utils import get_media_file_url


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
    for picture in default_storage.listdir(file_directory_within_bucket)[1]:
        default_storage.delete(os.path.join(file_directory_within_bucket, picture))

    default_storage.save(new_picture_path, picture_obj)

    new_picture_url = get_media_file_url(new_picture_path)
    user.picture = new_picture_url
    user.save()
    cache.delete(picture_cache_key)
