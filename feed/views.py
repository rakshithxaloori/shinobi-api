from django.http import JsonResponse
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


from authentication.models import User
from clips.models import Clip
from clips.serializers import ClipSerializer


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def following_feed_view(request):
    """Response contains the clips of all the followings."""
    datetime = request.data.get("datetime", None)
    if datetime is None:
        return JsonResponse(
            {"detail": "datetime is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    datetime = dateparse.parse_datetime(datetime)
    if datetime is None:
        return JsonResponse(
            {"detail": "Invalid datetime"}, status=status.HTTP_400_BAD_REQUEST
        )

    following_users = request.user.profile.followings.all()
    following_users |= User.objects.filter(pk=request.user.pk)
    clips = Clip.objects.filter(
        created_datetime__lt=datetime,
        uploader__in=following_users,
        upload_verified=True,
    ).order_by("-created_datetime")[:10]

    clips_data = ClipSerializer(clips, many=True, context={"me": request.user}).data

    return JsonResponse(
        {
            "detail": "{}'s feed".format(request.user.username),
            "payload": {
                "clips": clips_data,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def world_feed_view(request):
    """Returns clips from all users of the games that I play."""
    datetime = request.data.get("datetime", None)
    if datetime is None:
        return JsonResponse(
            {"detail": "datetime is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    datetime = dateparse.parse_datetime(datetime)
    if datetime is None:
        return JsonResponse(
            {"detail": "Invalid datetime"}, status=status.HTTP_400_BAD_REQUEST
        )

    games = request.user.profile.games

    clips = Clip.objects.filter(
        created_datetime__lt=datetime, game__in=games, upload_verified=True
    ).order_by("-created_datetime")[:10]

    clips_data = ClipSerializer(clips, many=True, context={"me": request.user}).data

    return JsonResponse(
        {
            "detail": "{}'s feed".format(request.user.username),
            "payload": {
                "clips": clips_data,
            },
        },
        status=status.HTTP_200_OK,
    )
