from rest_framework.serializers import ModelSerializer,SerializerMethodField

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
    follower_count = SerializerMethodField()

    class Meta:
        model = Profile
        fields=["user", "follower_count", "bio"]

    def get_follower_count(self, obj):
        return obj.user.follower.count()