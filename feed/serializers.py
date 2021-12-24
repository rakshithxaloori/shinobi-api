from rest_framework.serializers import ModelSerializer, SerializerMethodField
from clips.serializers import ClipSerializer

from feed.models import Post
from profiles.serializers import UserSerializer
from socials.serializers import GameSerializer

##########################################
class PostSerializer(ModelSerializer):
    clip = ClipSerializer()
    uploader = UserSerializer()
    game = GameSerializer()
    likes = SerializerMethodField()
    me_like = SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "created_datetime",
            "clip",
            "uploader",
            "game",
            "title",
            "likes",
            "me_like",
        ]
        read_only_fields = fields

    def get_likes(self, obj):
        return obj.liked_by.count()

    def get_me_like(self, obj):
        me = self.context.get("me", None)
        if me is None:
            return False
        try:
            return me.liked_posts.filter(pk=obj.pk).exists()
        except Exception:
            return False
