from django.http import JsonResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from knox.auth import TokenAuthentication


from authentication.models import User
from chat.models import Chat
from profiles.models import TwitchProfile
from profiles.serializers import ProfileSerializer, UserSerializer
from profiles.twitch import get_user_info
from profiles.utils import add_profile_picture


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_profile_view(request):
    profile_serializer = ProfileSerializer(request.user.profile)
    return JsonResponse(
        {
            "detail": "My profile data",
            "payload": {"profile": profile_serializer.data},
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile_view(request, username):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(username=username)
        profile_serializer = ProfileSerializer(user.profile)
        me_following = user in request.user.profile.following.all()
        print("me_following", me_following)
        return JsonResponse(
            {
                "detail": "{}'s profile data".format(username),
                "payload": {"profile": profile_serializer.data},
            },
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid username"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def follow_user_view(request, username):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        following_user = User.objects.get(username=username)
        profile = request.user.profile

        profile.following.add(following_user)
        profile.save()
        # Create a chat
        new_chat = Chat.objects.create()
        new_chat.save()
        new_chat.add(request.user, following_user)

        return JsonResponse(
            {"detail": "Following {}".format(username)}, status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid username"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def unfollow_user_view(request, username):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        following_user = User.objects.get(username=username)
        profile = request.user.profile

        profile.following.remove(following_user)
        profile.save()
        # Delete the chat
        chat = Chat.objects.filter(users__in=[request.user, following_user])
        chat.delete()

        return JsonResponse(
            {"detail": "Unfollowed {}".format(username)}, status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid username"}, status=status.HTTP_404_NOT_FOUND
        )

    except Chat.DoesNotExist:
        return JsonResponse(
            {"detail": "Unfollowed {}".format(username)}, status=status.HTTP_200_OK
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def remove_follower_view(request, username):
    """Remove the user from my followers list."""
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        follower_user = User.objects.get(username=username)
        profile = follower_user.profile
        profile.following.remove(request.user)

        return JsonResponse(
            {"detail": "Removed from followers"}, status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid username"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def twitch_connect_view(request):
    access_token = request.data.get("access_token", None)
    if access_token is None:
        return JsonResponse(
            {"detail": "access_token required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user_info = get_user_info(access_token=access_token)
        print(user_info)

        twitch_profile = TwitchProfile.objects.create(
            profile=request.user.profile,
            user_id=user_info.get("id", None),
            login=user_info.get("login", None),
            display_name=user_info.get("display_name", None),
            profile_image_url=user_info.get("profile_image_url", None),
            view_count=user_info.get("view_count", None),
        )
        twitch_profile.save()

        # Adds the picture if there was None or "" before
        add_profile_picture(request.user, user_info.get("profile_image_url", None))

        if user_info is None:
            return JsonResponse(
                {"detail": "Invalid access_token"}, status=status.HTTP_400_BAD_REQUEST
            )

        return JsonResponse({"detail": "Twitch connected!"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JsonResponse(
            {"detail": "Invalid access_token"}, status=status.HTTP_400_BAD_REQUEST
        )
