import rollbar
import requests
import os
from time import sleep

from ratelimit import limits, sleep_and_retry


RIOT_API_KEY = os.environ["RIOT_API_KEY"]
RIOT_LOL_RATE_LIMIT_1 = int(os.environ["RIOT_LOL_RATE_LIMIT_1"])
RIOT_LOL_RATE_PERIOD_1 = int(os.environ["RIOT_LOL_RATE_PERIOD_1"])
RIOT_LOL_RATE_LIMIT_2 = int(os.environ["RIOT_LOL_RATE_LIMIT_2"])
RIOT_LOL_RATE_PERIOD_2 = int(os.environ["RIOT_LOL_RATE_PERIOD_2"])

# FOR RIOT ACCOUNT
# AMERICAS 	americas.api.riotgames.com
# ASIA 	asia.api.riotgames.com
# EUROPE 	europe.api.riotgames.com

# FOR LOL DATA
# BR1 	br1.api.riotgames.com
# EUN1 	eun1.api.riotgames.com
# EUW1 	euw1.api.riotgames.com
# JP1 	jp1.api.riotgames.com
# KR 	kr.api.riotgames.com
# LA1 	la1.api.riotgames.com
# LA2 	la2.api.riotgames.com
# NA1 	na1.api.riotgames.com
# OC1 	oc1.api.riotgames.com
# TR1 	tr1.api.riotgames.com
# RU 	ru.api.riotgames.com


def platform_url(platform: str = None):
    if platform is None:
        raise ValueError("'platform' can't be None")
    platform = platform.lower()
    if platform not in [
        "br1",
        "eun1",
        "euw1",
        "jp1",
        "kr",
        "la1",
        "la2",
        "na1",
        "oc1",
        "tr1",
        "ru",
    ]:
        raise ValueError("invalid platform")
    return "https://{}.api.riotgames.com".format(platform)


def region_url(platform: str = None):
    platform = platform.lower()
    region = None
    if platform in ["na1", "br1", "la1", "la2", "oc1"]:
        # NA, BR, LAN, LAS, and OCE
        region = "americas"
    elif platform in ["kr", "jp"]:
        # KR and JP
        region = "asia"
    elif platform in ["eun1", "euw1", "tr1", "ru"]:
        # EUNE, EUW, TR, and RU
        region = "europe"

    if region is None:
        raise ValueError("invalid platform")
    return "https://{}.api.riotgames.com".format(region)


@sleep_and_retry
@limits(calls=int(RIOT_LOL_RATE_LIMIT_1), period=RIOT_LOL_RATE_PERIOD_1)
@sleep_and_retry
@limits(calls=int(RIOT_LOL_RATE_LIMIT_2), period=RIOT_LOL_RATE_PERIOD_2)
def lol_wrapper(endpoint, max_tries=10):
    for i in range(max_tries):
        headers = {"X-Riot-Token": RIOT_API_KEY}
        response = requests.get(endpoint, headers=headers)

        if response.ok:
            return response.json()

        else:
            if response.status_code == 429:
                sleep(float(response.headers["Retry-After"]))
                continue
            elif response.status_code >= 500:
                return None
            else:
                rollbar.report_exc_info(
                    extra_data={
                        "type": "riot_response",
                        "detail": "Encountered some Riot League of Legends Response Error.",
                        "status_code": response.status_code,
                        "endpoint": endpoint,
                    }
                )
                return None
    return None


def get_summoner(
    puuid: str = None, summoner_id: str = None, name: str = None, platform: str = None
):
    endpoint = None
    if puuid is not None:
        endpoint = "/lol/summoner/v4/summoners/by-puuid/{}".format(puuid)
    elif summoner_id is not None:
        endpoint = "/lol/summoner/v4/summoners/{}".format(summoner_id)
    elif name is not None:
        endpoint = "/lol/summoner/v4/summoners/by-name/{}".format(name)

    if endpoint is None:
        raise ValueError("'puuid', 'summoner_id', 'name'; all can't be 'None'")

    endpoint = "{}{}".format(platform_url(platform=platform), endpoint)

    json_response = lol_wrapper(endpoint=endpoint)

    return json_response


def get_matchlist_v5(
    puuid: str = None, start_index: int = None, count: int = None, platform: str = None
):
    if puuid is None:
        raise ValueError("'puuid' can't be 'None'")

    if start_index == None:
        raise ValueError("'start_index' required")

    if start_index < 0 or count < 0 or count > 100:
        raise ValueError("Bad indices")

    endpoint = "{}/lol/match/v5/matches/by-puuid/{}/ids?start={}&count={}".format(
        region_url(platform=platform), puuid, start_index, count
    )

    return lol_wrapper(endpoint=endpoint)


def get_match_v5(match_id=None, platform: str = None):
    if match_id is None:
        raise ValueError("'match_id' can't be None")

    endpoint = "{}/lol/match/v5/matches/{}".format(
        region_url(platform=platform), match_id
    )
    return lol_wrapper(endpoint=endpoint)


def get_champion_masteries(summoner_id: str = None, platform: str = None):
    if summoner_id is None:
        raise ValueError("'summoner_id' can't be 'None'")

    endpoint = "{}/lol/champion-mastery/v4/champion-masteries/by-summoner/{}".format(
        platform_url(platform=platform), summoner_id
    )

    return lol_wrapper(endpoint=endpoint)
