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
