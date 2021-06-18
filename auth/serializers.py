from django.conf.global_settings import AUTH_USER_MODEL as User

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

##########################################
class UserSignupSerializer(ModelSerializer):
    # Used to sign the player up
    class Meta:
        model = User
        fields = ["username", "password", "email"]
