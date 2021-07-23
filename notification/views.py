from django.http import JsonResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from knox.auth import TokenAuthentication

from notification.models import Notification, ExponentPushToken
from notification.serializers import NotificationSerializer


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def notifications_view(request, begin_index, end_index):
    if begin_index is None or end_index is None:
        return JsonResponse(
            {"detail": "Missing query params"}, status=status.HTTP_400_BAD_REQUEST
        )
    elif begin_index > end_index:
        return JsonResponse(
            {"detail": "Invalid indices"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user

    try:
        notifications_count = user.notifications.count()
        if notifications_count <= begin_index:
            return JsonResponse(
                {
                    "detail": "{}'s notifications".format(user.username),
                    "payload": {"notifications": []},
                },
                status=status.HTTP_200_OK,
            )

        if notifications_count <= end_index:
            notifications = user.notifications.order_by("-sent_at")[begin_index:]
        else:
            notifications = user.notifications.order_by("-sent_at")[
                begin_index:end_index
            ]

        notifications_serializer = NotificationSerializer(notifications, many=True)

        return JsonResponse(
            {
                "detail": "{}'s notifications".format(user.username),
                "payload": {"notifications": notifications_serializer.data},
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
@permission_classes([IsAuthenticated])
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
