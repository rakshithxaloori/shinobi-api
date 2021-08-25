from celery import shared_task

from django_cassiopeia import cassiopeia as cass

from league_of_legends.models import (
    LoLProfile,
    Team,
    Match,
    Participant,
    ParticipantStats,
)


@shared_task
def add_match_to_db(match):
    try:
        Match.objects.get(id=match.id)
        print("SKIPPING MATCH", match.id)

    except Match.DoesNotExist:
        # Add the match to DB
        print("ADDING MATCH", match.id)
        blue_team = Team.objects.create(
            creation=match.creation.datetime,
            color=Team.Color.blue,
            win=match.blue_team.win,
        )
        blue_team.save()
        red_team = Team.objects.create(
            creation=match.creation.datetime,
            color=Team.Color.red,
            win=match.red_team.win,
        )
        red_team.save()

        for p in match.blue_team.participants + match.red_team.participants:
            # if p.is_bot:
            #     continue
            try:
                summoner = LoLProfile.objects.get(puuid=p.summoner.puuid)
            except LoLProfile.DoesNotExist:
                summoner_remote = p.summoner
                summoner = LoLProfile.objects.create(
                    puuid=summoner_remote.puuid,
                    profile=None,
                    name=summoner_remote.name,
                    account_id=summoner_remote.account_id,
                    summoner_id=summoner_remote.id,
                )
                summoner.save()

            items = []
            for item in p.stats.items:
                if item is not None:
                    items.append({"name": item.name, "image": item.image.full})

            new_p_stats = ParticipantStats.objects.create(
                assists=p.stats.assists,
                deaths=p.stats.deaths,
                kills=p.stats.kills,
                items=items,
            )
            new_p_stats.save()

            if p.team.side.value == 100:
                # BLUE TEAM
                new_p = Participant.objects.create(
                    summoner=summoner,
                    team=blue_team,
                    stats=new_p_stats,
                    champion_key=p.champion.key,
                    role=p.role.value,
                )
            elif p.team.side.value == 200:
                # RED TEAM
                new_p = Participant.objects.create(
                    summoner=summoner,
                    team=red_team,
                    stats=new_p_stats,
                    champion_key=p.champion.key,
                    role=p.role.value,
                )
            new_p.save()

        new_match = Match.objects.create(
            id=match.id,
            creation=match.creation.datetime,
            blue_team=blue_team,
            red_team=red_team,
            mode=match.mode.value,
            region=match.region.value,
        )
        new_match.save()

    except Exception as e:
        # TODO REPORT
        print(e)


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
        latest_match_local = (
            lol_profile.participations.order_by("team__creation").first().team.match
        )
    except (Participant.DoesNotExist, AttributeError):
        # AttributeError is caused when Team instance doesn't exist
        fetch_all = True
    except Exception as e:
        print(e)
        fetch_all = True

    match_history = cass.get_summoner(account_id=lol_profile.account_id).match_history
    match = None

    # Atmost fetch only 20 matches
    # cause not needed more
    for i in range(5):
        print("FETCHING MATCH", match_history[i].id)
        try:
            match = match_history[i]
            if not fetch_all and match.id == latest_match_local.id:
                break
            add_match_to_db(match)
        except IndexError:
            # IndexError - when total matches < 20
            break
        except Exception as e:
            # SAFE GUARD, MOSTLY NOT NEEDED
            print(e)
            break
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

    summoner = cass.get_summoner(account_id=lol_profile.account_id)
    lol_profile.name = summoner.name
    lol_profile.save(update_fields=["name"])

    try:

        latest_match_remote = summoner.match_history[0]

        latest_match_local = (
            lol_profile.participations.order_by("team__creation").first().team.match
        )

    except Participant.DoesNotExist:
        return

    except Exception as e:
        print(e)
        return

    if latest_match_remote.id != latest_match_local.id:
        lol_profile.updating = True
        lol_profile.save(fields=["updating"])
        update_match_history(lol_profile=lol_profile)
