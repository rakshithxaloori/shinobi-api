import hmac
import requests
from hashlib import sha256
from decouple import config
from celery import shared_task

from django.core.cache import cache

from socials.models import TwitchProfile, TwitchStream
from profiles.models import Game


TWITCH_CLIENT_ID = config("TWITCH_CLIENT_ID")


# User token or access_token for the topics that require a scope
# App access token for public data like streams/follows


def get_user_info(access_token=None):
    if access_token is None:
        return None

    endpoint = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Client-ID": TWITCH_CLIENT_ID,
    }
    response = requests.get(endpoint, headers=headers)
    if response.ok:
        user_data = response.json()["data"][0]
        return user_data

    return None


def validate_app_access_token(app_access_token):
    endpoint = "https://id.twitch.tv/oauth2/validate"
    headers = {"Authorization": "OAuth {}".format(app_access_token)}
    response = requests.get(endpoint, headers=headers)
    return response.ok


def get_app_access_token():
    app_access_token = cache.get("twitch_app_access_token")

    if app_access_token is None or not validate_app_access_token(app_access_token):
        # Fetch new app access token
        endpoint = "https://id.twitch.tv/oauth2/token"
        payload = {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": config("TWITCH_CLIENT_SECRET"),
            "grant_type": "client_credentials",
            "scope": ["user_read"],
        }
        response = requests.post(endpoint, data=payload)
        if response.ok:
            app_access_token = response.json()["access_token"]
            cache.set("twitch_app_access_token", app_access_token, timeout=86400)
            return app_access_token
        else:
            return None

    else:
        # Reuse old token
        return app_access_token


@shared_task
def create_subscription(twitch_profile_pk=None):
    if twitch_profile_pk is None:
        return

    try:
        twitch_profile = TwitchProfile.objects.get(pk=twitch_profile_pk)
    except TwitchProfile.DoesNotExist:
        return

    app_access_token = get_app_access_token()
    if app_access_token is None:
        twitch_profile.is_active = False
        twitch_profile.save(update_fields=["is_active"])

    # Send a post request to TWITCH API
    endpoint = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": "Bearer {}".format(app_access_token),
        "Content-Type": "application/json",
    }
    TWITCH_CALLBACK_URL = "https://{}/socials/twitch/callback/".format(
        config("API_HOSTNAME")
    )
    payload = [
        {
            "type": "stream.online",
            "version": "1",
            "condition": {"broadcaster_user_id": twitch_profile.user_id},
            "transport": {
                "method": "webhook",
                "callback": TWITCH_CALLBACK_URL,
                "secret": twitch_profile.secret,
            },
        },
        {
            "type": "stream.offline",
            "version": "1",
            "condition": {"broadcaster_user_id": twitch_profile.user_id},
            "transport": {
                "method": "webhook",
                "callback": TWITCH_CALLBACK_URL,
                "secret": twitch_profile.secret,
            },
        },
    ]
    response_1 = requests.post(endpoint, headers=headers, json=payload[0])
    response_2 = requests.post(endpoint, headers=headers, json=payload[1])

    if response_1.ok and response_2.ok:
        # Twitch sends a response to the callback
        return


@shared_task
def delete_subscription(
    stream_online_subscription_id=None, stream_offline_subscription_id=None
):
    app_access_token = get_app_access_token()
    if app_access_token is None:
        return
    endpoint = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": "Bearer {}".format(app_access_token),
    }
    response_1 = requests.delete(
        endpoint,
        headers=headers,
        data={"id": stream_online_subscription_id},
    )
    response_2 = requests.delete(
        endpoint,
        headers=headers,
        data={"id": stream_offline_subscription_id},
    )


