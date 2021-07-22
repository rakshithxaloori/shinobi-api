from authentication.models import User
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from notification.models import Notification

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
        fields = ["sender", "type", "sent_at"]
        read_only_fields = fields
