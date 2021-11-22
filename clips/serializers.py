from rest_framework.serializers import ModelSerializer

from profiles.serializers import UserSerializer
from clips.models import Clip
from socials.serializers import GameSerializer

##########################################
class ClipSerializer(ModelSerializer):
    uploader = UserSerializer()
    game = GameSerializer()

    class Meta:
        model = Clip
        fields = [
            "id",
            "created_datetime",
            "uploader",
            "game",
            "title",
            "height_to_width_ratio",
            "url",
        ]
        read_only_fields = fields
