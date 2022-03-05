from rest_framework.serializers import ModelSerializer, SerializerMethodField

from clips.models import Clip

##########################################
class ClipSerializer(ModelSerializer):
    view_count = SerializerMethodField()

    class Meta:
        model = Clip
        fields = ["id", "height", "width", "duration", "url", "thumbnail", "view_count"]
        read_only_fields = fields

    def get_view_count(self, obj):
        try:
            if obj.clip_post.is_repost:
                return None
            else:
                return obj.view_count
        except Exception:
            return None

        # me = self.context.get("me", None)
        # if me is None:
        #     return None

        # try:
        #     if obj.clip_post.is_repost:
        #         return None
        #     elif me == obj.clip_post.posted_by:
        #         return obj.view_count
        #     else:
        #         return None
        # except Exception:
        #     return None
