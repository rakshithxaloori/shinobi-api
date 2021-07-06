from rest_framework.serializers import ModelSerializer, SerializerMethodField

from authentication.models import User
from profiles.models import Profile

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

    class Meta:
        model = Profile
        fields = ["user", "followers", "following", "bio"]

    def get_followers(self, obj):
        return obj.user.follower.count()

    def get_following(self, obj):
        return obj.following.count()
