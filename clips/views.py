import uuid
import json
from urllib.parse import urlencode
from urllib.request import urlopen


from django.http import JsonResponse
from django.conf import settings
from django.http.response import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework_api_key.permissions import HasAPIKey

from knox.auth import TokenAuthentication
from analytics.tasks import add_view_analytics_task


from authentication.models import User
from feed.models import Post
from feed.utils import POST_TITLE_LENGTH, get_users_for_tags
from profiles.models import Game
from clips.models import Clip
from clips.tasks import (
    check_convert_successful_task,
    check_upload_task,
    delete_invalid_duration_clip,
)
from clips.utils import (
    UPLOAD_TYPE,
    VIDEO_MAX_SIZE_IN_BYTES,
    create_presigned_s3_url,
    sns_client,
)
from shinobi.utils import get_country_code, get_ip_address, get_media_file_url

CLIP_DAILY_LIMIT = 20
MIN_CLIP_DURATION = 5
MAX_CLIP_DURATION = 61
URI_RECAPTCHA = "https://www.google.com/recaptcha/api/siteverify"


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def upload_check_view(request):
    clips_count = Clip.objects.filter(created_date=timezone.datetime.today()).count()
    quota = CLIP_DAILY_LIMIT - clips_count

    datetime_now = timezone.now()
    time = 24 - datetime_now.hour
    if time == 0:
        time = 60 - datetime_now.minute
        if time == 0:
            time = "{} seconds".format(60 - datetime_now.second)
        else:
            time = "{} minutes".format(time)
    else:
        time = "{} hours".format(time)

    return JsonResponse(
        {
            "detail": "{} can upload {} more clips".format(
                request.user.username, quota
            ),
            "payload": {"quota": quota, "time_left": time},
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def generate_s3_presigned_url_view(request):
    # Verify recaptcha
    uploaded_from = Clip.MOBILE
    if request.path == "/clips/presigned/web/":
        recaptcha_token = request.data.get("recaptcha_token", None)
        if recaptcha_token is None:
            content = {"detail": "Recaptcha token required"}
            return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)

        params = urlencode(
            {
                "secret": settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                "response": recaptcha_token,
            }
        )
        data = urlopen(URI_RECAPTCHA, params.encode("utf-8")).read()
        result = json.loads(data)
        success = result.get("success", None)
        if not success or success is None:
            content = {"detail": "Recaptcha verification failed"}
            return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            uploaded_from = Clip.WEB

    clips_count = Clip.objects.filter(
        created_date=timezone.datetime.today(), clip_post__posted_by=request.user
    ).count()
    if clips_count >= CLIP_DAILY_LIMIT:
        return JsonResponse(
            {"detail": "Daily limit of {} clips".format(CLIP_DAILY_LIMIT)},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    clip_size = request.data.get("clip_size", None)
    clip_type = request.data.get("clip_type", None)
    game_id = request.data.get("game_code", None)
    title = request.data.get("title", None)
    tags = request.data.get("tags", None)

    duration = request.data.get("duration", None)
    clip_height = request.data.get("clip_height", None)
    clip_width = request.data.get("clip_width", None)

    if clip_size is None:
        return JsonResponse(
            {"detail": "clip_size is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    clip_size = int(clip_size)
    if clip_size <= 10:
        return JsonResponse(
            {"detail": "Invalid clip_size"}, status=status.HTTP_400_BAD_REQUEST
        )
    elif clip_size > VIDEO_MAX_SIZE_IN_BYTES:
        return JsonResponse(
            {"detail": "clip_size has to be less than 500 MB"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if clip_type is None:
        return JsonResponse(
            {"detail": "clip_type is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    if game_id is None:
        return JsonResponse(
            {"detail": "game_code is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    if title is None or type(title) != str:
        return JsonResponse(
            {"detail": "title is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    if len(title) > POST_TITLE_LENGTH:
        return JsonResponse(
            {
                "detail": "title has to be less than {} characters".format(
                    POST_TITLE_LENGTH
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid game_code"}, status=status.HTTP_400_BAD_REQUEST
        )

    if duration is None:
        return JsonResponse(
            {"detail": "Duration required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if clip_height is None or clip_width is None:
        return JsonResponse(
            {"detail": "clip_height, clip_width required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        duration = int(duration)
    except ValueError:
        return JsonResponse(
            {"detail": "duration invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        clip_height = int(clip_height)
        clip_width = int(clip_width)
    except ValueError:
        return JsonResponse(
            {"detail": "clip height or width invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if duration != 0 and (duration < MIN_CLIP_DURATION or duration > MAX_CLIP_DURATION):
        return JsonResponse(
            {"detail": "Duration invalid"}, status=status.HTTP_400_BAD_REQUEST
        )
    if clip_height < 0 or clip_width < 0:
        return JsonResponse(
            {"detail": "clip_height, clip_width invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    clip_uuid = uuid.uuid4()
    clip_file_path = "{prefix}/{filename}.{type}".format(
        prefix=settings.S3_FILE_UPLOAD_PATH_PREFIX,
        filename=clip_uuid,
        type=clip_type,
    )

    clip_s3_url = create_presigned_s3_url(clip_size, clip_file_path, UPLOAD_TYPE.CLIP)

    thumbnail_size = request.data.get("thumbnail_size", None)
    thumbnail_type = request.data.get("thumbnail_type", None)
    thumbnail_file_url = None
    thumbnail_s3_url = None
    if thumbnail_size is not None and thumbnail_type is not None:
        thumbnail_file_path = "{prefix}/{filename}.{type}".format(
            prefix=settings.S3_FILE_THUMBNAIL_PATH_PREFIX,
            filename=uuid.uuid4(),
            type=thumbnail_type,
        )
        thumbnail_s3_url = create_presigned_s3_url(
            thumbnail_size, thumbnail_file_path, UPLOAD_TYPE.THUMBNAIL
        )
        thumbnail_file_url = get_media_file_url(thumbnail_file_path)

    # Create Clip
    new_clip = Clip.objects.create(
        file_uuid=clip_uuid,
        upload_path=clip_file_path,
        thumbnail=thumbnail_file_url,
        duration=duration,
        height=clip_height,
        width=clip_width,
        uploaded_from=uploaded_from,
    )
    new_clip.save()
    new_post = Post.objects.create(
        clip=new_clip,
        posted_by=request.user,
        game=game,
        title=title,
        country_code=get_country_code(get_ip_address(request=request)),
    )
    new_post.tags.set(get_users_for_tags(request.user, tags))
    new_post.save()
    check_upload_task.apply_async(
        args=[new_clip.upload_path],
        eta=timezone.now() + timezone.timedelta(hours=1, minutes=10),
    )

    return JsonResponse(
        {
            "detail": "",
            "payload": {
                "url": clip_s3_url,
                "thumbnail_url": thumbnail_s3_url,
                "post_id": new_post.id,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def upload_successful_view(request):
    upload_path = request.data.get("file_key", None)
    if upload_path is None:
        return JsonResponse(
            {"detail": "file_key is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    check_upload_task.delay(upload_path)

    return JsonResponse({"detail": ""}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def viewed_clip_view(request):
    clip_id = request.data.get("clip_id", None)
    if clip_id is None:
        return JsonResponse(
            {"detail": "clip_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        clip = Clip.objects.get(id=clip_id)
    except Clip.DoesNotExist:
        return JsonResponse(
            {"detail": "clip_id invalid"}, status=status.HTTP_400_BAD_REQUEST
        )

    clip.viewed_by.add(request.user)

    if request.user != clip.clip_post.posted_by:
        clip.view_count += 1
        clip.save(update_fields=["view_count"])

    add_view_analytics_task.delay()
    return JsonResponse({"detail": "clip viewed"}, status=status.HTTP_200_OK)


@csrf_exempt
def mediaconvert_sns_view(request):
    json_data = json.loads(request.body)
    if json_data["Type"] == "SubscriptionConfirmation":
        # Confirm subscription
        response = sns_client.confirm_subscription(
            TopicArn=settings.AWS_SNS_TOPIC_ARN, Token=json_data["Token"]
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            print(response)
            # TODO get input url from

    else:
        try:
            message = json.loads(json_data["Message"])
            input_url = message["input_url"]
            jobID = message["jobID"]
            duration = message["fullDetails"]["outputGroupDetails"][0]["outputDetails"][
                0
            ]["durationInMs"]
            videoDetails = message["fullDetails"]["outputGroupDetails"][0][
                "outputDetails"
            ][0]["videoDetails"]

            if (
                duration < MIN_CLIP_DURATION * 1000
                or duration > MAX_CLIP_DURATION * 1000
            ):
                # Delete clip
                delete_invalid_duration_clip.delay(input_url)

            else:
                # Fire a task that verifies the clip
                check_convert_successful_task.delay(
                    input_url, jobID, duration, videoDetails
                )

        except Exception as e:
            print("EXCEPTION", e)

    return HttpResponse(status=status.HTTP_200_OK)
