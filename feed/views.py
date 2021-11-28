from django.http import JsonResponse

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
def feed_view(request):
    """Response contains the clips of all the followings."""
    try:
        begin_index = int(request.data.get("begin_index", 0))
        end_index = int(request.data.get("end_index", 10))
    except Exception:
        begin_index = 0
        end_index = 10
    following_users = request.user.profile.followings.all()
    following_users |= User.objects.filter(pk=request.user.pk)
    clips = Clip.objects.filter(uploader__in=following_users).order_by(
        "-created_datetime"
    )[begin_index:end_index]

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
