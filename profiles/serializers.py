from rest_framework.serializers import ModelSerializer, SerializerMethodField

from authentication.models import User
from profiles.models import Game, Profile, Following
from socials.serializers import SocialsSerializer

##########################################
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "picture"]
        read_only_fields = fields


class FullProfileSerializer(ModelSerializer):
    user = UserSerializer()
    followers = SerializerMethodField()
    following = SerializerMethodField()
    me_following = SerializerMethodField()
    socials = SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["user", "followers", "following", "bio", "me_following", "socials"]

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

    def get_socials(self, obj):
        return SocialsSerializer(obj).data


##########################################
class MiniProfileSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ["user", "follower_count"]


##########################################
class FollowersSerializer(ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = Following
        fields = ["user"]

    def get_user(self, obj):
        return UserSerializer(obj.profile.user).data


##########################################
class FollowingSerializer(ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = User
        fields = ["user"]

    def get_user(self, obj):
        return UserSerializer(obj).data


##########################################
class GameSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = ["id", "game_code", "name", "logo_url"]
