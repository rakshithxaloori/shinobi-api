import uuid
import boto3

from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.utils import dateparse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework_api_key.permissions import HasAPIKey

from knox.auth import TokenAuthentication
from clips.serializers import ClipSerializer


from profiles.models import Game
from clips.models import Clip
from clips.tasks import (
    check_upload_after_delay,
    check_upload_successful_task,
)
from shinobi.utils import get_media_file_url


if settings.CI_CD_STAGE == "testing" or settings.CI_CD_STAGE == "production":
    s3_client = boto3.client(
        service_name="s3",
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
else:
    s3_client = None


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def upload_check_view(request):
    clips_count = Clip.objects.filter(created_date=timezone.datetime.today()).count()
    if clips_count < 3:
        return JsonResponse(
            {
                "detail": "{} can upload {} more clips".format(
                    request.user.username, 3 - clips_count
                ),
                "payload": {
                    "is_uploading": request.user.is_uploading_clip,
                    "quota": 3 - clips_count,
                },
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def generate_s3_presigned_url_view(request):
    if request.user.is_uploading_clip:
        return JsonResponse(
            {"detail": "uploading a clip, try again later"},
            status=status.HTTP_409_CONFLICT,
        )

    clips_count = Clip.objects.filter(
        created_date=timezone.datetime.today(), uploader=request.user
    ).count()
    if clips_count >= 3:
        return JsonResponse(
            {"detail": "Daily limit of 3 clips"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    clip_size = request.data.get("clip_size", None)
    clip_type = request.data.get("clip_type", None)
    game_code = request.data.get("game_code", None)
    title = request.data.get("title", None)

    if clip_size is None:
        return JsonResponse(
            {"detail": "clip_size is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    clip_size = int(clip_size)
    if clip_size <= 10:
        return JsonResponse(
            {"detail": "Invalid clip_size"}, status=status.HTTP_400_BAD_REQUEST
        )
    elif clip_size > 50000000:
        # 50 MB
        return JsonResponse(
            {"detail": "clip_size has to be less than 100 MB"},
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
    if len(title) > 30:
        return JsonResponse(
            {"detail": "title has to be less than 30 characters"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        game = Game.objects.get(id=game_code)
    except Game.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid game_code"}, status=status.HTTP_400_BAD_REQUEST
        )

    file_path = "clips/{username}/{filename}.{type}".format(
        username=request.user.username, filename=uuid.uuid4(), type=clip_type
    )
    fields = {
        "Content-Type": "multipart/form-data",
    }

    conditions = [
        ["content-length-range", clip_size - 10, clip_size + 10],
        {"content-type": "multipart/form-data"},
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
        title=title, uploader=request.user, game=game, url=file_url
    )
    new_clip.save()
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
def get_clips_view(request):
    # CAN ALSO USE ID?
    datetime = request.data.get("datetime", None)
    if datetime is None:
        return JsonResponse(
            {"detail": "datetime is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    print(datetime)
    datetime = dateparse.parse_datetime(datetime)
    if datetime is None:
        return JsonResponse(
            {"detail": "Invalid datetime"}, status=status.HTTP_400_BAD_REQUEST
        )

    clips = Clip.objects.filter(
        created_datetime__lt=datetime, upload_verified=True
    ).order_by("-created_datetime")[:2]

    clips_data = ClipSerializer(clips, many=True).data
    print(clips_data)

    return JsonResponse(
        {"detail": "clips from {}".format(datetime), "payload": {"clips": clips_data}},
        status=status.HTTP_200_OK,
    )
