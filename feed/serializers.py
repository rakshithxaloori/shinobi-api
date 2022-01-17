from rest_framework.serializers import ModelSerializer, SerializerMethodField
from clips.serializers import ClipSerializer

from feed.models import Post
from profiles.serializers import UserSerializer, GameSerializer

##########################################
class PostSerializer(ModelSerializer):
    clip = SerializerMethodField()
    posted_by = SerializerMethodField()
    game = SerializerMethodField()
    title = SerializerMethodField()
    likes = SerializerMethodField()
    reposts = SerializerMethodField()
    shares = SerializerMethodField()
    reposted_by = SerializerMethodField()
    me_like = SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "created_datetime",
            "clip",
            "posted_by",
            "game",
            "title",
            "likes",
            "reposts",
            "shares",
            "is_repost",
            "reposted_by",
            "me_like",
        ]
        read_only_fields = fields

    def get_clip(self, obj):
        context = {"me": self.context.get("me", None)}
        if obj.is_repost:
            if obj.repost is None:
                return None
            return ClipSerializer(obj.repost.clip, context=context).data
        return ClipSerializer(obj.clip, context=context).data

    def get_posted_by(self, obj):
        if obj.is_repost:
            if obj.repost is None:
                return None
            return UserSerializer(obj.repost.posted_by).data
        return UserSerializer(obj.posted_by).data

    def get_game(self, obj):
        if obj.is_repost:
            if obj.repost is None:
                return None
            return GameSerializer(obj.repost.game).data
        return GameSerializer(obj.game).data

    def get_title(self, obj):
        if obj.is_repost:
            if obj.repost is None:
                return None
            return obj.repost.title
        return obj.title

    def get_likes(self, obj):
        if obj.is_repost:
            if obj.repost is None:
                return None
            return obj.repost.liked_by.count()
        return obj.liked_by.count()

    def get_reposts(self, obj):
        if obj.is_repost:
            if obj.repost is None:
                return None
            return Post.objects.filter(repost=obj.repost).count()
        return Post.objects.filter(repost=obj).count()

    def get_shares(self, obj):
        if obj.is_repost:
            if obj.repost is None:
                return None
            return obj.repost.share_count
        return obj.share_count

    def get_reposted_by(self, obj):
        if obj.is_repost:
            return UserSerializer(obj.posted_by).data
        return None

    def get_me_like(self, obj):
        me = self.context.get("me", None)
        if me is None:
            return False
        try:
            if obj.is_repost:
                obj_pk = obj.repost.pk
            else:
                obj_pk = obj.pk
            return me.liked_posts.filter(pk=obj_pk).exists()
        except Exception:
            return False
