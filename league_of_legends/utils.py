import random

from authentication.models import User
from profiles.models import Profile
from league_of_legends.models import LolProfile
from league_of_legends.cache import get_champion_mini


def get_lol_profile(username):
    if username is None:
        return None
    try:
        lol_profile = User.objects.get(username=username).profile.lol_profile
        return lol_profile
    except (User.DoesNotExist, Profile.DoesNotExist, LolProfile.DoesNotExist):
        return None


def clean_champion_mastery(champion_mastery):
    cm = get_champion_mini(champion_key=champion_mastery["championId"])
    cm["level"] = champion_mastery["championLevel"]
    return cm


def get_random_profile_icon(profile_icon: str = None):
    if profile_icon is None:
        raise ValueError("profile_icon can't be None")

    profile_icons_list = [*range(0, 29, 1)]
    try:
        profile_icons_list.remove(profile_icon)
    except ValueError:
        # profile_icon not in list
        pass
    return random.choice(profile_icons_list)
