from django.http import JsonResponse
from django.utils import timezone
from django.db.models import F

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework_api_key.permissions import HasAPIKey

from knox.auth import TokenAuthentication

from chat.models import Chat, Message, ChatUser
from chat.serializers import ChatUserSerializer, MessageSerializer


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def chats_view(request, begin_index, end_index):
    if begin_index is None or end_index is None:
        return JsonResponse(
            {"detail": "Missing query params"}, status=status.HTTP_400_BAD_REQUEST
        )
    elif begin_index > end_index:
        return JsonResponse(
            {"detail": "Invalid indices"}, status=status.HTTP_400_BAD_REQUEST
        )

    chat_users = request.user.chat_users
    username = request.user.username

    try:
        chat_users_count = chat_users.count()
        if chat_users_count <= begin_index:
            return JsonResponse(
                {
                    "detail": "{}'s chats".format(username),
                    "payload": {"chat_users": []},
                },
                status=status.HTTP_200_OK,
            )

        if chat_users_count <= end_index:
            chat_users = chat_users.order_by("-chat__last_updated")[begin_index:]
        else:
            chat_users = chat_users.order_by("-chat__last_updated")[
                begin_index:end_index
            ]

        chats_serializer = ChatUserSerializer(
            chat_users, many=True, context={"username": username}
        )
        return JsonResponse(
            {
                "detail": "{}'s chats".format(username),
                "payload": {"chat_users": chats_serializer.data},
            },
            status=status.HTTP_200_OK,
        )

    except Chat.DoesNotExist:
        return JsonResponse(
            {
                "detail": "{}'s chats".format(username),
                "payload": {"chat_users": []},
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def chat_messages(request, chat_id, begin_index=0, end_index=25):
    """Send chat messages."""
    if chat_id is None or begin_index is None or end_index is None:
        return JsonResponse(
            {"detail": "Missing query params"}, status=status.HTTP_400_BAD_REQUEST
        )
    elif begin_index > end_index:
        return JsonResponse(
            {"detail": "Invalid indices"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        chat = Chat.objects.get(id=chat_id)

        messages_count = chat.messages.all().count()
        if messages_count <= begin_index:
            return JsonResponse(
                {
                    "detail": "{}'s chat".format(request.user.username),
                    "payload": {"messages": None},
                },
                status=status.HTTP_200_OK,
            )
        if messages_count <= end_index:
            messages = chat.messages.order_by("-sent_at")[begin_index:]
        else:
            messages = chat.messages.order_by("-sent_at")[begin_index:end_index]

        messages_serializer = MessageSerializer(messages, many=True)
        return JsonResponse(
            {
                "detail": "{}'s chat".format(request.user.username),
                "payload": {"messages": messages_serializer.data},
            },
            status=status.HTTP_200_OK,
        )

    except Chat.DoesNotExist:
        return JsonResponse(
            {"detail": "Chat doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Message.DoesNotExist:
        return JsonResponse(
            {
                "detail": "{}'s chat".format(request.user.username),
                "payload": {"messages": None},
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def last_read_view(request):
    chat_id = request.data.get("chat_id", None)
    if chat_id is None:
        return JsonResponse(
            {"detail": "chat_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        chat_user = ChatUser.objects.get(chat__pk=chat_id, user=request.user)
        chat_user.last_read = timezone.now()
        chat_user.save(update_fields=["last_read"])
        return JsonResponse({"detail": "last_read updated"}, status=status.HTTP_200_OK)

    except ChatUser.DoesNotExist:
        return JsonResponse(
            {"detail": "chat_id invalid"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def unread_view(request):
    """Return True if there are unread chats, False otherwise."""
    unread_bool = request.user.chat_users.filter(
        last_read__lt=F("chat__last_updated")
    ).exists()

    unread_bool = False
    for chat_user in request.user.chat_users.order_by("chat__last_updated"):
        if chat_user.last_read < chat_user.chat.last_updated:
            unread_bool = True
            break

    return JsonResponse(
        {"detail": "Unread if any", "payload": {"unread": unread_bool}},
        status=status.HTTP_200_OK,
    )
