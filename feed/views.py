from django.http import JsonResponse
from django.utils import dateparse
from django.db.models import Q

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
from feed.serializers import PostSerializer
from feed.models import Post, Report
from profiles.models import Game
from notification.models import Notification
from notification.tasks import create_inotif_task
from profiles.utils import get_action_approve
from feed.utils import (
    POST_TITLE_LENGTH,
    POSTS_FETCH_COUNT,
    TAGS_MAX_COUNT,
    get_users_for_tags,
    is_upload_count_zero,
)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def following_feed_view(request):
    """Response contains the posts of all the followings."""
    datetime = request.data.get("datetime", None)
    fetch_count = request.data.get("fetch_count", POSTS_FETCH_COUNT)
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
    posts = Post.objects.filter(
        Q(created_datetime__lt=datetime, posted_by__in=following_users),
        Q(is_repost=True, repost__clip__convert_verified=True)
        | Q(is_repost=False, clip__convert_verified=True),
    ).order_by("-created_datetime")[:fetch_count]

    posts_data = PostSerializer(posts, many=True, context={"me": request.user}).data

    return JsonResponse(
        {
            "detail": "{}'s feed".format(request.user.username),
            "payload": {
                "posts": posts_data,
                "upload": is_upload_count_zero(request.user),
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def world_feed_view(request):
    """Returns posts from all users of the games that I play."""
    datetime = request.data.get("datetime", None)
    fetch_count = request.data.get("fetch_count", POSTS_FETCH_COUNT)
    game_id = request.data.get("game_id", None)
    game = None
    if datetime is None:
        return JsonResponse(
            {"detail": "datetime is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    datetime = dateparse.parse_datetime(datetime)
    if datetime is None:
        return JsonResponse(
            {"detail": "Invalid datetime"}, status=status.HTTP_400_BAD_REQUEST
        )

    if game_id is not None:
        try:
            game = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            game = None

    if game is None:
        posts = Post.objects.filter(
            Q(created_datetime__lt=datetime),
            Q(is_repost=True, repost__clip__convert_verified=True)
            | Q(is_repost=False, clip__convert_verified=True),
        ).order_by("-created_datetime")[:fetch_count]
    else:
        posts = Post.objects.filter(
            Q(created_datetime__lt=datetime),
            Q(is_repost=True, repost__clip__convert_verified=True)
            | Q(is_repost=False, clip__convert_verified=True),
            Q(is_repost=True, repost__game=game) | Q(is_repost=False, game=game),
        ).order_by("-created_datetime")[:fetch_count]

    posts_data = PostSerializer(posts, many=True, context={"me": request.user}).data

    return JsonResponse(
        {
            "detail": "{}'s feed".format(request.user.username),
            "payload": {
                "posts": posts_data,
                "upload": is_upload_count_zero(request.user),
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
    fetch_count = request.data.get("fetch_count", POSTS_FETCH_COUNT)
    game_id = request.data.get("game_id", None)
    game = None
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

    if game_id is not None:
        try:
            game = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            game = None

    if game is None:
        posts = Post.objects.filter(
            created_datetime__lt=datetime, posted_by=user
        ).order_by("-created_datetime")[:fetch_count]
    else:
        posts = Post.objects.filter(
            Q(created_datetime__lt=datetime),
            Q(posted_by=user),
            Q(is_repost=True, repost__game=game) | Q(is_repost=False, game=game),
        ).order_by("-created_datetime")[:fetch_count]

    posts_data = PostSerializer(posts, many=True, context={"me": request.user}).data
    payload = {"posts": posts_data}
    if username == request.user.username:
        payload["upload"] = is_upload_count_zero(request.user)

    return JsonResponse(
        {"detail": "posts from {}".format(datetime), "payload": payload},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def post_status_view(request):
    post_id = request.data.get("post_id", None)
    if post_id is None:
        return JsonResponse(
            {"detail": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        post = Post.objects.get(pk=post_id, is_repost=False)

        return JsonResponse(
            {
                "detail": "clip status",
                "payload": {"status": post.clip.convert_verified},
            },
            status=status.HTTP_200_OK,
        )
    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "clip status", "payload": {"status": None}},
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([HasAPIKey])
def get_post_view(request):
    post_id = request.data.get("post_id", None)
    if post_id is None:
        return JsonResponse(
            {"detail": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        post = Post.objects.get(id=post_id)
        post_data = PostSerializer(post, context={"me": request.user}).data
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
def update_post_view(request):
    post_id = request.data.get("post_id", None)
    game_id = request.data.get("game_id", None)
    title = request.data.get("title", None)
    tags = request.data.get("tags", None)
    if post_id is None:
        return JsonResponse(
            {"detail": "post_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    if game_id is None and title is None:
        return JsonResponse(
            {"detail": "Post not changed"}, status=status.HTTP_202_ACCEPTED
        )
    if title is None or type(title) != str:
        return JsonResponse(
            {"detail": "title is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    if len(title) > POST_TITLE_LENGTH:
        return JsonResponse(
            {
                "detail": "title has to be less than {} characters".format(
                    POST_TITLE_LENGTH
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    action_approved = get_action_approve(request.user)
    if not action_approved:
        return JsonResponse(
            {"detail": "Too many actions"}, status=status.HTTP_406_NOT_ACCEPTABLE
        )

    try:
        post = Post.objects.get(id=post_id)
        if post.is_repost:
            return JsonResponse(
                {"detail": "Repost cannot be edited"}, status=status.HTTP_403_FORBIDDEN
            )

    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "Post doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    if game_id is not None:
        try:
            game = Game.objects.get(id=game_id)
            post.game = game
        except Game.DoesNotExist:
            return JsonResponse(
                {"detail": "Game doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
            )
    if title is not None:
        post.title = title

    if tags is not None and type(tags) == list:
        if len(tags) > TAGS_MAX_COUNT:
            return JsonResponse(
                {"detail": "You can only add upto {} tags".format(TAGS_MAX_COUNT)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tags_instances = get_users_for_tags(request.user, tags)
        post.tags.set(tags_instances)

    post.save(update_fields=["game", "title"])

    return JsonResponse({"detail": "Post updated!"}, status=status.HTTP_200_OK)


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
        if post.is_repost:
            post = post.repost

    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "Post doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    post.liked_by.add(request.user)
    post.save()
    create_inotif_task.delay(Notification.LIKE, request.user.pk, post.posted_by.pk)
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
        post = Post.objects.get(id=post_id, posted_by=request.user)
    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "Post doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
        )

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
        if post.is_repost:
            post = post.repost
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
    if post.is_repost:
        post.repost.share_count += 1
        post.repost.save(update_fields=["share_count"])
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
        if post.is_repost:
            post = post.repost
    except Post.DoesNotExist:
        return JsonResponse(
            {"detail": "Post doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    report = Report.objects.create(
        reported_by=request.user,
        post=post,
        is_not_playing=is_not_playing,
        is_not_game_clip=is_not_game_clip,
    )
    report.save()
    return JsonResponse({"detail": "report received"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def repost_view(request):
    post_id = request.data.get("post_id", None)
    if post_id is None:
        return JsonResponse(
            {"detail": "post_id required"}, stauts=status.HTTP_400_BAD_REQUEST
        )
    try:
        # Repost only pure posts
        post = Post.objects.get(id=post_id, is_repost=False)
    except Post.DoesNotExist:
        return JsonResponse({"detail": "Post doesn't exist"})

    repost = Post.objects.create(posted_by=request.user, is_repost=True, repost=post)
    repost.save()
    create_inotif_task.delay(Notification.REPOST, request.user.pk, post.posted_by.pk)
    return JsonResponse({"detail": "Reposted!"}, status=status.HTTP_200_OK)
