import re
from datetime import datetime


from proeliumx.celery import app as celery_app

from league_of_legends.wrapper import get_match_v5, get_summoner, get_matchlist_v5
from league_of_legends.models import (
    LolProfile,
    Team,
    Match,
    Participant,
    ParticipantStats,
)


@celery_app.task(queue="lol")
def add_match_to_db(match_id, platform):
    try:
        Match.objects.get(id=match_id)
        return

    except Match.DoesNotExist:
        match_info = get_match_v5(match_id=match_id, platform=platform)

        if (
            match_info is None
            or match_info["info"]["gameType"] != "MATCHED_GAME"
            or len(re.findall(r"\bTUTORIAL", match_info["info"]["gameMode"])) > 0
        ):
            # Skip if not Match Game or if Tutorial
            return

        match_info = match_info["info"]
        blue_team = None
        red_team = None

        for team in match_info["teams"]:
            if team["teamId"] == 100:
                # BLUE TEAM
                blue_team = Team.objects.create(
                    creation=datetime.fromtimestamp(match_info["gameCreation"] / 1000),
                    color=Team.Color.blue,
                    win=team["win"],
                )

            elif team["teamId"] == 200:
                # RED TEAM
                red_team = Team.objects.create(
                    creation=datetime.fromtimestamp(match_info["gameCreation"] / 1000),
                    color=Team.Color.red,
                    win=team["win"],
                )

        # participants_list = []
        participants_stats_list = []
        lol_profiles_list = []
        for p in match_info["participants"]:
            try:
                lol_profile = LolProfile.objects.get(puuid=p["puuid"])
                lol_profile.name = p["summonerName"]
                lol_profile.profile_icon = p["profileIcon"]
                lol_profile.level = p["summonerLevel"]
                lol_profile.summoner_id = p["summonerId"]
                lol_profile.save(update_fields=["name", "profile_icon", "level"])

            except LolProfile.DoesNotExist:
                lol_profile = LolProfile(
                    puuid=p["puuid"],
                    name=p["summonerName"],
                    profile_icon=p["profileIcon"],
                    level=p["summonerLevel"],
                    summoner_id=p["summonerId"],
                )
                lol_profiles_list.append(lol_profile)

            # Items
            item_regex = re.compile("^item\d")  # ^ -> starts with
            item_keys = list(filter(item_regex.match, p.keys()))

            items = []

            for item_key in item_keys:
                item = p[item_key]
                if item != 0:
                    items.append(item)

            # Spell casts
            spell_cast_regex = re.compile("^spell\d")
            spell_cast_keys = list(filter(spell_cast_regex.match, p.keys()))

            spell_casts = []

            for key in spell_cast_keys:
                spell_cast = p[key]
                if spell_cast != 0:
                    spell_casts.append(spell_cast)

            new_p_stats = ParticipantStats(
                assists=p["assists"],
                deaths=p["deaths"],
                kills=p["kills"],
                total_damage_dealt=p["totalDamageDealt"],
                double_kills=p["doubleKills"],
                penta_kills=p["pentaKills"],
                quadra_kills=p["quadraKills"],
                triple_kills=p["tripleKills"],
                items=items,
                spell_casts=spell_casts,
            )

            team = None
            if p["teamId"] == 100:
                team = blue_team
            elif p["teamId"] == 200:
                team = red_team

            new_p = Participant(
                summoner=lol_profile,
                team=team,
                stats=new_p_stats,
                champion_key=p["championId"],  # int
                role=p["role"],
            )

            participants_stats_list.append((new_p_stats, new_p))
            # participants_list.append(new_p)

        new_match = Match.objects.create(
            id=match_id,
            creation=datetime.fromtimestamp(match_info["gameCreation"] / 1000),
            blue_team=blue_team,
            red_team=red_team,
            mode=match_info["gameMode"],
            platform=match_info["platformId"],
        )

        # This is executed when all code above runs
        # successfully, so we don't save any half baked data
        blue_team.save()
        red_team.save()

        for lol_profile in lol_profiles_list:
            lol_profile.save()

        for stats, participant in participants_stats_list:
            stats.save()
            participant.stats = stats
            participant.save()

        new_match.save()

    except Exception as e:
        print("EXCEPTION def add_match_to_db:", e)


@celery_app.task(queue="lol")
def update_match_history(lol_profile_pk):
    print("UPDATE MATCH HISTORY")
    try:
        lol_profile = LolProfile.objects.get(pk=lol_profile_pk)
        if lol_profile.profile is not None:
            # Only fetch match history if profile is attached
            fetch_all = False
            try:
                team = lol_profile.participations.order_by("-team__creation").first()
                team = team.team
                if team.color == "B":
                    latest_match_local = team.b_match
                else:
                    latest_match_local = team.r_match
            except Exception:
                print("FETCH ALL")
                fetch_all = True

            matchlist = get_matchlist_v5(
                puuid=lol_profile.puuid,
                start_index=0,
                count=20,
                platform=lol_profile.platform,
            )

            print("MATCHLIST", matchlist)

            if matchlist is not None:
                for match_id in matchlist:
                    if not fetch_all and match_id == latest_match_local.id:
                        break
                    print("ADD TO DB")
                    add_match_to_db.delay(
                        match_id=match_id, platform=lol_profile.platform
                    )
                    # add_match_to_db(match_id=match_id)
    except LolProfile.DoesNotExist:
        print("LOL PROFILE NOT FOUND")
        pass

    if not lol_profile.active:
        lol_profile.active = True
        lol_profile.save(update_fields=["active"])
    elif lol_profile.updating:
        lol_profile.updating = False
        lol_profile.save(update_fields=["updating"])


@celery_app.task(queue="lol")
def check_new_matches(lol_profile_pk):
    try:
        lol_profile = LolProfile.objects.get(pk=lol_profile_pk)
        summoner = get_summoner(puuid=lol_profile.puuid, platform=lol_profile.platform)
        if summoner is not None:
            lol_profile = LolProfile.objects.get(puuid=summoner["puuid"])
            lol_profile.name = summoner["name"]
            lol_profile.profile_icon = summoner["profileIconId"]
            lol_profile.level = summoner["summonerLevel"]
            lol_profile.summoner_id = summoner["id"]
            lol_profile.save(
                update_fields=["name", "profile_icon", "level", "summoner_id"]
            )

            try:
                latest_remote_match_id = get_matchlist_v5(
                    puuid=lol_profile.puuid,
                    start_index=0,
                    count=1,
                    platform=lol_profile.platform,
                )

                if latest_remote_match_id is not None:
                    latest_remote_match_id = latest_remote_match_id[0]

                    team = (
                        lol_profile.participations.order_by("-team__creation")
                        .first()
                        .team
                    )
                    if team.color == "B":
                        latest_match_local = team.b_match
                    else:
                        latest_match_local = team.r_match

                    if latest_remote_match_id != latest_match_local.id:
                        lol_profile.updating = True
                        lol_profile.save(update_fields=["updating"])
                        update_match_history.delay(lol_profile_pk)
                        # update_match_history(lol_profile_pk)

            except Exception as e:
                print("EXCEPTION def create_new_matches:", e)
                pass

    except LolProfile.DoesNotExist:
        pass
