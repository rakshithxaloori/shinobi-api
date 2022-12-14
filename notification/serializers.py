from rest_framework.serializers import ModelSerializer

from notification.models import Notification
from authentication.models import User

##########################################
class SenderSerialzier(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "picture"]
        read_only_fields = fields


class NotificationSerializer(ModelSerializer):
    sender = SenderSerialzier()

    class Meta:
        model = Notification
        fields = ["id", "sender", "type", "sent_at", "extra_data"]
        read_only_fields = fields
