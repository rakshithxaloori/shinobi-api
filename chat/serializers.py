from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.utils.model_meta import _get_fields

from chat.models import Chat, Message

##########################################
class MessageSerializer(ModelSerializer):
    sent_by = SerializerMethodField()

    class Meta:
        model = Message
        fields = ["text", "sent_by", "is_read", "sent_at"]
        read_only_fields = fields

    def get_sent_by(self, obj):
        return {"username": obj.sent_by.username, "picture": obj.sent_by.picture}


class ChatSerializer(ModelSerializer):
    # Used to sign the player up
    user = SerializerMethodField()
    last_message = SerializerMethodField()

    class Meta:
        model = Chat
        fields = ["id", "last_updated", "last_message", "user"]
        read_only_fields = fields

    def get_user(self, obj):
        users = obj.users.all()
        if self.context["username"] == users[0].username:
            user = users[0]
        else:
            user = users[1]

        return {"username": user.username, "picture": user.picture}

    def get_last_message(self, obj):
        try:
            last_message = obj.messages.order_by("-sent_at")[0]
            last_message_data = MessageSerializer(last_message).data
            return last_message_data
        except (Message.DoesNotExist, IndexError):
            return None