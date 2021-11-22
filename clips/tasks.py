import celery
from django.core.files.storage import default_storage

from shinobi.celery import app as celery_app


from authentication.models import User
from shinobi.utils import get_media_file_url, get_media_file_path
from clips.models import Clip


@celery_app.task(queue="celery")
def check_upload_after_delay(clip_pk):
    try:
        clip = Clip.objects.get(pk=clip_pk)
    except Clip.DoesNotExist:
        return
    if not clip.upload_verified:
        file_path = get_media_file_path(clip.url)
        if default_storage.exists(file_path):
            if default_storage.size(file_path) > 50 * 1000 * 1000:
                # Greater than 50
                default_storage.delete(file_path)
                clip.delete()
            else:
                clip.upload_verified = True
                clip.save(update_fields=["upload_verified"])
        else:
            clip.delete()


@celery_app.task(queue="celery")
def check_upload_successful_task(file_path):
    # Check if the upload is successful in S3
    if file_path is None:
        return
    try:
        file_url = get_media_file_url(file_path)
        clip = Clip.objects.get(url=file_url)
    except Clip.DoesNotExist:
        return

    if default_storage.exists(file_path):
        if default_storage.size(file_path) > 50000010:
            # Greater than 50 MB
            default_storage.delete(file_path)
            clip.delete()
        else:
            clip.upload_verified = True
            clip.save(update_fields=["upload_verified"])


@celery_app.task(queue="celery")
def delete_clip_task(url):
    file_path = get_media_file_path(url)
    if default_storage.exists(file_path):
        default_storage.delete(file_path)
