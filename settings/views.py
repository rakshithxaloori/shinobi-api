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


from settings.serializers import PrivacySettingsSerializer


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def get_privacy_settings(request):
    privacy_data = PrivacySettingsSerializer(request.user.profile.privacy_settings).data
    return JsonResponse(
        {
            "detail": "{}'s privacy settings".format(request.user.username),
            "payload": privacy_data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def update_privacy_settings(request):
    settings = request.data.get("settings", None)
    if settings is None:
        return JsonResponse(
            {"detail": "settings is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        serializer = PrivacySettingsSerializer(
            request.user.profile.privacy_settings, data=settings
        )
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"detail": "saved!"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {"detail": "settings invalid"}, status=status.HTTP_400_BAD_REQUEST
            )
    except Exception:
        return JsonResponse(
            {"detail": "settings invalid"}, status=status.HTTP_400_BAD_REQUEST
        )
