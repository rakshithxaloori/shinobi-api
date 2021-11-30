from django.conf import settings
from django.core.files.storage import default_storage

from shinobi.celery import app as celery_app


from clips.utils import s3_client
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
            if default_storage.size(file_path) > 100 * 1000 * 1000:
                # Greater than 100 MB
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
        if default_storage.size(file_path) > 100 * 1000 * 1000:
            # Greater than 100 MB
            default_storage.delete(file_path)
            clip.delete()
        else:
            clip.upload_verified = True
            clip.save(update_fields=["upload_verified"])


@celery_app.task(queue="celery")
def check_compressed_successful_task(file_s3_url: str):
    # s3://plx-dev-static/clips/uploads/test.mp4
    if file_s3_url is None:
        return
    upload_file_key = file_s3_url.split(
        "s3://{bucket_name}/".format(bucket_name=settings.AWS_STORAGE_BUCKET_NAME)
    )[1]
    upload_filename = file_s3_url.split(settings.S3_FILE_UPLOAD_PATH_PREFIX + "/")[1]
    upload_filename = upload_filename.split(".mp4")[0] + "-compressed.mp4"
    compressed_file_key = "{compressed_prefix}/{filename}".format(
        compressed_prefix=settings.S3_FILE_COMPRESSED_PATH_PREFIX,
        filename=upload_filename,
    )

    print(
        "{upload_file_key}$$".format(upload_file_key=upload_file_key),
        default_storage.exists(upload_file_key),
    )

    if default_storage.exists(compressed_file_key):
        # Check if size is smaller
        if default_storage.size(upload_file_key) < default_storage.size(
            compressed_file_key
        ):
            # Mv uploaded file
            copy_source = {
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": upload_file_key,
            }
            s3_client.copy(
                copy_source, settings.AWS_STORAGE_BUCKET_NAME, compressed_file_key
            )

            # Delete the uploaded file
            default_storage.delete(upload_file_key)

        try:
            file_cdn_url = get_media_file_url(compressed_file_key)
            clip = Clip.objects.get(url=get_media_file_url(upload_file_key))
            clip.compressed_verified = True
            clip.url = file_cdn_url
            clip.save(update_fields=["compressed_verified", "url"])
        except Clip.DoesNotExist:
            print("Clip.DoesNotExist", upload_file_key)
            if default_storage.exists(compressed_file_key):
                default_storage.delete(compressed_file_key)


@celery_app.task(queue="celery")
def delete_clip_task(url):
    file_path = get_media_file_path(url)
    if default_storage.exists(file_path):
        default_storage.delete(file_path)
