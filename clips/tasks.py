from django.conf import settings
from django.core.files.storage import default_storage

from shinobi.celery import app as celery_app


from clips.utils import VIDEO_MAX_SIZE_IN_BYTES
from shinobi.utils import get_media_file_url, get_media_file_path
from clips.models import Clip


def delete_upload_file(file_path):
    # Verify that it's uploads/
    if default_storage.exists(file_path):
        default_storage.delete(file_path)


@celery_app.task(queue="celery")
def check_upload_after_delay(clip_pk):
    try:
        clip = Clip.objects.get(pk=clip_pk)
    except Clip.DoesNotExist:
        return
    if not clip.upload_verified:
        file_path = get_media_file_path(clip.url)
        bucket_url = "s3://{bucket_name}/".format(
            bucket_name=settings.AWS_STORAGE_BUCKET_NAME
        )
        input_s3_url = bucket_url + file_path

        check_compressed_successful_task(input_s3_url)


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
        if default_storage.size(file_path) > VIDEO_MAX_SIZE_IN_BYTES:
            delete_upload_file(file_path)
            clip.delete()
        else:
            clip.upload_verified = True
            clip.save(update_fields=["upload_verified"])


@celery_app.task(queue="celery")
def check_compressed_successful_task(input_s3_url: str):
    # s3://plx-dev-static/clips/uploads/20secs.mov
    if input_s3_url is None:
        return
    bucket_url = "s3://{bucket_name}/".format(
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME
    )
    upload_file_key = input_s3_url.split(bucket_url)[1]

    upload_filename = input_s3_url.split(settings.S3_FILE_UPLOAD_PATH_PREFIX + "/")[
        1
    ].split(".")[0]

    compressed_file_key = "{compressed_prefix}/{filename}_720p_8.mp4".format(
        compressed_prefix=settings.S3_FILE_COMPRESSED_PATH_PREFIX,
        filename=upload_filename,
    )

    if default_storage.exists(compressed_file_key):
        # Delete the uploaded file
        delete_upload_file(upload_file_key)

        try:
            compressed_file_key = "{}/{}_{}_{}.mp4".format(
                settings.S3_FILE_COMPRESSED_PATH_PREFIX, upload_filename, "{}p", "{}"
            )
            file_cdn_url = get_media_file_url(compressed_file_key)
            # Replace hex symbols
            file_cdn_url = file_cdn_url.replace("%7B", "{")
            file_cdn_url = file_cdn_url.replace("%7D", "}")

            clip = Clip.objects.get(url=get_media_file_url(upload_file_key))
            clip.compressed_verified = True
            clip.url = file_cdn_url
            clip.save(update_fields=["compressed_verified", "url"])
        except Clip.DoesNotExist:
            print("Clip.DoesNotExist", upload_file_key, compressed_file_key)
            fileargs = [(720, 8), (720, 7), (480, 7), (360, 7)]
            for filearg in fileargs:
                vid_file_key = compressed_file_key.format(filearg[0], filearg[1])
                if default_storage.exists(vid_file_key):
                    default_storage.delete(vid_file_key)


@celery_app.task(queue="celery")
def delete_clip_task(url):
    file_path = get_media_file_path(url)
    if default_storage.exists(file_path):
        # Upload
        delete_upload_file(file_path)
    # Upload and compressed
    fileargs = [(720, 8), (720, 7), (480, 7), (360, 7)]
    for filearg in fileargs:
        vid_file_key = file_path.format(filearg[0], filearg[1])
        if default_storage.exists(vid_file_key):
            default_storage.delete(vid_file_key)
