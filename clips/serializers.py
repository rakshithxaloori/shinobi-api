from rest_framework.serializers import ModelSerializer, SerializerMethodField

from profiles.serializers import UserSerializer
from clips.models import Clip
from socials.serializers import GameSerializer

##########################################
class ClipSerializer(ModelSerializer):
    uploader = UserSerializer()
    game = GameSerializer()
    likes = SerializerMethodField()
    me_like = SerializerMethodField()

    class Meta:
        model = Clip
        fields = [
            "id",
            "created_datetime",
            "uploader",
            "game",
            "title",
            "likes",
            "me_like",
            "height_to_width_ratio",
            "url",
        ]
        read_only_fields = fields

    def get_likes(self, obj):
        return obj.liked_by.count()

    def get_me_like(self, obj):
        me = self.context.get("me", None)
        if me is None:
            return False
        try:
            return me.liked_clips.filter(pk=obj.pk).exists()
        except Exception:
            return False
