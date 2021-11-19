import pickle

from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework_api_key.permissions import HasAPIKey

from knox.auth import TokenAuthentication


from clips.tasks import upload_clip
from clips.models import Clip


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def upload_check_view(request):
    clips_count = Clip.objects.filter(created_date=timezone.datetime.today()).count()
    if clips_count < 5:
        return JsonResponse(
            {
                "detail": "{} can upload {} more clips".format(
                    request.user.username, 5 - clips_count
                ),
                "payload": {
                    "uploading": request.user.is_uploading_clip,
                    "quota": 5 - clips_count,
                },
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def upload_clip_view(request):
    # Check for daily upload limit
    if request.user.is_uploading_clip:
        return JsonResponse(
            {"detail": "uploading a clip, try again later"},
            status=status.HTTP_409_CONFLICT,
        )
    clips_count = Clip.objects.filter(
        created_date=timezone.datetime.today(), uploader=request.user
    ).count()
    if clips_count >= 5:
        return JsonResponse(
            {"detail": "Daily limit of 5 clips"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
    else:
        # game_code = request.POST.get("game_code", None)
        # # TODO Verify game code
        # if game_code is None:
        #     return JsonResponse(
        #         {"detail": "game_code missing"}, status=status.HTTP_400_BAD_REQUEST
        #     )

        clip_obj = request.FILES.get("clip", None)
        if clip_obj is None:
            return JsonResponse(
                {"detail": "clip missing"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Cache the clip
        clip_cache_key = "clip:{username}".format(username=request.user.username)
        cache.set(clip_cache_key, pickle.dumps(clip_obj), timeout=3600)
        upload_clip.delay(request.user.pk, clip_cache_key, "", clip_obj.content_type)
        return JsonResponse(
            {"detail": "uploading {}'s clip".format(request.user.username)},
            status=status.HTTP_200_OK,
        )
