from rest_framework.serializers import ModelSerializer

from authentication.models import User

##########################################
class UserSignupSerializer(ModelSerializer):
    # Used to sign the player up
    class Meta:
        model = User
        fields = ["username", "password", "email", "first_name", "last_name", "picture"]
