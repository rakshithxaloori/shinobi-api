from django.conf import settings
from django.core.files.storage import default_storage

from shinobi.celery import app as celery_app


from clips.utils import VIDEO_MAX_SIZE_IN_BYTES, VIDEO_FILE_ARGS, create_job
from shinobi.utils import get_media_file_url, get_media_file_path
from clips.models import Clip
from feed.models import Post
from notification.tasks import create_inotif_task
from authentication.models import User
from profiles.models import Following
from notification.models import Notification


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
        if default_storage.exists(file_path):
            if default_storage.size(file_path) > VIDEO_MAX_SIZE_IN_BYTES:
                delete_upload_file(file_path)
                clip.delete()
            else:
                clip.upload_verified = True
                clip.save(update_fields=["upload_verified"])
                create_job(
                    file_path=file_path,
                    height=clip.height,
                    width=clip.width,
                )
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
        if default_storage.size(file_path) > VIDEO_MAX_SIZE_IN_BYTES:
            delete_upload_file(file_path)
            clip.delete()
        else:
            clip.upload_verified = True
            clip.save(update_fields=["upload_verified"])
            create_job(
                file_path=file_path,
                height=clip.height,
                width=clip.width,
            )


@celery_app.task(queue="celery")
def check_compressed_successful_task(input_s3_url, jobID, durationInMs, videoDetails):
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

    compressed_file_key = "{compressed_prefix}/{filename}_4.mp4".format(
        compressed_prefix=settings.S3_FILE_COMPRESSED_PATH_PREFIX,
        filename=upload_filename,
    )

    if default_storage.exists(compressed_file_key):
        # Delete the uploaded file
        delete_upload_file(upload_file_key)

        try:
            compressed_file_key = "{}/{}_{}.mp4".format(
                settings.S3_FILE_COMPRESSED_PATH_PREFIX, upload_filename, "{}"
            )
            file_cdn_url = get_media_file_url(compressed_file_key)
            # Replace hex symbols
            file_cdn_url = file_cdn_url.replace("%7B", "{")
            file_cdn_url = file_cdn_url.replace("%7D", "}")

            clip = Clip.objects.get(url=get_media_file_url(upload_file_key))

            clip.compressed_verified = True
            clip.url = file_cdn_url
            clip.duration = durationInMs / 1000
            clip.job_id = jobID
            if clip.height == 0 or clip.width == 0:
                clip.width = videoDetails["widthInPx"]
                clip.height = videoDetails["heightInPx"]
                clip.save(
                    update_fields=[
                        "compressed_verified",
                        "url",
                        "duration",
                        "width",
                        "height",
                        "job_id",
                    ]
                )

            else:
                clip.save(
                    update_fields=["compressed_verified", "url", "duration", "job_id"]
                )

            clip_post = clip.clip_post
            send_clip_notifications_task.delay(clip_post.pk)

        except Clip.DoesNotExist:
            print("Clip.DoesNotExist", upload_file_key, compressed_file_key)
            fileargs = VIDEO_FILE_ARGS
            for filearg in fileargs:
                vid_file_key = compressed_file_key.format(filearg)
                if default_storage.exists(vid_file_key):
                    default_storage.delete(vid_file_key)


@celery_app.task(queue="celery")
def delete_invalid_duration_clip(input_s3_url):
    # Delete clip
    bucket_url = "s3://{bucket_name}/".format(
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME
    )
    upload_file_key = input_s3_url.split(bucket_url)[1]

    upload_filename = input_s3_url.split(settings.S3_FILE_UPLOAD_PATH_PREFIX + "/")[
        1
    ].split(".")[0]

    compressed_file_key = "{}/{}_{}.mp4".format(
        settings.S3_FILE_COMPRESSED_PATH_PREFIX, upload_filename, "{}"
    )

    try:
        clip = Clip.objects.get(url=get_media_file_url(file_path=upload_file_key))
        clip.delete()
        delete_clip_task.delay(get_media_file_url(compressed_file_key))
    except Clip.DoesNotExist:
        pass


@celery_app.task(queue="celery")
def delete_clip_task(url):
    file_path = get_media_file_path(url)
    # Replace hex symbols
    file_path = file_path.replace("%7B", "{")
    file_path = file_path.replace("%7D", "}")

    if default_storage.exists(file_path):
        # Upload
        delete_upload_file(file_path)
    # Upload and compressed
    fileargs = VIDEO_FILE_ARGS
    for filearg in fileargs:
        vid_file_key = file_path.format(filearg)
        if default_storage.exists(vid_file_key):
            default_storage.delete(vid_file_key)


@celery_app.task(queue="celery")
def send_clip_notifications_task(post_id):
    try:
        clip_post = Post.objects.get(pk=post_id)
        user_pk = clip_post.posted_by.pk
        game_name = clip_post.game.name
        title = clip_post.title
        tags = clip_post.tags.all()
        try:
            sender = User.objects.get(pk=user_pk)
            followers = Following.objects.filter(user=sender)
            extra_data = {"post_id": post_id, "game_name": game_name, "title": title}

            create_inotif_task(
                type=Notification.CLIP,
                sender_pk=user_pk,
                receiver_pk=user_pk,
                extra_data=extra_data,
            )
            for follower in followers:
                if tags.filter(pk=follower.profile.user.pk).exists():
                    create_inotif_task(
                        type=Notification.TAG,
                        sender_pk=user_pk,
                        receiver_pk=follower.profile.user.pk,
                        extra_data=extra_data,
                    )
                else:
                    create_inotif_task(
                        type=Notification.CLIP,
                        sender_pk=user_pk,
                        receiver_pk=follower.profile.user.pk,
                        extra_data=extra_data,
                    )
        except User.DoesNotExist:
            return
    except Post.DoesNotExist:
        return
