import os
import uuid
import pickle

from django.core.cache import cache
from django.conf import settings
from django.core.files.storage import default_storage

from shinobi.celery import app as celery_app


from authentication.models import User
from shinobi.utils import get_media_file_url


@celery_app.task(queue="celery")
def upload_clip(user_pk, clip_cache_key, game_pk, clip_type):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return

    clip_pickle = cache.get(clip_cache_key)
    if clip_pickle is None:
        return

    clip_obj = pickle.loads(clip_pickle)

    # organize a path for the file in bucket
    file_directory_within_bucket = "clips/{username}".format(username=user.username)

    # synthesize a full file path; note that we included the filename
    new_clip_path = os.path.join(
        file_directory_within_bucket,
        "{uuid}.{type}".format(uuid=uuid.uuid4(), type=clip_type.split("/")[1]),
    )

    try:
        user.is_uploading_clip = True
        user.save(update_fields=["is_uploading_clip"])
        default_storage.save(new_clip_path, clip_obj)

        new_clip_url = get_media_file_url(new_clip_path)
        print("CLIP URL", new_clip_path)
    except Exception:
        pass
    finally:
        user.is_uploading_clip = False
        user.save(update_fields=["is_uploading_clip"])
