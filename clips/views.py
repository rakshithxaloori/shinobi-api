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
    return JsonResponse(
        {
            "detail": "{} can upload {} more clips".format(
                request.user.username, 3 - clips_count
            ),
            "payload": {
                "quota": 3 - clips_count,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def generate_s3_presigned_url_view(request):
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
    clip_height_to_width_ratio = request.data.get("clip_height_to_width_ratio", None)

    if clip_size is None:
        return JsonResponse(
            {"detail": "clip_size is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    clip_size = int(clip_size)
    if clip_size <= 10:
        return JsonResponse(
            {"detail": "Invalid clip_size"}, status=status.HTTP_400_BAD_REQUEST
        )
    elif clip_size > 50 * 1000 * 1000:
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
    if clip_height_to_width_ratio is None or clip_height_to_width_ratio < 0:
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
        clip_height_to_width_ratio = float(clip_height_to_width_ratio)
    except ValueError:
        return JsonResponse(
            {"detail": "clip_height_to_width_ratio invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    file_path = "clips/uploads/{username}/{filename}.{type}".format(
        username=request.user.username, filename=uuid.uuid4(), type=clip_type
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
        uploader=request.user,
        game=game,
        url=file_url,
        height_to_width_ratio=clip_height_to_width_ratio,
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

    id = request.data.get("id", 0)
    id_top = request.data.get("id_top", 0)

    if id_top is None:
        return JsonResponse(
            {"detail": "id_top is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        id = int(id)
        id_top = int(id_top)
    except (ValueError, TypeError):
        return JsonResponse(
            {"detail": "invalid id or id_top"}, status=status.HTTP_400_BAD_REQUEST
        )

    clip_count = 2

    if id == 0:
        clips = Clip.objects.filter(upload_verified=True).order_by("-id")[:clip_count]
    else:
        clips = Clip.objects.filter(id__lt=id, upload_verified=True).order_by("-id")[
            :clip_count
        ]

    refresh = Clip.objects.filter(upload_verified=True).order_by("-id").first()

    if refresh is None or id_top == 0 or refresh.id == id_top:
        refresh = False
    else:
        refresh = True

    clips_data = ClipSerializer(clips, many=True).data

    return JsonResponse(
        {
            "detail": "clips from {}".format(id),
            "payload": {"clips": clips_data, "refresh": refresh},
        },
        status=status.HTTP_200_OK,
    )
