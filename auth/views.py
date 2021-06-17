from django.http import JsonResponse
from django.contrib.auth import User

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from knox.auth import TokenAuthentication
from knox.models import AuthToken

from rest_framework_api_key.permissions import HasAPIKey

from google.oauth2 import id_token
from google.auth.transport import requests

from decouple import config


from auth.utils import token_response


@api_view(["POST"])
@permission_classes([HasAPIKey])
def google_login_view(request):
    google_id_token = request.data.get("id_token", None)

    if google_id_token is None:
        return JsonResponse(
            {"detail": "id_token is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        id_info = id_token.verify_oauth2_token(google_id_token, requests.Request())
        if id_info["aud"] not in [config("GOOGLE_MOBILE_APP_CLIENT_ID")]:
            return JsonResponse(
                {"detail": "Couldn't verify"}, status=status.HTTP_403_FORBIDDEN
            )

        user = User.objects.get(email=id_info["email"])

        if not user.is_active:
            # Account disabled
            return JsonResponse(
                {"detail": "Account disabled"}, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        return token_response(user)

    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Account doesn't exist"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    except ValueError:
        # Invalid token
        return JsonResponse(
            {"detail": "id_token invalid"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def logout_view(request):
    # Logging out is simply deleting the token
    request._auth.delete()
    return JsonResponse({"detail": "Logged out"}, status=status.HTTP_200_OK)
