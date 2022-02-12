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

from notification.models import Notification, ExponentPushToken
from notification.serializers import NotificationSerializer


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def notifications_view(request):
    datetime = request.data.get("datetime", None)
    fetch_count = request.data.get("fetch_count", 15)
    if datetime is None:
        return JsonResponse(
            {"detail": "datetime is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    datetime = dateparse.parse_datetime(datetime)
    if datetime is None:
        return JsonResponse(
            {"detail": "Invalid datetime"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user

    try:
        notifications = request.user.notifications.order_by("-sent_at").filter(
            sent_at__lt=datetime
        )[:fetch_count]

        notifications_data = NotificationSerializer(notifications, many=True).data

        return JsonResponse(
            {
                "detail": "{}'s notifications".format(user.username),
                "payload": {"notifications": notifications_data},
            },
            status=status.HTTP_200_OK,
        )

    except Notification.DoesNotExist:
        return JsonResponse(
            {
                "detail": "{}'s notifications".format(user.username),
                "payload": {"notifications": []},
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def push_token_create_view(request):
    # Happens when the user logs in
    token = request.data.get("token", None)
    if token is None:
        return JsonResponse(
            {"detail": "token is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        ExponentPushToken.objects.get(user=request.user, token=token)
    except ExponentPushToken.DoesNotExist:
        new_expo_push_token = ExponentPushToken.objects.create(
            user=request.user, token=token
        )
        new_expo_push_token.save()

    return JsonResponse({"detail": "Token saved"}, status=status.HTTP_200_OK)
