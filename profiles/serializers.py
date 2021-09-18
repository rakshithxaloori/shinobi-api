from rest_framework.serializers import ModelSerializer, SerializerMethodField

from authentication.models import User
from profiles.models import Profile
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
    game_alias = SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["user", "game_alias", "follower_count"]

    def get_game_alias(self, obj):
        """Return the game that user plays the most."""
        try:
            # TODO {game_alias, game_logo_url}
            # The currently supported formats are png, jpg, jpeg, bmp, gif, webp, psd (iOS only) - RN Image Component
            return {
                "alias": obj.lol_profile.name,
                "logo": "https://ubuntuhandbook.org/wp-content/uploads/2018/09/lol-icon.png",
            }
        except Exception:
            return {"alias": "", "logo": ""}
