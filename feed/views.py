from django.http import JsonResponse
from django.utils import dateparse

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
from clips.models import Clip
from feed.serializers import PostSerializer
from feed.models import Post, Report
from profiles.utils import get_action_approve


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def following_feed_view(request):
    """Response contains the clips of all the followings."""
    datetime = request.data.get("datetime", None)
    if datetime is None:
        return JsonResponse(
            {"detail": "datetime is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    datetime = dateparse.parse_datetime(datetime)
    if datetime is None:
        return JsonResponse(
            {"detail": "Invalid datetime"}, status=status.HTTP_400_BAD_REQUEST
        )

    following_users = request.user.profile.followings.all()
    following_users |= User.objects.filter(pk=request.user.pk)
    clips = Clip.objects.filter(
        created_datetime__lt=datetime,
        uploader__in=following_users,
        compressed_verified=True,
    ).order_by("-created_datetime")[:10]

    clips_data = PostSerializer(clips, many=True, context={"me": request.user}).data

    return JsonResponse(
        {
            "detail": "{}'s feed".format(request.user.username),
            "payload": {
                "clips": clips_data,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def world_feed_view(request):
    """Returns clips from all users of the games that I play."""
    datetime = request.data.get("datetime", None)
    if datetime is None:
        return JsonResponse(
            {"detail": "datetime is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    datetime = dateparse.parse_datetime(datetime)
    if datetime is None:
        return JsonResponse(
            {"detail": "Invalid datetime"}, status=status.HTTP_400_BAD_REQUEST
        )

    games = request.user.profile.games

    clips = Clip.objects.filter(
        created_datetime__lt=datetime, game__in=games, upload_verified=True
    ).order_by("-created_datetime")[:10]

    clips_data = PostSerializer(clips, many=True, context={"me": request.user}).data

    return JsonResponse(
        {
            "detail": "{}'s feed".format(request.user.username),
            "payload": {
                "clips": clips_data,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def get_profile_posts_view(request):
    datetime = request.data.get("datetime", None)
    username = request.data.get("username", None)
    if datetime is None:
        return JsonResponse(
            {"detail": "datetime is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    datetime = dateparse.parse_datetime(datetime)
    if datetime is None:
        return JsonResponse(
            {"detail": "Invalid datetime"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse(
            {"detail": "Invalid username"}, status=status.HTTP_400_BAD_REQUEST
        )

    posts = Post.objects.filter(created_datetime__lt=datetime, uploader=user).order_by(
        "-created_datetime"
    )[:10]

    posts_data = PostSerializer(posts, many=True).data

    return JsonResponse(
        {"detail": "posts from {}".format(datetime), "payload": {"posts": posts_data}},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def get_post_view(request):
    post_id = request.data.get("post_id", None)
    if post_id is None:
        return JsonResponse(
            {"detail": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        post = Post.objects.get(id=post_id)
        post_data = PostSerializer(post).data
        return JsonResponse(
            {"detail": "post {}".format(post_id), "payload": {"post": post_data}},
            status=status.HTTP_200_OK,
        )
    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "invalid post_id"}, status=status.HTTP_400_BAD_REQUEST
        )


################################################


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def like_post_view(request):
    post_id = request.data.get("post_id", None)
    if post_id is None:
        return JsonResponse(
            {"detail": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    action_approved = get_action_approve(request.user)
    if not action_approved:
        return JsonResponse(
            {"detail": "Too many actions"}, status=status.HTTP_406_NOT_ACCEPTABLE
        )

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "Post doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    post.liked_by.add(request.user)
    post.save()
    return JsonResponse({"detail": "post liked"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def delete_post_view(request):
    post_id = request.data.get("post_id", None)
    if post_id is None:
        return JsonResponse(
            {"detail": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "Post doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    if post.uploader != request.user:
        return JsonResponse({"detail": "Denied"}, status=status.HTTP_401_UNAUTHORIZED)

    post.clip.delete()
    post.delete()
    return JsonResponse({"detail": "post deleted"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def unlike_post_view(request):
    post_id = request.data.get("post_id", None)
    if post_id is None:
        return JsonResponse(
            {"detail": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    action_approved = get_action_approve(request.user)
    if not action_approved:
        return JsonResponse(
            {"detail": "Too many actions"}, status=status.HTTP_406_NOT_ACCEPTABLE
        )

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "Post doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    post.liked_by.remove(request.user)
    post.save()
    return JsonResponse({"detail": "post unliked"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def share_post_view(request):
    post_id = request.data.get("post_id", None)
    if post_id is None:
        return JsonResponse(
            {"detail": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "post_id invalid"}, status=status.HTTP_400_BAD_REQUEST
        )

    post.share_count += 1
    post.save(update_fields=["share_count"])
    return JsonResponse({"detail": "post share"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def report_post_view(request):
    post_id = request.data.get("post_id", None)
    is_not_playing = request.data.get("not_play", None)
    is_not_game_clip = request.data.get("not_game", None)

    action_approved = get_action_approve(request.user)
    if not action_approved:
        return JsonResponse(
            {"detail": "Too many actions"}, status=status.HTTP_406_NOT_ACCEPTABLE
        )

    if post_id is None:
        return JsonResponse(
            {"detail": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    if is_not_playing is None or is_not_game_clip is None:
        return JsonResponse(
            {"detail": "values missing"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "post_id invalid"}, status=status.HTTP_400_BAD_REQUEST
        )

    report = Report.objects.create(
        reported_by=request.user,
        post=post,
        is_not_playing=is_not_playing,
        is_not_game_clip=is_not_game_clip,
    )
    report.save()
    return JsonResponse({"detail": "report received"}, status=status.HTTP_200_OK)
