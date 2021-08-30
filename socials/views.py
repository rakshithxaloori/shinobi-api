from django.http import JsonResponse, HttpResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework_api_key.permissions import HasAPIKey

from knox.auth import TokenAuthentication


from socials.models import TwitchProfile, TwitchStream, YouTubeProfile

from profiles import tasks as p_tasks
from socials import twitch_tasks
from socials import youtube


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
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
        user_info = twitch_tasks.get_user_info(access_token=access_token)
        if user_info is None:
            return JsonResponse(
                {"detail": "Invalid access_token"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            twitch_profile = TwitchProfile.objects.get(
                user_id=user_info.get("id", None)
            )
            return JsonResponse(
                {"detail": "This Twitch is already connected to other account"},
                status=status.HTTP_208_ALREADY_REPORTED,
            )
        except TwitchProfile.DoesNotExist:
            twitch_profile = TwitchProfile.objects.create(
                profile=request.user.profile,
                user_id=user_info.get("id", None),
                login=user_info.get("login", None),
                display_name=user_info.get("display_name", None),
                view_count=user_info.get("view_count", None),
            )
            twitch_profile.save()

            # Adds the picture if there was None or "" before
            p_tasks.add_profile_picture.delay(
                request.user.pk, user_info.get("profile_image_url", None)
            )

            return JsonResponse(
                {"detail": "Twitch connected!"}, status=status.HTTP_200_OK
            )
    except Exception as e:
        print(e)
        return JsonResponse(
            {"detail": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
def twitch_callback_view(request):
    # Handle callback based on callback_data["subscription"]["status"]
    request_body = request.body
    callback_data = request.data
    print(callback_data)

    callback_status = callback_data["subscription"]["status"]
    try:
        twitch_profile = TwitchProfile.objects.get(
            user_id=callback_data["subscription"]["condition"]["broadcaster_user_id"]
        )
        if (
            twitch_tasks.verify_signature(
                headers=request.headers,
                request_body=request_body,
                webhook_secret=twitch_profile.secret,
            )
            != 200
        ):
            # Signature doesn't match
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        if callback_status == "enabled":
            if callback_data["subscription"]["type"] == "stream.online":
                twitch_tasks.stream_online.delay(twitch_profile_pk=twitch_profile.pk)

            elif callback_data["subscription"]["type"] == "stream.offline":
                try:
                    twitch_stream = twitch_profile.twitch_stream
                    twitch_stream.title = ""
                    twitch_stream.is_streaming = False
                    twitch_stream.save(update_fields=["title", "is_streaming"])
                except TwitchStream.DoesNotExist:
                    pass

            return HttpResponse(status=status.HTTP_200_OK)

        elif callback_status == "webhook_callback_verification_pending":
            if callback_data["subscription"]["type"] == "stream.online":
                twitch_profile.stream_online_subscription_id = callback_data[
                    "subscription"
                ]["id"]
            elif callback_data["subscription"]["type"] == "stream.offline":
                twitch_profile.stream_offline_subscription_id = callback_data[
                    "subscription"
                ]["id"]
            twitch_profile.save(
                update_fields=[
                    "stream_online_subscription_id",
                    "stream_offline_subscription_id",
                ]
            )
            return HttpResponse(callback_data["challenge"], status=status.HTTP_200_OK)

        elif callback_status == "webhook_callback_verification_failed":
            return HttpResponse(status=status.HTTP_200_OK)

        elif callback_status == "notification_failures_exceeded":
            return HttpResponse(status=status.HTTP_200_OK)

        elif callback_status == "authorization_revoked":
            twitch_profile.is_active = False
            twitch_profile.save(update_fields=["is_active"])
            return HttpResponse(status=status.HTTP_200_OK)

        elif callback_status == "user_removed":
            try:
                twitch_profile.twitch_stream.delete()
            except TwitchStream.DoesNotExist:
                pass
            twitch_profile.delete()
            return HttpResponse(status=status.HTTP_200_OK)

    except TwitchProfile.DoesNotExist:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
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

        else:
            # Create YouTubeProfile model with channel_id
            yt_channel = yt_channels[0]

            image_url = yt_channel["snippet"]["thumbnails"].get("medium", None)
            if image_url is None:
                image_url = yt_channel["snippet"]["thumbnails"]["default"]
            image_url = image_url["url"]
            new_youtube_profile = YouTubeProfile.objects.create(
                profile=request.user.profile,
                channel_id=yt_channel["id"],
                channel_image_url=image_url,
            )
            new_youtube_profile.save()
            return JsonResponse(
                {"detail": "YouTube connected!"}, status=status.HTTP_200_OK
            )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
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


# if callback_data["subscription"]["type"] == "stream.online":
#     print(callback_data)
#     {
#         "subscription": {
#             "id": "67c6024c-dba3-45f3-ad95-fefe5b2773a1",
#             "status": "enabled",
#             "type": "stream.online",
#             "version": "1",
#             "condition": {"broadcaster_user_id": "655414459"},
#             "transport": {
#                 "method": "webhook",
#                 "callback": "https://d8985f17ea05.ngrok.io/profile/twitch/callback/",
#             },
#             "created_at": "2021-07-26T08:38:49.748425134Z",
#             "cost": 0,
#         },
#         "event": {
#             "id": "39715133707",
#             "broadcaster_user_id": "655414459",
#             "broadcaster_user_login": "uchiha_leo_06",
#             "broadcaster_user_name": "uchiha_leo_06",
#             "type": "live",
#             "started_at": "2021-07-26T09:35:36Z",
#         },
#     }

# elif callback_data["subscription"]["type"] == "stream.offline":
#     print(callback_data)
#     {
#         "subscription": {
#             "id": "593ef4b1-d6ba-46fc-a41c-d39b7d543a78",
#             "status": "enabled",
#             "type": "stream.offline",
#             "version": "1",
#             "condition": {"broadcaster_user_id": "655414459"},
#             "transport": {
#                 "method": "webhook",
#                 "callback": "https://d8985f17ea05.ngrok.io/profile/twitch/callback/",
#             },
#             "created_at": "2021-07-26T08:38:50.240681852Z",
#             "cost": 0,
#         },
#         "event": {
#             "broadcaster_user_id": "655414459",
#             "broadcaster_user_login": "uchiha_leo_06",
#             "broadcaster_user_name": "uchiha_leo_06",
#         },
#     }
