from iso3166 import countries

from django.http import JsonResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework_api_key.permissions import HasAPIKey

from knox.auth import TokenAuthentication


from authentication.utils import get_info_from_access_token, token_response, create_user
from authentication.models import User
from notification.tasks import delete_push_token
from authentication.tasks import user_offline, user_online
from shinobi.utils import get_country_code, get_ip_address


@api_view(["POST"])
@permission_classes([HasAPIKey])
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
@permission_classes([HasAPIKey])
def google_login_view(request):
    google_access_token = request.data.get("access_token", None)

    if google_access_token is None:
        return JsonResponse(
            {"detail": "access_token are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        google_info = get_info_from_access_token(access_token=google_access_token)
        if google_info is None:
            return JsonResponse(
                {"detail": "Couldn't verify"}, status=status.HTTP_403_FORBIDDEN
            )
        user = User.objects.get(email=google_info["email"])

        if not user.is_active:
            # Account disabled
            return JsonResponse(
                {"detail": "Account disabled"}, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        user_online.delay(user.pk, ip)
        return token_response(user)

    except ValueError:
        # Invalid token
        return JsonResponse(
            {"detail": "id_token invalid"}, status=status.HTTP_400_BAD_REQUEST
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Account doesn't exist. Signup to create an account!"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def logout_view(request):
    # Delete auth token
    request._auth.delete()

    # Change active status
    user_pk = request.user.pk
    user_offline.delay(user_pk)

    # Delete push token
    push_token = request.data.get("token", None)
    if push_token is not None:
        try:
            delete_push_token.delay(user_pk, push_token)
        except Exception:
            pass
    return JsonResponse({"detail": "Logged out"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([HasAPIKey])
def google_signup_view(request):
    google_access_token = request.data.get("access_token", None)

    if google_access_token is None:
        return JsonResponse(
            {"detail": "access_token are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        google_info = get_info_from_access_token(access_token=google_access_token)
        if google_info is None:
            return JsonResponse(
                {"detail": "Couldn't verify"}, status=status.HTTP_403_FORBIDDEN
            )

        user_already_exists = User.objects.get(email=google_info["email"])
        return token_response(user_already_exists)

    except User.DoesNotExist:
        username = request.data.get("username", None)
        return create_user(
            username,
            google_info["email"],
            google_info.get("given_name", ""),
            google_info.get("family_name", ""),
            google_info.get("picture", None),
        )

    except Exception as e:
        print(e)
        # Send a mail to somebody
        return JsonResponse(
            {"detail": "Invalid username or code"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def online_view(request):
    user = request.user

    user_online.delay(user.pk, get_ip_address(request))

    return JsonResponse(
        {
            "detail": "Active status updated",
            "payload": {
                "username": user.username,
                "picture": user.picture,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def offline_view(request):
    user_offline.delay(request.user.pk)
    return JsonResponse(
        {"detail": "Inactive status updated"}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def valid_token_view(request):
    return JsonResponse(
        {
            "detail": "token valid",
            "payload": {
                "username": request.user.username,
                "picture": request.user.picture,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def update_country_view(request):
    request.user.country_code = get_country_code(get_ip_address(request))
    request.user.save(update_fields=["country_code"])
    return JsonResponse({"detail": "country updated!"}, status=status.HTTP_200_OK)
