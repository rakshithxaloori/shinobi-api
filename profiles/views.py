from os import POSIX_FADV_DONTNEED
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
from profiles.models import TwitchProfile, YouTubeProfile
from profiles.serializers import ProfileSerializer, UserSerializer
from profiles import twitch
from profiles.utils import add_profile_picture
from profiles import youtube


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def all_profiles_view(request):
    user_serializer = UserSerializer(
        User.objects.filter(is_staff=False).exclude(username=request.user.username),
        many=True,
    )
    return JsonResponse(
        {"detail": "All user profiles", "payload": {"users": user_serializer.data}},
        status=status.HTTP_200_OK,
    )


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
        # TODO create only if the chat already doesn't exist
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

    try:
        # TODO Reconnect
        TwitchProfile.objects.get(profile=request.user.profile)
        return JsonResponse(
            {"detail": "Twitch profile already connected"},
            status=status.HTTP_208_ALREADY_REPORTED,
        )

    except TwitchProfile.DoesNotExist:
        access_token = request.data.get("access_token", None)
        if access_token is None:
            return JsonResponse(
                {"detail": "access_token required"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_info = twitch.get_user_info(access_token=access_token)

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


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def youtube_connect_view(request):
    try:
        # TODO Reconnect
        YouTubeProfile.objects.get(profile=request.user.profile)
        return JsonResponse(
            {"detail": "YouTube already connected"},
            status=status.HTTP_208_ALREADY_REPORTED,
        )
    except YouTubeProfile.DoesNotExist:
        access_token = request.data.get("access_token", None)
        if access_token is None:
            return JsonResponse(
                {"detail": "access_token required"}, status=status.HTTP_400_BAD_REQUEST
            )

        yt_channels = youtube.get_user_info(access_token=access_token).get("items")
        if yt_channels is None:
            return JsonResponse(
                {"detail": "access_token invalid"}, status=status.HTTP_400_BAD_REQUEST
            )

        if len(yt_channels) > 1:
            channel_ids = [
                {
                    "id": channel["id"],
                    "name": channel["snippet"]["title"],
                    "thumbnail": channel["snippet"]["thumbnails"]["default"],
                }
                for channel in yt_channels
            ]
            return JsonResponse(
                {
                    "detail": "Choose one YouTube channel",
                    "payload": {"channels": channel_ids},
                },
                status=status.HTTP_300_MULTIPLE_CHOICES,
            )

        # Create YouTubeProfile model with channel_id
        chosen_channel = yt_channels[0]

        image_url = chosen_channel["snippet"]["thumbnails"].get("medium", None)
        if image_url is None:
            image_url = chosen_channel["snippet"]["thumbnails"]["default"]
        image_url = image_url["url"]
        new_youtube_profile = YouTubeProfile.objects.create(
            profile=request.user.profile,
            channel_id=chosen_channel["id"],
            channel_image_url=image_url,
        )
        new_youtube_profile.save()
        return JsonResponse({"detail": "YouTube connected!"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def youtube_select_channel_view(request):
    try:
        # TODO Reconnect
        YouTubeProfile.objects.get(profile=request.user.profile)
        return JsonResponse(
            {"detail": "YouTube already connected"},
            status=status.HTTP_208_ALREADY_REPORTED,
        )
    except YouTubeProfile.DoesNotExist:
        access_token = request.data.get("access_token", None)
        channel_id = request.data.get("channel_id", None)
        if access_token is None or channel_id is None:
            return JsonResponse(
                {"detail": "access_token, channel_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        yt_channels = youtube.get_user_info(access_token=access_token).get("items")
        if yt_channels is None:
            # Session expired or invalid access_token
            return JsonResponse(
                {"detail": "access_token invalid or expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chosen_channel = None
        for channel in yt_channels:
            if channel["id"] == channel_id:
                chosen_channel = channel
                break

        if chosen_channel is not None:
            # Create YouTubeProfile model with channel_id
            image_url = chosen_channel["snippet"]["thumbnails"].get("medium", None)
            if image_url is None:
                image_url = chosen_channel["snippet"]["thumbnails"]["default"]
            image_url = image_url["url"]
            new_youtube_profile = YouTubeProfile.objects.create(
                profile=request.user.profile,
                channel_id=chosen_channel["id"],
                channel_image_url=image_url,
            )
            new_youtube_profile.save()
            return JsonResponse(
                {"detail": "YouTube connected!"}, status=status.HTTP_200_OK
            )
        else:
            return JsonResponse(
                {"detail": "Invalid channel_id"}, status=status.HTTP_400_BAD_REQUEST
            )
