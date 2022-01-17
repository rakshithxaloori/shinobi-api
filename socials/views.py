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


from socials.models import Socials
from socials.serializers import SocialsSerializer


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def get_socials_view(request):
    socials_data = SocialsSerializer(request.user.profile.socials).data

    return JsonResponse(
        {
            "detail": "{}'s socials".format(request.user.username),
            "payload": socials_data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def save_socials_view(request):
    youtube = request.data.get("youtube", None)
    instagram = request.data.get("instagram", None)
    twitch = request.data.get("twitch", None)

    socials = request.user.profile.socials
    socials.youtube = youtube
    socials.instagram = instagram
    socials.twitch = twitch
    socials.save()

    return JsonResponse(
        {"detail": "{}'s socials saved!".format(request.user.username)},
        status=status.HTTP_200_OK,
    )
