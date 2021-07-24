import requests
from decouple import config

from profiles.models import TwitchProfile

# TODO generalize the url
TWITCH_CALLBACK_URL = config("API_HOSTNAME") + ":8000/" + "profiles/twitch/callback/"


def _get_tokens(code):
    """Returns access_token, refresh_token for authorization_code."""
    endpoint = "https://id.twitch.tv/oauth2/token"
    payload = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": config("TWITCH_CLIENT_ID"),
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
        "Client-ID": config("TWITCH_CLIENT_ID"),
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


def refresh_access_token(twitch_profile, refresh_token):
    endpoint = "https://id.twitch.tv/oauth2/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": "",
        "client_id": config("TWITCH_CLIENT_ID"),
        "client_secret": config("TWITCH_CLIENT_SECRET"),
    }

    response = requests.post(endpoint, data=payload)
    if response.status_code == 200:
        # TODO Save access_token, refresh_token
        print(response.json())
        pass
    elif response.status_code == 400:
        # TODO Invalid refresh token
        # Remove user's TwitchProfile
        pass
    elif response.status_code == 401:
        # TODO User changed password or disconnected our app
        # Remove user's TwitchProfile
        pass


def validate_access_token(access_token):
    endpoint = "https://api.twitch.tv/oauth2/validate"
    headers = {
        "Authorization": "Bearer {}".format(access_token),
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return True
    else:
        access_token = refresh_access_token()
        return False


def create_subscription(user_id):
    if user_id is None:
        return

    # TODO validate token first
    try:
        access_token = validate_access_token()

        # Send a post request to TWITCH API
        endpoint = "https://api.twitch.tv/helix/eventsub/subscriptions"
        headers = {
            "Client-ID": config("TWITCH_CLIENT_ID"),
        }
        payload = [
            {
                "type": "stream.online",
                "version": "1",
                "condition": {"broadcaster_user_id": user_id},
                "transport": {
                    "method": "webhook",
                    "callback": TWITCH_CALLBACK_URL,
                    "secret": "",  # TODO secret
                },
            }
        ]
        response = requests.post(endpoint, headers=headers, data=payload)
        if response.status_code == 200:
            # Twitch sends a response to callback
            return
        else:
            return

    except TwitchProfile.DoesNotExist:
        return
