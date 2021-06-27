from django.http import JsonResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from knox.auth import TokenAuthentication

from google.oauth2 import id_token
from google.auth.transport import requests

from decouple import config

from authentication.models import User


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_profile_view(request):
    return JsonResponse(
        {
            "detail": "",
            "payload": {
                "username": request.user.username,
                "picture": request.user.picture,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def follow_user_view(request, username):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        following_user = User.objects.get(username=username)

        request.user.profile.following.add(following_user)

        return JsonResponse({"detail": "Following added"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid username"}, status=status.HTTP_404_NOT_FOUND
        )
