from django.http import JsonResponse
from django.utils import timezone
from django.utils.crypto import get_random_string

from rest_framework import status

from knox.models import AuthToken

from authentication.serializers import UserSignupSerializer
from authentication.models import User


def token_response(user):
    token = AuthToken.objects.create(user)[1]
    content = {"detail": "Logged in", "token_key": token}
    # Change user's last login to current time
    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])
    return JsonResponse(content, status=status.HTTP_200_OK)


def create_user(username, email):
    try:
        if username is None:
            return JsonResponse(
                {"detail": "username required"}, status=status.HTTP_400_BAD_REQUEST
            )
        User.objects.get(username=username)
        return JsonResponse(
            {"detail": "Username taken"}, status=status.HTTP_409_CONFLICT
        )
    except User.DoesNotExist:
        # Create an account
        new_user_serializer = UserSignupSerializer(
            data={
                "username": username,
                "password": get_random_string(length=10),
                "email": email,
            }
        )
        if new_user_serializer.is_valid():
            new_user = new_user_serializer.save()
            new_user.set_unusable_password()
            new_user.save()
            return token_response(new_user)
        else:
            print(new_user_serializer.errors)
            return JsonResponse(
                {"detail": new_user_serializer.errors.values()[0]},
                status=status.HTTP_400_BAD_REQUEST,
            )
