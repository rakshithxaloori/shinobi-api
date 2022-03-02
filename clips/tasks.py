from django.conf import settings
from django.core.files.storage import default_storage


from shinobi.celery import app as celery_app


from clips.utils import VIDEO_MAX_SIZE_IN_BYTES, VIDEO_FILE_ARGS, create_job, s3_client
from shinobi.utils import get_media_file_url, get_media_file_path
from clips.models import Clip
from feed.models import Post
from notification.tasks import create_inotif_task
from authentication.models import User
from profiles.models import Following
from notification.models import Notification


AWS_UPLOADS_BUCKET_NAME = settings.AWS_UPLOADS_BUCKET_NAME
S3_FILE_UPLOAD_PATH_PREFIX = settings.S3_FILE_UPLOAD_PATH_PREFIX
S3_FILE_CONVERT_PATH_PREFIX = settings.S3_FILE_CONVERT_PATH_PREFIX
S3_FILE_THUMBNAIL_PATH_PREFIX = settings.S3_FILE_THUMBNAIL_PATH_PREFIX


def _delete_upload_file(file_path: str):
    try:
        if file_path.startswith(S3_FILE_UPLOAD_PATH_PREFIX):
            s3_client.delete_object(Bucket=AWS_UPLOADS_BUCKET_NAME, Key=file_path)

    except s3_client.exceptions.NoSuchKey:
        pass


def _get_upload_size(file_path):
    try:
        response = s3_client.get_object_attributes(
            Bucket=AWS_UPLOADS_BUCKET_NAME,
            Key=file_path,
            ObjectAttributes=[
                "ObjectSize",
            ],
        )
        return response["ObjectSize"]
    except Exception:
        return 0


@celery_app.task(queue="celery")
def check_upload_task(upload_path):
    if upload_path is None:
        return
    try:
        clip = Clip.objects.get(
            upload_path=upload_path, upload_verified=False, convert_verified=False
        )
    except Clip.DoesNotExist:
        return

    file_size = _get_upload_size(clip.upload_path)

    if file_size > 0:
        if file_size > VIDEO_MAX_SIZE_IN_BYTES:
            clip.delete()
        else:
            clip.upload_verified = True
            clip.save(update_fields=["upload_verified"])
            create_job(
                file_path=clip.upload_path,
                height=clip.height,
                width=clip.width,
            )
    else:
        clip.delete()


@celery_app.task(queue="celery")
def check_convert_successful_task(upload_s3_url, jobID, durationInMs, videoDetails):
    # s3://plx-dev-uploads/clips/uploads/20secs.mov
    if upload_s3_url is None:
        return
    upload_bucket_url = "s3://{bucket_name}/".format(
        bucket_name=AWS_UPLOADS_BUCKET_NAME
    )
    upload_file_key = upload_s3_url.split(upload_bucket_url)[1]

    upload_filename = upload_s3_url.split(settings.S3_FILE_UPLOAD_PATH_PREFIX + "/")[
        1
    ].split(".")[0]

    convert_file_key = "{convert_prefix}/{filename}_4.mp4".format(
        convert_prefix=S3_FILE_CONVERT_PATH_PREFIX,
        filename=upload_filename,
    )

    if default_storage.exists(convert_file_key):
        # Delete the uploaded file
        _delete_upload_file(upload_file_key)

        try:
            convert_file_key = "{}/{}_{}.mp4".format(
                S3_FILE_CONVERT_PATH_PREFIX, upload_filename, "{}"
            )
            file_cdn_url = get_media_file_url(convert_file_key)

            clip = Clip.objects.get(upload_path=upload_file_key)
            clip.convert_verified = True
            clip.url = file_cdn_url
            clip.duration = durationInMs / 1000
            clip.job_id = jobID
            if clip.height == 0 or clip.width == 0:
                clip.width = videoDetails["widthInPx"]
                clip.height = videoDetails["heightInPx"]
                clip.save(
                    update_fields=[
                        "convert_verified",
                        "url",
                        "duration",
                        "width",
                        "height",
                        "job_id",
                    ]
                )

            else:
                clip.save(
                    update_fields=["convert_verified", "url", "duration", "job_id"]
                )

            clip_post = clip.clip_post
            send_clip_notifications_task.delay(clip_post.pk)

        except Clip.DoesNotExist:
            print("Clip.DoesNotExist", upload_file_key, convert_file_key)
            delete_clip_files.delay(upload_file_key, convert_file_key, None)


@celery_app.task(queue="celery")
def delete_invalid_duration_clip(upload_s3_url):
    # Delete clip
    upload_bucket_url = "s3://{bucket_name}/".format(
        bucket_name=AWS_UPLOADS_BUCKET_NAME
    )
    upload_file_key = upload_s3_url.split(upload_bucket_url)[1]

    try:
        clip = Clip.objects.get(upload_path=upload_file_key)
        delete_clip_files(
            clip.upload_path,
            get_media_file_path(clip.url),
            get_media_file_path(clip.thumbnail),
        )
        clip.delete()
    except Clip.DoesNotExist:
        pass


@celery_app.task(queue="celery")
def delete_clip_files(upload_path: str, convert_path: str, tb_path: str):
    # Delete upload file
    _delete_upload_file(upload_path)

    # Delete thumbnail
    if tb_path.startswith(S3_FILE_THUMBNAIL_PATH_PREFIX) and default_storage.exists(
        tb_path
    ):
        default_storage.delete(tb_path)

    # Delete convert files
    if convert_path is not None and convert_path.startswith(
        S3_FILE_CONVERT_PATH_PREFIX
    ):
        fileargs = VIDEO_FILE_ARGS
        for filearg in fileargs:
            vid_file_key = convert_path.format(filearg)
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
