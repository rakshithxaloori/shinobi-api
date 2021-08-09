from rest_framework.serializers import ModelSerializer, SerializerMethodField

from authentication.models import User
from profiles.models import Game, Profile, TwitchProfile, TwitchStream, YouTubeProfile

##########################################
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "picture"]
        read_only_fields = fields


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


class ProfileSerializer(ModelSerializer):
    user = UserSerializer()
    followers = SerializerMethodField()
    following = SerializerMethodField()
    me_following = SerializerMethodField()
    twitch_profile = TwitchProfileSerializer()
    youtube = SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "user",
            "followers",
            "following",
            "bio",
            "me_following",
            "twitch_profile",
            "youtube",
        ]

    def get_followers(self, obj):
        return obj.user.follower.count()

    def get_following(self, obj):
        return obj.followings.count()

    def get_me_following(self, obj):
        me = self.context.get("me", None)
        if me is None:
            return False
        user_pk = self.context.get("user_pk")
        return me.profile.followings.filter(pk=user_pk).exists()

    def get_youtube(self, obj):
        try:
            return obj.youtube_profile.channel_id
        except YouTubeProfile.DoesNotExist:
            return None
