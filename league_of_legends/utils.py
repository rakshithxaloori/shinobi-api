import random, time


from authentication.models import User
from profiles.models import Profile
from league_of_legends.models import LoLProfile
from league_of_legends.cache import get_champion_mini


def get_lol_profile(username):
    if username is None:
        return None
    try:
        lol_profile = User.objects.get(username=username).profile.lol_profile
        return lol_profile
    except (User.DoesNotExist, Profile.DoesNotExist, LoLProfile.DoesNotExist):
        return None


def clean_champion_mastery(champion_mastery):
    cm = get_champion_mini(champion_key=champion_mastery["championId"])
    cm["level"] = champion_mastery["championLevel"]
    return cm
