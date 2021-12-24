from rest_framework.serializers import ModelSerializer, SerializerMethodField

from clips.models import Clip

##########################################
class ClipSerializer(ModelSerializer):
    class Meta:
        model = Clip
        fields = [
            "id",
            "height",
            "width",
            "url",
        ]
        read_only_fields = fields
