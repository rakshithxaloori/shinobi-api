import requests
from os import cpu_count
from decouple import config
from ratelimit import limits, sleep_and_retry


RIOT_API_KEY = config("RIOT_API_KEY")

# FOR RIOT ACCOUNT
# AMERICAS 	americas.api.riotgames.com
# ASIA 	asia.api.riotgames.com
# EUROPE 	europe.api.riotgames.com

# FOR LOL
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

# TODO nearest region route
NEAREST_PLATFORM_ROUTE = "na1.api.riotgames.com"
PLATFORM_API_URL = "https://{}".format(NEAREST_PLATFORM_ROUTE)

NEAREST_REGION_ROUTE = "americas.api.riotgames.com"
REGION_API_URL = "https://{}".format(NEAREST_REGION_ROUTE)

# URLs, maybe use these in serializers?
profile_icon = "http://ddragon.leagueoflegends.com/cdn/11.17.1/img/profileicon/{}.png"  # profileIconId


# TODO is there a better way to pipe requests
# instead of limitting #requests in each cpu,
# so max won't exceed total limit
@sleep_and_retry
@limits(calls=int(15 / cpu_count()), period=1)
@sleep_and_retry
@limits(calls=int(80 / cpu_count()), period=120)
def lol_wrapper(endpoint):
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(endpoint, headers=headers)

    if response.ok:
        return response.json()

    else:
        if response.status_code == 429:
            print(response.headers)
            raise Exception("RETRY WITH BACKOFF {}".format(response.status_code))
        elif response.status_code >= 500:
            raise Exception("RIOT SERVER ERROR {}".format(response.status_code))
        else:
            print("RIOT RESPONSE ERROR {}".format(response.status_code))
            # TODO sent this to someone
            return None


def get_summoner(puuid: str = None, summoner_id: str = None, name: str = None):
    endpoint = None
    if puuid is not None:
        endpoint = "/lol/summoner/v4/summoners/by-puuid/{}".format(puuid)
    elif summoner_id is not None:
        endpoint = "/lol/summoner/v4/summoners/{}".format(summoner_id)
    elif name is not None:
        endpoint = "/lol/summoner/v4/summoners/by-name/{}".format(name)

    if endpoint is None:
        raise ValueError("puuid, summoner_id, name; all can't be 'None'")

    endpoint = "{}{}".format(PLATFORM_API_URL, endpoint)

    json_response = lol_wrapper(endpoint=endpoint)

    return json_response


def get_matchlist_v5(puuid: str = None, start_index: int = None, count: int = None):
    if puuid is None:
        raise ValueError("puuid can't be 'None'")

    if start_index == None:
        raise ValueError("start_index required")

    if start_index < 0 or count < 0 or count > 100:
        raise ValueError("Bad indices")

    endpoint = "{}/lol/match/v5/matches/by-puuid/{}/ids?start={}&count={}".format(
        REGION_API_URL, puuid, start_index, count
    )

    return lol_wrapper(endpoint=endpoint)


def get_match_v5(match_id=None):
    if match_id is None:
        raise ValueError("match_id can't be None")

    endpoint = "{}/lol/match/v5/matches/{}".format(REGION_API_URL, match_id)
    return lol_wrapper(endpoint=endpoint)


def get_champion_masteries(summoner_id: str = None):
    if summoner_id is None:
        raise ValueError("summoner_id can't be 'None'")

    endpoint = "{}/lol/champion-mastery/v4/champion-masteries/by-summoner/{}".format(
        PLATFORM_API_URL, summoner_id
    )

    return lol_wrapper(endpoint=endpoint)
