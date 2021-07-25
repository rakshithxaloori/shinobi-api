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

from chat.models import Chat, Message
from chat.serializers import ChatSerializer, MessageSerializer


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

    user = request.user

    try:
        chats_count = user.chats.count()
        if chats_count <= begin_index:
            return JsonResponse(
                {
                    "detail": "{}'s chats".format(user.username),
                    "payload": {"chats": []},
                },
                status=status.HTTP_200_OK,
            )

        if chats_count <= end_index:
            chats = user.chats.order_by("-last_updated")[begin_index:]
        else:
            chats = user.chats.order_by("-last_updated")[begin_index:end_index]

        chats_serializer = ChatSerializer(
            chats, many=True, context={"username": user.username}
        )
        return JsonResponse(
            {
                "detail": "{}'s chats".format(user.username),
                "payload": {"chats": chats_serializer.data},
            },
            status=status.HTTP_200_OK,
        )

    except Chat.DoesNotExist:
        return JsonResponse(
            {
                "detail": "{}'s chats".format(user.username),
                "payload": {"chats": []},
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
