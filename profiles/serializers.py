from rest_framework.serializers import ModelSerializer, SerializerMethodField

from authentication.models import User
from profiles.models import Profile, TwitchProfile, YouTubeProfile

##########################################
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "picture"]
        read_only_fields = fields


##########################################
class ProfileSerializer(ModelSerializer):
    user = UserSerializer()
    followers = SerializerMethodField()
    following = SerializerMethodField()
    twitch = SerializerMethodField()
    youtube = SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["user", "followers", "following", "bio", "twitch", "youtube"]

    def get_followers(self, obj):
        return obj.user.follower.count()

    def get_following(self, obj):
        return obj.following.count()

    def get_twitch(self, obj):
        try:
            return obj.twitch_profile.login
        except TwitchProfile.DoesNotExist:
            return None

    def get_youtube(self, obj):
        try:
            return obj.youtube_profile.channel_id
        except YouTubeProfile.DoesNotExist:
            return None
