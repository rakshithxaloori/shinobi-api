from rest_framework.serializers import ModelSerializer, SerializerMethodField

from authentication.models import User
from profiles.models import Profile, Following
from socials.serializers import SocialsSerializer
from profiles.utils import game_alias

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
    game_alias = SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["user", "game_alias", "follower_count"]

    def get_game_alias(self, obj):
        """Return the game that user plays the most."""
        return game_alias(obj)


##########################################
class FollowersSerializer(ModelSerializer):
    user = SerializerMethodField()
    game_alias = SerializerMethodField()

    class Meta:
        model = Following
        fields = ["user", "game_alias"]

    def get_user(self, obj):
        return UserSerializer(obj.profile.user).data

    def get_game_alias(self, obj):
        return game_alias(obj.profile)


##########################################
class FollowingSerializer(ModelSerializer):
    user = SerializerMethodField()
    game_alias = SerializerMethodField()

    class Meta:
        model = User
        fields = ["user", "game_alias"]

    def get_user(self, obj):
        return UserSerializer(obj).data

    def get_game_alias(self, obj):
        return game_alias(obj.profile)
