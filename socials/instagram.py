import requests
import rollbar
import os


INSTAGRAM_CLIENT_ID = os.environ["INSTAGRAM_CLIENT_ID"]
INSTAGRAM_CLIENT_SECRET = os.environ["INSTAGRAM_CLIENT_SECRET"]
OAUTH_REDIRECT_URI = os.environ["OAUTH_REDIRECT_URI"]


def _get_user_info(access_token=None, user_id=None):
    if access_token is None or user_id is None:
        return None

    api_version = "v11.0"
    endpoint = "https://graph.instagram.com/{}/{}?fields=account_type,id,username&access_token={}".format(
        api_version, user_id, access_token
    )

    response = requests.get(endpoint)
    if response.ok:
        data = response.json()
        return data
    else:
        return None


def get_user_info(authorization_code):
    if authorization_code is None:
        return None

    endpoint = "https://api.instagram.com/oauth/access_token"
    payload = {
        "client_id": INSTAGRAM_CLIENT_ID,
        "client_secret": INSTAGRAM_CLIENT_SECRET,
        "code": authorization_code,
        "grant_type": "authorization_code",
        "redirect_uri": OAUTH_REDIRECT_URI,
    }

    response = requests.post(endpoint, data=payload)
    if response.ok:
        data = response.json()
        # data
        # {
        #     "access_token": "IGQVJYRnZAoMXl2TTJ2UlhhY2xacEdheUZAscFAtck1KTFFMSVZAZAN19YVC1jNTltWjdJTjZAwRmphdElpOUl3aUFKQTZAHZAFpjNFVwTVFSeW96NU9mRUM2V1RhYng4UUF0NDJuNVIxTGpNaTkyaVoxOHpFXzJoNmNJamlNMXlV",
        #     "user_id": 17841412566615195,
        # }
        return _get_user_info(data["access_token"], data["user_id"])
    else:
        rollbar.report_exc_info(
            extra_data={
                "type": "instagram_connect",
                "detail": "Encountered some Instagram Request Error.",
                "endpoint": endpoint,
            }
        )
        return None
