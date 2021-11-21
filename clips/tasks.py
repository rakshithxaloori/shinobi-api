from django.core.files.storage import default_storage

from shinobi.celery import app as celery_app


from authentication.models import User
from shinobi.utils import get_media_file_url
from clips.models import Clip, ClipToUpload


@celery_app.task(queue="celery")
def check_upload_successful_task(file_path, title):
    # Check if the upload is successful in S3
    if file_path is None:
        return
    if default_storage.exists(file_path):
        if default_storage.size(file_path) > 50000000:
            # Greater than 50 MB
            default_storage.delete(file_path)

        # Delete intermediate ClipToUpload
        file_url = get_media_file_url(file_path)
        try:
            clip_to_upload = ClipToUpload.objects.get(url=file_url)
            new_clip = Clip.objects.create(
                created_date=clip_to_upload.created_date,
                created_datetime=clip_to_upload.created_datetime,
                uploader=clip_to_upload.uploaded_by,
                game=clip_to_upload.game,
                title=title,
                url=clip_to_upload.url,
            )
            print("SAVING CLIP")
            print("DELETING CLIPTOSAVE")
            new_clip.save()
            clip_to_upload.delete()
        except ClipToUpload.DoesNotExist:
            default_storage.delete(file_path)


@celery_app.task(queue="celery")
def check_upload_failed_task(file_path):
    # Invalidate the presigned url
    # Check if the upload exists and if so delete
    # Delete ClipToUpload
    pass
