import pickle

from django.http import JsonResponse
from django.core.cache import cache

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework_api_key.permissions import HasAPIKey

from knox.auth import TokenAuthentication


from authentication.models import User
from chat.models import Chat
from profiles.models import Profile, Following
from profiles.serializers import (
    FollowingSerializer,
    FullProfileSerializer,
    MiniProfileSerializer,
    FollowersSerializer,
)
from profiles.tasks import update_profile_picture


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def trending_profiles_view(request):
    trending_profiles = Profile.objects.order_by("-follower_count").filter(
        user__is_staff=False
    )[:10]

    profiles_data = MiniProfileSerializer(trending_profiles, many=True).data

    return JsonResponse(
        {
            "detail": "All user profiles",
            "payload": {"profiles": profiles_data},
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def my_profile_view(request):
    profile_data = FullProfileSerializer(request.user.profile).data
    return JsonResponse(
        {
            "detail": "My profile data",
            "payload": {"profile": profile_data},
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def profile_view(request, username):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(username=username)
        profile_data = FullProfileSerializer(
            user.profile, context={"me": request.user, "user_pk": user.pk}
        ).data
        return JsonResponse(
            {
                "detail": "{}'s profile data".format(username),
                "payload": {"profile": profile_data},
            },
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid username"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def search_view(request, username):
    profiles = Profile.objects.filter(
        user__username__startswith=username, user__is_staff=False
    )[:10]
    profiles_data = MiniProfileSerializer(profiles, many=True).data

    return JsonResponse(
        {
            "detail": "usernamess that start with {}".format(username),
            "payload": {"users": profiles_data},
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def follow_user_view(request, username):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        being_followed_user = User.objects.get(username=username)
        follower_profile = request.user.profile
        follower_profile.followings.add(being_followed_user)
        follower_profile.save()
        return JsonResponse(
            {"detail": "Following {}".format(username)}, status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid username"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def unfollow_user_view(request, username):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        being_followed_user = User.objects.get(username=username)
        profile = request.user.profile
        profile.followings.remove(being_followed_user)
        profile.save()
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
@permission_classes([IsAuthenticated, HasAPIKey])
def remove_follower_view(request, username):
    """Remove the user from my followers list."""
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        follower_user = User.objects.get(username=username)
        profile = follower_user.profile
        profile.followings.remove(request.user)

        return JsonResponse(
            {"detail": "{} removed from followers".format(follower_user.username)},
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid username"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def update_profile_view(request):
    bio = request.POST.get("bio", None)
    picture_obj = request.FILES.get("picture", None)
    if bio is not None:
        if len(bio) > 150:
            return JsonResponse(
                {"detail": "bio has to be less than 150 characters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            profile = request.user.profile
            profile.bio = bio
            profile.save(update_fields=["bio"])

    if picture_obj is not None:
        # do your validation here e.g. file size/type check
        if picture_obj.size > 5000000:
            # Greater than 5 MB
            return JsonResponse(
                {"detail": "Image has to be less than 5 MB"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if picture_obj.content_type != "image/png":
            return JsonResponse(
                {"detail": "Image has to be a PNG file"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cache the image
        picture_cache_key = "picture:{username}".format(username=request.user.username)
        cache.set(picture_cache_key, pickle.dumps(picture_obj), timeout=600)
        update_profile_picture.delay(
            request.user.pk,
            picture_cache_key,
            picture_obj.name,
            picture_obj.content_type,
        )

    return JsonResponse(
        {"detail": "{}'s profile updated".format(request.user.username)},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def followers_list_view(request, username=None, begin_index=0, end_index=10):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if not User.objects.filter(username=username).exists():
        return JsonResponse(
            {"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND
        )

    followers = Following.objects.filter(user__username=username)[begin_index:end_index]
    followers_serializers_data = FollowersSerializer(followers, many=True).data
    return JsonResponse(
        {
            "detail": "{}'s followers".format(username),
            "payload": {
                "followers": followers_serializers_data,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def following_list_view(request, username=None, begin_index=0, end_index=10):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if not User.objects.filter(username=username).exists():
        return JsonResponse(
            {"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND
        )

    following = Profile.objects.get(user__username=username).followings.all()[
        begin_index:end_index
    ]
    following_serializers_data = FollowingSerializer(following, many=True).data
    return JsonResponse(
        {
            "detail": "{}'s following".format(username),
            "payload": {
                "following": following_serializers_data,
            },
        },
        status=status.HTTP_200_OK,
    )