def verify_signature(headers, request_body, webhook_secret):
    hmac_message = (
        headers["Twitch-Eventsub-Message-Id"]
        + headers["Twitch-Eventsub-Message-Timestamp"]
        + request_body.decode("UTF-8")
    )
    signature = hmac.new(
        webhook_secret.encode("UTF-8"), hmac_message.encode("UTF-8"), sha256
    )

    expected_signature_header = "sha256=" + signature.hexdigest()

    if headers["Twitch-Eventsub-Message-Signature"] != expected_signature_header:
        return 403
    else:
        return 200


def get_stream_data(twitch_user_id):
    app_access_token = get_app_access_token()
    if app_access_token is None:
        return None
    endpoint = "https://api.twitch.tv/helix/streams?user_id={}".format(twitch_user_id)
    headers = {
        "Authorization": "Bearer {}".format(app_access_token),
        "Client-ID": TWITCH_CLIENT_ID,
    }
    response = requests.get(endpoint, headers=headers)
    stream_data = response.json()["data"]
    if len(stream_data) == 1:
        return stream_data[0]
    else:
        return None


@shared_task
def stream_online(twitch_profile_pk=None):
    if twitch_profile_pk is None:
        return

    try:
        twitch_profile = TwitchProfile.objects.get(pk=twitch_profile_pk)
    except TwitchProfile.DoesNotExist:
        return
    stream_data = get_stream_data(twitch_user_id=twitch_profile.user_id)
    print(stream_data)
    if stream_data is not None:
        # Check if the game is valid
        try:
            # Only save streams whose games are in db
            game = Game.objects.get(id=stream_data["game_id"])
            try:
                # Rewrite the old stream
                twitch_stream = twitch_profile.twitch_stream
                twitch_stream.stream_id = stream_data["id"]
                twitch_stream.game = game
                twitch_stream.title = stream_data["title"]
                twitch_stream.thumbnail_url = stream_data["thumbnail_url"]
                twitch_stream.is_streaming = True
                twitch_stream.save()
            except TwitchStream.DoesNotExist:
                # Create TwitchStream instance
                twitch_stream = TwitchStream.objects.create(
                    stream_id=stream_data["id"],
                    twitch_profile=twitch_profile,
                    game=game,
                    title=stream_data["title"],
                    thumbnail_url=stream_data["thumbnail_url"],
                )
                twitch_stream.save()
        except Game.DoesNotExist:
            return


# get_user_info
# print(response.json())
# {
#     "data": [
#         {
#             "id": "655414459",
#             "login": "uchiha_leo_06",
#             "display_name": "uchiha_leo_06",
#             "type": "",
#             "broadcaster_type": "",
#             "description": "",
#             "profile_image_url": "https://static-cdn.jtvnw.net/user-default-pictures-uv/ebb84563-db81-4b9c-8940-64ed33ccfc7b-profile_image-300x300.png",
#             "offline_image_url": "",
#             "view_count": 0,
#             "email": "uchiha.leo.06@gmail.com",
#             "created_at": "2021-02-26T17:03:02.556887Z",
#         }
#     ]
# }

# get_app_access_token
# print(response.json())
# {
#     "access_token": "m23ud4xumy8kdb1xni8vx718vgqcpv",
#     "expires_in": 4701749,
#     "scope": ["user_read"],
#     "token_type": "bearer",
# }

# get_stream_data
# print(response.json())
# {
#     "data": [
#         {
#             "id": "39715239339",
#             "user_id": "655414459",
#             "user_login": "uchiha_leo_06",
#             "user_name": "uchiha_leo_06",
#             "game_id": "509658",
#             "game_name": "Just Chatting",
#             "type": "live",
#             "title": "Test",
#             "viewer_count": 0,
#             "started_at": "2021-07-26T10:21:54Z",
#             "language": "en",
#             "thumbnail_url": "https://static-cdn.jtvnw.net/previews-ttv/live_user_uchiha_leo_06-{width}x{height}.jpg",
#             "tag_ids": ["6ea6bca4-4712-4ab9-a906-e3336a9d8039"],
#             "is_mature": False,
#         }
#     ],
#     "pagination": {},
# }
# {'data': [], 'pagination': {}}
