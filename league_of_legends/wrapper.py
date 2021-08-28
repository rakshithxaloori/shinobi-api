import requests
from decouple import config

from league_of_legends.utils import retry_with_backoff_decorator

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
NEAREST_REGION_ROUTE = "na1.api.riotgames.com"
BASE_API_URL = "https://{}".format(NEAREST_REGION_ROUTE)

# URLs, maybe use these in serializers?
profile_icon = "http://ddragon.leagueoflegends.com/cdn/11.16.1/img/profileicon/{}.png"  # profileIconId


@retry_with_backoff_decorator()
def lol_wrapper(endpoint):
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(endpoint, headers=headers)

    if response.ok:
        return response.json()

    else:
        if response.status_code == 429:
            raise Exception("RETRY WITH BACKOFF")
        else:
            return None


def get_summoner(
    puuid: str = None, account_id: str = None, summoner_id: str = None, name: str = None
):
    endpoint = None
    if puuid is not None:
        endpoint = "/lol/summoner/v4/summoners/by-puuid/{}".format(puuid)
    elif account_id is not None:
        endpoint = "/lol/summoner/v4/summoners/by-account/{}".format(account_id)
    elif summoner_id is not None:
        endpoint = "/lol/summoner/v4/summoners/{}".format(summoner_id)
    elif name is not None:
        endpoint = "/lol/summoner/v4/summoners/by-name/{}".format(name)

    if endpoint is None:
        raise ValueError("puuid, account_id, summoner_id, name; all can't be 'None'")

    endpoint = "{}{}".format(BASE_API_URL, endpoint)

    json_response = lol_wrapper(endpoint=endpoint)

    return json_response


def get_matchlist(
    account_id: str = None, begin_index: int = None, end_index: int = None
):
    if account_id is None:
        raise ValueError("account_id can't be 'None'")

    if begin_index == None or end_index == None:
        raise ValueError("begin_index, end_index required")

    if begin_index < 0 or begin_index > end_index or end_index - begin_index > 100:
        raise ValueError("Bad indices")

    endpoint = (
        "{}/lol/match/v4/matchlists/by-account/{}?beginIndex={}&endIndex={}".format(
            BASE_API_URL, account_id, begin_index, end_index
        )
    )

    return lol_wrapper(endpoint=endpoint)


def get_match(match_id=None):
    if match_id is None:
        raise ValueError("match_id can't be 'None'")

    endpoint = "{}/lol/match/v4/matches/{}".format(BASE_API_URL, match_id)

    match = lol_wrapper(endpoint=endpoint)
    if match is not None:
        # Combine participants, participantIdentities
        for p in match["participants"]:
            for pi in match["participantIdentities"]:
                if p["participantId"] == pi["participantId"]:
                    p["player"] = pi["player"]
                    break

        match.pop("participantIdentities")
    return match


def get_champion_masteries(summoner_id: str = None):
    if summoner_id is None:
        raise ValueError("account_id can't be 'None'")

    endpoint = "{}/lol/champion-mastery/v4/champion-masteries/by-summoner/{}".format(
        BASE_API_URL, summoner_id
    )

    return lol_wrapper(endpoint=endpoint)
