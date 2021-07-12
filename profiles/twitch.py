import requests
from decouple import config


def get_user_info(access_token=None):
    if access_token is None:
        return None

    endpoint = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Client-ID": config("TWITCH_CLIENT_ID"),
    }
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()["data"][0]
    else:
        return None
