from rest_framework.serializers import ModelSerializer, SerializerMethodField

from profiles.serializers import UserSerializer
from clips.models import Clip
from socials.serializers import GameSerializer

##########################################
class ClipSerializer(ModelSerializer):
    uploader = UserSerializer()
    game = GameSerializer()
    likes = SerializerMethodField()

    class Meta:
        model = Clip
        fields = [
            "id",
            "created_datetime",
            "uploader",
            "game",
            "title",
            "likes",
            "height_to_width_ratio",
            "url",
        ]
        read_only_fields = fields

    def get_likes(self, obj):
        return obj.liked_by.count()
