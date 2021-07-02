from django.http import JsonResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from knox.auth import TokenAuthentication

from authentication.models import User
from chat.models import Chat, Message
from chat.serializers import ChatSerializer, MessageSerializer


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def chats_view(request):
    """Send chats."""
    all_chats = request.user.chats
    all_chats_serializer = ChatSerializer(
        all_chats, many=True, context={"username": request.user.username}
    )
    return JsonResponse(
        {
            "detail": "{}'s chats".format(request.user.username),
            "payload": {"chats": all_chats_serializer.data},
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def chat_messages(request, chat_id, begin_index, end_index):
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

        messages_count = chat.messages.count()
        if messages_count <= end_index:
            messages = chat.messages[begin_index:]
        else:
            messages = chat.messages[begin_index:end_index]

        messages_serializer = MessageSerializer(messages, many=True)
        return JsonResponse(
            {
                "detail": "{}'s chat".format(request.user.username),
                "payload": {"chats": messages_serializer.data},
            },
            status=status.HTTP_200_OK,
        )

    except Chat.DoesNotExist:
        pass
    except Message.DoesNotExist:
        pass
