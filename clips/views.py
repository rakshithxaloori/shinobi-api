import uuid
import json
from urllib.parse import urlencode
from urllib.request import urlopen


from django.http import JsonResponse
from django.conf import settings
from django.http.response import HttpResponse
from django.utils import timezone
from django.utils import dateparse
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


from feed.models import Post
from profiles.models import Game
from clips.models import Clip
from clips.tasks import (
    check_compressed_successful_task,
    check_upload_after_delay,
    check_upload_successful_task,
)
from clips.utils import VIDEO_MAX_SIZE_IN_BYTES, s3_client, sns_client
from shinobi.utils import get_media_file_url

CLIP_DAILY_LIMIT = 20
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
    game_code = request.data.get("game_code", None)
    title = request.data.get("title", None)

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
    if game_code is None:
        return JsonResponse(
            {"detail": "game_code is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    if title is None:
        return JsonResponse(
            {"detail": "title is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    if len(title) > 40:
        return JsonResponse(
            {"detail": "title has to be less than 30 characters"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if clip_height is None or clip_height < 0 or clip_width is None or clip_width < 0:
        return JsonResponse(
            {"detail": "clip_height_to_width_ratio required or invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        game = Game.objects.get(id=game_code)
    except Game.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid game_code"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        clip_height = int(clip_height)
        clip_width = int(clip_width)
    except ValueError:
        return JsonResponse(
            {"detail": "clip height or width invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    file_path = "{prefix}/{filename}.{type}".format(
        prefix=settings.S3_FILE_UPLOAD_PATH_PREFIX,
        filename=uuid.uuid4(),
        type=clip_type,
    )
    fields = {
        "Content-Type": "multipart/form-data",
    }

    conditions = [
        ["content-length-range", clip_size - 10, clip_size + 10],
        {"content-type": "multipart/form-data"},
        # {"content-length": clip_size},
    ]
    expires_in = 3600
    url = s3_client.generate_presigned_post(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=file_path,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=expires_in,
    )

    file_url = get_media_file_url(file_path)
    # Create Clip

    new_clip = Clip.objects.create(
        url=file_url,
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
    )
    new_post.save()
    check_upload_after_delay.apply_async(
        args=[new_clip.pk], eta=timezone.now() + timezone.timedelta(hours=1, minutes=10)
    )

    return JsonResponse({"detail": "", "payload": url}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def upload_successful_view(request):
    file_key = request.data.get("file_key", None)
    if file_key is None:
        return JsonResponse(
            {"detail": "file_key is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    check_upload_successful_task.delay(file_key)

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
    clip.save()
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

    else:
        try:
            message = json.loads(json_data["Message"])
            # Fire a task that verifies the clip
            check_compressed_successful_task.delay(message["input_url"])
        except Exception as e:
            print(e)

    return HttpResponse(status=status.HTTP_200_OK)
