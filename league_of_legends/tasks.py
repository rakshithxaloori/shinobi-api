import re
from datetime import datetime

from celery import shared_task


from league_of_legends.wrapper import get_match, get_summoner, get_matchlist
from league_of_legends.models import (
    LoLProfile,
    Team,
    Match,
    Participant,
    ParticipantStats,
)


@shared_task
def add_match_to_db(match_id):
    try:
        Match.objects.get(pk=match_id)
        return

    except Match.DoesNotExist:
        match_dict = get_match(match_id=match_id)

        if match_dict is None or match_dict["gameType"] != "MATCHED_GAME":
            return

        for team in match_dict["teams"]:
            if team["teamId"] == 100:
                # BLUE TEAM
                blue_team = Team.objects.create(
                    creation=datetime.fromtimestamp(match_dict["gameCreation"] / 1000),
                    color=Team.Color.blue,
                    win=team["win"] == "Win",
                )

            elif team["teamId"] == 200:
                # RED TEAM
                red_team = Team.objects.create(
                    creation=datetime.fromtimestamp(match_dict["gameCreation"] / 1000),
                    color=Team.Color.red,
                    win=team["win"] == "Win",
                )

        for p in match_dict["participants"]:
            summoner = get_summoner(account_id=p["player"]["accountId"])
            if summoner is None:
                continue
            try:
                lol_profile = LoLProfile.objects.get(puuid=summoner["puuid"])

            except LoLProfile.DoesNotExist:
                lol_profile = LoLProfile.objects.create(
                    puuid=summoner["puuid"],
                    name=summoner["name"],
                    account_id=summoner["accountId"],
                    summoner_id=summoner["id"],
                )
                lol_profile.save()

            stats = p["stats"]
            item_regex = re.compile("^item")  # ^ -> starts with
            item_keys = list(filter(item_regex.match, stats.keys()))

            items = []

            for item_key in item_keys:
                item = stats[item_key]
                if item != 0:
                    items.append(item)

            new_p_stats = ParticipantStats.objects.create(
                assists=stats["assists"],
                deaths=stats["deaths"],
                kills=stats["kills"],
                items=items,
            )
            new_p_stats.save()

            team = None
            if p["teamId"] == 100:
                team = blue_team
            elif p["teamId"] == 200:
                team = red_team

            new_p = Participant.objects.create(
                summoner=lol_profile,
                team=team,
                stats=new_p_stats,
                champion_key=p["championId"],  # int
                role=p["timeline"]["role"],
            )
            new_p.save()

        new_match = Match.objects.create(
            id=match_dict["gameId"],
            creation=datetime.fromtimestamp(match_dict["gameCreation"] / 1000),
            blue_team=blue_team,
            red_team=red_team,
            mode=match_dict["gameMode"],
            region=match_dict["platformId"],
        )
        blue_team.save()
        red_team.save()
        new_match.save()

    except Exception as e:
        print("EXCEPTION def add_match_to_db:", e)


@shared_task
def update_match_history(lol_profile_pk):
    try:
        lol_profile = LoLProfile.objects.get(pk=lol_profile_pk)
    except LoLProfile.DoesNotExist:
        return
    if lol_profile.profile is None:
        # Only fetch match history if profile is attached
        return

    fetch_all = False
    try:
        team = lol_profile.participations.order_by("-team__creation").first().team
        if team.color == "B":
            latest_match_local = team.b_match
        else:
            latest_match_local = team.r_match
    except Exception:
        fetch_all = True

    matchlist = get_matchlist(
        account_id=lol_profile.account_id, begin_index=0, end_index=20
    )["matches"]

    if matchlist is None:
        return

    for match in matchlist:
        if not fetch_all and match["gameId"] == latest_match_local.id:
            break
        add_match_to_db.delay(match_id=match["gameId"])
        # add_match_to_db(match_id=match["gameId"])

    if not lol_profile.active:
        lol_profile.active = True
        lol_profile.save(update_fields=["active"])
    elif lol_profile.updating:
        lol_profile.updating = False
        lol_profile.save(update_fields=["updating"])


@shared_task
def check_new_matches(lol_profile_pk):
    try:
        lol_profile = LoLProfile.objects.get(pk=lol_profile_pk)
    except LoLProfile.DoesNotExist:
        return

    summoner = get_summoner(puuid=lol_profile.puuid)
    if summoner is None:
        return

    lol_profile.name = summoner["name"]
    lol_profile.save(update_fields=["name"])

    try:

        latest_remote_match_id = get_matchlist(
            account_id=lol_profile.account_id, begin_index=0, end_index=1
        )["matches"][0]["gameId"]

        team = lol_profile.participations.order_by("-team__creation").first().team
        if team.color == "B":
            latest_match_local = team.b_match
        else:
            latest_match_local = team.r_match

    except Exception as e:
        print("EXCEPTION def create_new_matches:", e)
        return

    if latest_remote_match_id != latest_match_local.id:
        lol_profile.updating = True
        lol_profile.save(update_fields=["updating"])
        update_match_history.delay(lol_profile_pk)
        # update_match_history(lol_profile_pk)
