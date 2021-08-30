from rest_framework.serializers import ModelSerializer, SerializerMethodField

from profiles.models import Game, Profile
from socials.models import TwitchProfile, TwitchStream, YouTubeProfile


##########################################
class GameSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = ["name", "logo_url"]
        read_only_fields = fields


class TwitchStreamSerializer(ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = TwitchStream
        fields = ["game", "title", "thumbnail_url"]
        read_only_fields = fields


##########################################
class TwitchProfileSerializer(ModelSerializer):
    is_streaming = SerializerMethodField()

    class Meta:
        model = TwitchProfile
        fields = ["login", "is_streaming"]
        read_only_fields = fields

    def get_is_streaming(self, obj):
        try:
            return obj.twitch_stream.is_streaming
        except Exception:
            return False


class SocialsSerializer(ModelSerializer):
    twitch_profile = TwitchProfileSerializer()
    youtube = SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["twitch_profile", "youtube"]

    def get_youtube(self, obj):
        try:
            return {"channel_id": obj.youtube_profile.channel_id}
        except YouTubeProfile.DoesNotExist:
            return None
