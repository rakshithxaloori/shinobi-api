from django.utils import timezone
from django.utils.crypto import get_random_string

from profiles.models import Game


TOTAL_ACTION_COUNT = 1000
BIO_MAX_LENGTH = 150


def get_action_approve(user):
    today_date = timezone.now().date()
    if user.last_action_date != today_date:
        user.last_action_date = today_date
        user.action_count = 0
        user.save(update_fields=["last_action_date", "action_count"])
        return True
    else:
        # TODAY
        if user.action_count >= TOTAL_ACTION_COUNT:
            return False
        else:
            user.action_count += 1
            user.save(update_fields=["action_count"])
            return True


def get_random_id():
    id_str = get_random_string(length=6, allowed_chars="123456789")
    while Game.objects.filter(id=id_str).exists():
        id_str = get_random_string(length=6, allowed_chars="123456789")
    return id_str


def upload_all_games():
    for game in games:
        try:
            if (
                Game.objects.filter(name=game[0]).exists()
                or Game.objects.filter(game_code=game[1]).exists()
            ):
                continue
            new_id = get_random_id()
            game_instance = Game.objects.create(
                id=new_id, name=game[0], game_code=game[1], logo_url=game[2]
            )
            game_instance.save()
            print("Saved {}".format(game[0]))
        except Exception as e:
            print(e)


games = [
    (
        "League of Legends",
        "LOL",
        "https://cdn.shinobi.cc/logos/lol-256x256.png",
    ),
    ("Valorant", "VAL", "https://cdn.shinobi.cc/logos/val-256x256.png"),
    (
        "Counter Strike: Global Offensive",
        "CSGO",
        "https://cdn.shinobi.cc/logos/csgo-256x256.png",
    ),
    ("Destiny 2", "DS2", "https://cdn.shinobi.cc/logos/ds2-256x256.png"),
    ("Free Fire", "FF", "https://cdn.shinobi.cc/logos/ff-256x256.png"),
    (
        "Battlegrounds Mobile India",
        "BGMI",
        "https://cdn.shinobi.cc/logos/bgmi-256x256.png",
    ),
    ("Dota 2", "DTA2", "https://cdn.shinobi.cc/logos/dta2-256x256.png"),
    ("Apex Legends", "AXL", "https://cdn.shinobi.cc/logos/axl-256x256.png"),
    ("Grand Theft Auto V", "GTAV", "https://cdn.shinobi.cc/logos/gtav-256x256.png"),
    ("Fortnite", "FNT", "https://cdn.shinobi.cc/logos/fnt-256x256.png"),
    ("Call of Duty: Warzone", "CDW", "https://cdn.shinobi.cc/logos/cdw-256x256.png"),
    ("Minecraft", "MNC", "https://cdn.shinobi.cc/logos/mnc-256x256.png"),
    ("World of Warcraft", "WOW", "https://cdn.shinobi.cc/logos/wow-256x256.png"),
    (
        "PlayerUnknown's Battlegrounds",
        "PUBG",
        "https://cdn.shinobi.cc/logos/pubg-256x256.png",
    ),
    (
        "PlayerUnknown's Battlegrounds Mobile",
        "PUBGM",
        "https://cdn.shinobi.cc/logos/pubgm-256x256.png",
    ),
    ("Roblox", "RBLX", "https://cdn.shinobi.cc/logos/rblx-256x256.png"),
    ("Overwatch", "OW", "https://cdn.shinobi.cc/logos/ow-256x256.png"),
    ("Among Us", "AU", "https://cdn.shinobi.cc/logos/au-256x256.png"),
    ("Rocket League", "RL", "https://cdn.shinobi.cc/logos/rl-256x256.png"),
    (
        "The Elder Scrolls V: Skyrim",
        "ESV",
        "https://cdn.shinobi.cc/logos/esv-256x256.png",
    ),
    ("Genshin Impact", "GI", "https://cdn.shinobi.cc/logos/gi-256x256.png"),
]
