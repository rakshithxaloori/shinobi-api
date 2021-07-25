from os import access
import requests
from hashlib import sha256
from decouple import config

from profiles.models import TwitchProfile

# TODO generalize the url
TWITCH_CALLBACK_URL = config("API_HOSTNAME") + ":8000/" + "profiles/twitch/callback/"
TWITCH_CLIENT_ID = config("TWITCH_CLIENT_ID")


def _get_tokens(code):
    """Returns access_token, refresh_token for authorization_code."""
    endpoint = "https://id.twitch.tv/oauth2/token"
    payload = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": config("TWITCH_CLIENT_SECRET"),
        # TODO generalize the redirect_uri
        "redirect_uri": "https://auth.expo.io/@rakshith.aloori/ProeliumX",
    }
    response = requests.post(endpoint, data=payload)
    # print(response.json())
    # {
    #     "access_token": "t08pbgg1mnjl9h4zw5xdcq28s9mpb9",
    #     "expires_in": 13950,
    #     "refresh_token": "n6m54e85glbtg3bss759mnfwmgv8uxjpgsitbxjlerokqt01vd",
    #     "scope": ["user_read"],
    #     "token_type": "bearer",
    # }
    if response.status_code == 200:
        response_data = response.json()
        return response_data["access_token"], response_data["refresh_token"]

    elif response.status_code >= 400:
        # TODO handle
        return None, None


def get_user_info(code=None):
    if code is None:
        return None

    access_token, refresh_token = _get_tokens(code=code)
    if access_token is None:
        return None

    endpoint = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Client-ID": TWITCH_CLIENT_ID,
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
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

        user_data = response.json()["data"][0]
        user_data["access_token"] = access_token
        user_data["refresh_token"] = refresh_token
        return user_data

    return None


def refresh_access_token(access_token):
    try:
        twitch_profile = TwitchProfile.objects.get(access_token=access_token)
        endpoint = "https://id.twitch.tv/oauth2/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": twitch_profile.refresh_token,
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": config("TWITCH_CLIENT_SECRET"),
        }

        response = requests.post(endpoint, data=payload)
        if response.status_code == 200:
            # Save access_token, refresh_token
            response_data = response.json()
            # print(response.json())
            # {
            #     "access_token": "01dn8sp75thb6zgjkee77y7tkiap6p",
            #     "expires_in": 15541,
            #     "refresh_token": "9yl7m1t90npy33laonvkz6gjxndkkdrvolrn83zlx7g5hmuz1a",
            #     "scope": ["user_read"],
            #     "token_type": "bearer",
            # }
            twitch_profile.access_token = response_data["access_token"]
            twitch_profile.refresh_token = response_data["refresh_token"]
            twitch_profile.save(update_fields=["access_token", "refresh_token"])
        elif response.status_code == 400 or response.status_code == 401:
            # Invalid refresh token or User changed password or disconnected our app
            twitch_profile.is_active = False
            twitch_profile.save(update_fields=["is_active"])
    except TwitchProfile.DoesNotExist:
        # Just as a safety net. This is already handled in callback view
        return


def validate_access_token(access_token):
    endpoint = "https://api.twitch.tv/oauth2/validate"
    headers = {
        "Authorization": "OAuth {}".format(access_token),
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code != 200:
        refresh_access_token(access_token)


def create_subscription(twitch_profile=None):
    if twitch_profile is None:
        return

    try:
        validate_access_token(twitch_profile.access_token)
    except Exception as e:
        print(e)
        return

    if not twitch_profile.is_active:
        return

    # Send a post request to TWITCH API
    endpoint = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
    }
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
    response = requests.post(endpoint, headers=headers, data=payload)
    if response.status_code == 200:
        # Twitch sends a response to the callback
        return


def verify_signature(headers, request_body, webhook_secret):
    hmac_message = (
        headers["Twitch-Eventsub-Message-Id"]
        + headers["Twitch-Eventsub-Message-Timestamp"]
        + request_body
    )
    signature = sha256(webhook_secret, hmac_message)
    expected_signature_header = "sha256=" + signature.hexdigest()

    if headers["Twitch-Eventsub-Message-Signature"] != expected_signature_header:
        print("TWITCH SIGNATURE DOESN'T MATCH")
        return 403
    else:
        return 200


def get_stream_data():
    # Validate access token
    # validate_access_token(access_token=access_token)
    pass


def revoke_access_token(access_token=None):
    if access_token is None:
        return

    endpoint = "https://id.twitch.tv/oauth2/revoke"
    payload = {"cliend_id": TWITCH_CLIENT_ID, "token": access_token}
    requests.post(endpoint, data=payload)
