from rest_framework.serializers import ModelSerializer

from socials.models import Socials


class SocialsSerializer(ModelSerializer):
    class Meta:
        model = Socials
        fields = ["youtube", "instagram", "twitch"]
        read_only_fields = fields
