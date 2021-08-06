from django.test import TestCase

# Create your tests here.
from profiles.twitch import create_subscription
from profiles.models import TwitchProfile
import requests
from decouple import config

TWITCH_CLIENT_ID = config("TWITCH_CLIENT_ID")


def test():
    twitch_profile = TwitchProfile.objects.first()
    create_subscription(twitch_profile=twitch_profile)


def list_subscriptions():
    endpoint = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": "Bearer m23ud4xumy8kdb1xni8vx718vgqcpv",
    }
    response = requests.get(endpoint, headers=headers)
    data = response.json()
    print(data)


def del_subscriptions():
    endpoint = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": "Bearer m23ud4xumy8kdb1xni8vx718vgqcpv",
    }
    response = requests.get(endpoint, headers=headers)
    data = response.json()
    print("BEFORE DELETE", data)
    for subs in response.json()["data"]:
        print("DELETING", subs["id"])
        response_1 = requests.delete(
            endpoint,
            headers=headers,
            data={"id": subs["id"]},
        )
        print(response_1.status_code)
    response = requests.get(endpoint, headers=headers)
    data = response.json()
    print("AFTER DELETE", data)


# from profiles.tests import test, list_subscriptions, del_subscriptions