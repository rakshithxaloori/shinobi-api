from os import access
import requests
import hmac
from hashlib import sha256
from decouple import config


# TODO generalize the url
TWITCH_CALLBACK_URL = "https://cf3c1db1d2bc.ngrok.io/" + "profile/twitch/callback/"
TWITCH_CLIENT_ID = config("TWITCH_CLIENT_ID")


# User token or access_token for the topics that require a scope
# App access token for public data like streams/follows


def get_user_info(access_token=None):
    print("TWITCH GETTING USER INFO")
    if access_token is None:
        return None

    endpoint = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Client-ID": TWITCH_CLIENT_ID,
    }
    response = requests.get(endpoint, headers=headers)
    if response.ok:
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
        return user_data

    return None


def validate_app_access_token():
    endpoint = "https://id.twitch.tv/oauth2/validate"
    headers = {"Authorization": "OAuth {}".format()}
    response = requests.get(endpoint, headers=headers)
    return response.ok


def get_app_access_token():
    return "m23ud4xumy8kdb1xni8vx718vgqcpv"
    if validate_app_access_token():
        return ""
    else:
        endpoint = "https://id.twitch.tv/oauth2/token"
        payload = {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": config("TWITCH_CLIENT_SECRET"),
            "grant_type": "client_credentials",
            "scope": ["user_read"],
        }
        response = requests.post(endpoint, data=payload)
        # print(response.json())
        # {
        #     "access_token": "m23ud4xumy8kdb1xni8vx718vgqcpv",
        #     "expires_in": 4701749,
        #     "scope": ["user_read"],
        #     "token_type": "bearer",
        # }
        if response.ok:
            return response.json()["access_token"]
        else:
            return None


def create_subscription(twitch_profile=None):
    print("TWITCH CREATING SUBSCRIPTION")
    if twitch_profile is None:
        return

    # Create or reuse
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

    print(response_1.json())
    print(response_2.json())
    if response_1.ok and response_2.ok:
        # Twitch sends a response to the callback
        return


def delete_subscription(twitch_profile=None):
    print("TWITCH DELETING SUBSCRIPTION")
    if twitch_profile is None:
        return

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
        data={"id": twitch_profile.stream_online_subscription_id},
    )
    response_2 = requests.delete(
        endpoint,
        headers=headers,
        data={"id": twitch_profile.stream_offline_subscription_id},
    )

    if response_1.ok:
        twitch_profile.stream_online_subscription_id = None
    if response_2.ok:
        twitch_profile.stream_offline_subscription_id = None
    twitch_profile.save(
        update_fields=[
            "stream_online_subscription_id",
            "stream_offline_subscription_id",
        ]
    )


def verify_signature(headers, request_body, webhook_secret):
    print("VERIFYING SIGNATURE")
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
        print("TWITCH SIGNATURE DOESN'T MATCH")
        print("EXPECTED", expected_signature_header)
        print("RECEIVED", headers["Twitch-Eventsub-Message-Signature"])
        return 403
    else:
        print("TWITCH SIGNATURES MATCH")
        return 200


def get_stream_data():
    # Validate access token
    # validate_access_token(access_token=access_token)
    pass
