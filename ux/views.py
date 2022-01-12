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


from ux.models import AppUpdate
from ux.serializers import AppUpdateSerializer

# Create your views here.
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def get_updates_view(request):
    version = request.data.get("version", None)
    if version is None:
        return JsonResponse(
            {"detail": "version is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        app_update = AppUpdate.objects.get(version=version)
        app_update_data = AppUpdateSerializer(app_update).data
        update_available = AppUpdate.objects.filter(
            created__gt=app_update.created
        ).exists()
        return JsonResponse(
            {
                "detail": "{}'s updates".format(version),
                "payload": {
                    "updates": app_update_data["updates"],
                    "update_available": update_available,
                },
            },
            status=status.HTTP_200_OK,
        )
    except AppUpdate.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid version"}, status=status.HTTP_400_BAD_REQUEST
        )
