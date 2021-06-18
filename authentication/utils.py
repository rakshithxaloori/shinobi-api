from django.http import JsonResponse
from django.utils import timezone

from rest_framework import status

from knox.models import AuthToken


def token_response(user):
    token = AuthToken.objects.create(user)[1]
    content = {"detail": "Logged in", "token_key": token}
    # Change user's last login to current time
    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])
    return JsonResponse(content, status=status.HTTP_200_OK)
