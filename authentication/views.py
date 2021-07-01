from django.http import JsonResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from knox.auth import TokenAuthentication

from google.oauth2 import id_token
from google.auth.transport import requests

from decouple import config

from authentication.utils import token_response, create_user
from authentication.models import User


@api_view(["POST"])
def check_username_view(request):
    username = request.data.get("username", None)

    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        User.objects.get(username=username)
        return JsonResponse(
            {"detail": "Username taken"}, status=status.HTTP_406_NOT_ACCEPTABLE
        )
    except User.DoesNotExist:
        return JsonResponse({"detail": "Username available"}, status=status.HTTP_200_OK)


@api_view(["POST"])
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
        print(id_info)
        user = User.objects.get(email=id_info["email"])

        if not user.is_active:
            # Account disabled
            return JsonResponse(
                {"detail": "Account disabled"}, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        return token_response(user)

    except ValueError:
        # Invalid token
        return JsonResponse(
            {"detail": "id_token invalid"}, status=status.HTTP_400_BAD_REQUEST
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Account doesn't exist"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Logging out is simply deleting the token
    request._auth.delete()
    return JsonResponse({"detail": "Logged out"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def google_signup_view(request):
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

        email = id_info["email"]
        print(id_info)
        user_already_exists = User.objects.get(email=email)
        return token_response(user_already_exists)

    except User.DoesNotExist:
        username = request.data.get("username", None)
        return create_user(
            username,
            email,
            id_info.get("given_name", ""),
            id_info.get("family_name", ""),
            id_info.get("picture", None),
        )

    except ValueError:
        # Invalid token
        return JsonResponse(
            {"detail": "id_token invalid"}, status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        print(e)
        # Send a mail to somebody
        return JsonResponse(
            {"detail": "Invalid sign up form"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def token_valid_view():
    return JsonResponse({"detail": "Valid token"}, status=status.HTTP_200_OK)
