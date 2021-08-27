import random, time, json
import urllib.request

from django.core.cache import cache


def retry_with_backoff_decorator(retries=100, backoff_in_seconds=1):
    def rwb(f):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return f(*args, **kwargs)
                except:
                    if x == retries:
                        raise
                    else:
                        sleep = backoff_in_seconds * 2 ** x + random.uniform(0, 1)
                        print("EXPONENTIAL BACKOFF", sleep)
                        time.sleep(sleep)
                        x += 1

        return wrapper

    return rwb


def save_champions_list_cache():
    with urllib.request.urlopen(
        "https://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/champion.json"
    ) as url:
        champions_data = json.loads(url.read().decode())
        champions_list = list(champions_data["data"].values())
        cache.set("lol_champions_list", champions_list, timeout=None)
        return champions_list


def get_champions_list_cache():
    champions_list = cache.get("lol_champions_list")
    if champions_list is None:
        return save_champions_list_cache()
    else:
        return champions_list


def get_champion_full(champion_key):
    for champion in get_champions_list_cache():
        # 'Zyra': {'blurb': 'Born in an ancient, sorcerous catastrophe, Zyra is the '
        #            'wrath of nature given form—an alluring hybrid of plant and '
        #            'human, kindling new life with every step. She views the '
        #            'many mortals of Valoran as little more than prey for her '
        #            'seeded progeny, and thinks...',
        #   'id': 'Zyra',
        #   'image': {'full': 'Zyra.png',
        #             'group': 'champion',
        #             'h': 48,
        #             'sprite': 'champion5.png',
        #             'w': 48,
        #             'x': 240,
        #             'y': 0},
        #   'info': {'attack': 4, 'defense': 3, 'difficulty': 7, 'magic': 8},
        #   'key': '143',
        #   'name': 'Zyra',
        #   'partype': 'Mana',
        #   'stats': {'armor': 29,
        #             'armorperlevel': 3,
        #             'attackdamage': 53,
        #             'attackdamageperlevel': 3.2,
        #             'attackrange': 575,
        #             'attackspeed': 0.625,
        #             'attackspeedperlevel': 2.11,
        #             'crit': 0,
        #             'critperlevel': 0,
        #             'hp': 504,
        #             'hpperlevel': 79,
        #             'hpregen': 5.5,
        #             'hpregenperlevel': 0.5,
        #             'movespeed': 340,
        #             'mp': 418,
        #             'mpperlevel': 25,
        #             'mpregen': 13,
        #             'mpregenperlevel': 0.4,
        #             'spellblock': 30,
        #             'spellblockperlevel': 0.5},
        #   'tags': ['Mage', 'Support'],
        #   'title': 'Rise of the Thorns',
        #   'version': '11.16.1'}}
        if int(champion["key"]) == champion_key:
            return {
                "name": champion["name"],
                "image": "https://ddragon.leagueoflegends.com/cdn/11.16.1/img/champion/{}".format(
                    champion["image"]["full"]
                ),
                "blurb": champion["blurb"],
                "info": champion["info"],
            }
    return None


def get_champion_mini(champion_key=None):
    if champion_key is None:
        raise ValueError("champion_key can't be 'None'")

    for champion in get_champions_list_cache():
        if int(champion["key"]) == champion_key:
            return {
                "name": champion["name"],
                "image": "https://ddragon.leagueoflegends.com/cdn/11.16.1/img/champion/{}".format(
                    champion["image"]["full"]
                ),
            }
    return None
