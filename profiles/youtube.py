import requests


def get_user_info(access_token=None):
    if access_token is None:
        return None

    endpoint = (
        "https://youtube.googleapis.com/youtube/v3/channels?part=snippet&mine=true"
    )
    headers = {
        "Authorization": "Bearer {}".format(access_token),
    }
    response = requests.get(endpoint, headers=headers)
    if response.ok:
        return response.json()
    else:
        return None
