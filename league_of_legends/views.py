from cassiopeia.core import summoner
from django.http import JsonResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework_api_key.permissions import HasAPIKey

from knox.auth import TokenAuthentication

from django_cassiopeia import cassiopeia as cass


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def my_lol_profile_view(request):
    summoner = cass.get_summoner(name="bigfatlp", region="NA")
    return JsonResponse(
        {
            "detail": "{}'s lol profile".format(request.user.username),
            "payload": {
                "name": summoner.name,
                "level": summoner.level,
                "plaform": summoner.region.value,
                "profile_icon": summoner.profile_icon.url,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def match_history_view(request, username=None, match_index=0):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # try:
    #     summoner_name = User.objects.get(
    #         username=username
    #     ).league_of_legends_profile_name
    # except (User.DoesNotExist, LeagueOfLegendsProfile.DoesNotExist):
    #     return JsonResponse({"detail": ""}, status=status.HTTP_404_NOT_FOUND)

    summoner = cass.get_summoner(name="bigfatlp")
    try:
        match = summoner.match_history[match_index]
        match_dict = {}
        match_dict["id"] = match.id
        match_dict["creation"] = match.creation.for_json()
        team = None
        participant = None

        for p in match.blue_team.participants:
            if summoner == p.summoner:
                team = match.blue_team
                participant = p
                break

        if team is None:
            for p in match.red_team.participants:
                if summoner == p.summoner:
                    team = match.red_team
                    participant = p
                    break

        match_dict["team"] = {"side": team.side.name, "win": team.win}

        match_dict["participant"] = {
            "role": participant.role.value,
            "champion": {
                "name": participant.champion.name,
                "image": participant.champion.image.url,
                "key": participant.champion.key,
            },
            "stats": {
                "assists": participant.stats.assists,
                "deaths": participant.stats.deaths,
                "kills": participant.stats.kills,
            },
        }
        items = []

        for item in participant.stats.items:
            if item is not None:
                items.append(
                    {
                        "name": item.name,
                        "image": "http://ddragon.leagueoflegends.com/cdn/11.16.1/img/item/{}".format(
                            item.image.full
                        ),
                    }
                )

        match_dict["participant"]["stats"]["items"] = items

        return JsonResponse(
            {
                "detail": "{}'s match history".format(summoner.name),
                "match": match_dict,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        print(e)
        return JsonResponse(
            {"detail": "Match doesn't exist"}, status=status.HTTP_404_NOT_FOUND
        )


# @api_view(["GET"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, HasAPIKey])
# def match_history_view(request, username=None, begin_index=0, end_index=10):
#     if username is None:
#         return JsonResponse(
#             {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
#         )

#     # try:
#     #     summoner_name = User.objects.get(
#     #         username=username
#     #     ).league_of_legends_profile_name
#     # except (User.DoesNotExist, LeagueOfLegendsProfile.DoesNotExist):
#     #     return JsonResponse({"detail": ""}, status=status.HTTP_404_NOT_FOUND)

#     if begin_index > end_index:
#         return JsonResponse(
#             {"detail": "Bad indices"}, status=status.HTTP_400_BAD_REQUEST
#         )

#     summoner = cass.get_summoner(name="bigfatlp")
#     match_history = []
#     for match in summoner.match_history[begin_index:end_index]:
#         match_dict = {}
#         match_dict["creation"] = match.creation.for_json()
#         team = None
#         participant = None

#         for p in match.blue_team.participants:
#             if summoner == p.summoner:
#                 team = match.blue_team
#                 participant = p
#                 break

#         if team is None:
#             for p in match.red_team.participants:
#                 if summoner == p.summoner:
#                     team = match.red_team
#                     participant = p
#                     break

#         match_dict["team"] = {"side": team.side.name, "win": team.win}

#         match_dict["participant"] = {
#             "role": participant.role.value,
#             "champion": {
#                 "name": participant.champion.name,
#                 "image": participant.champion.image.url,
#                 "key": participant.champion.key,
#             },
#             "stats": {
#                 "assists": participant.stats.assists,
#                 "deaths": participant.stats.deaths,
#                 "kills": participant.stats.kills,
#             },
#         }
#         items = []

#         for item in participant.stats.items:
#             if item is not None:
#                 items.append(
#                     {
#                         "name": item.name,
#                         "image": "http://ddragon.leagueoflegends.com/cdn/11.16.1/img/item/{}".format(
#                             item.image.full
#                         ),
#                     }
#                 )

#         match_dict["participant"]["stats"]["items"] = items

#         match_history.append(match_dict)

#     return JsonResponse(
#         {
#             "detail": "{}'s match history".format(summoner.name),
#             "match_history": match_history,
#         },
#         status=status.HTTP_200_OK,
#     )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def champion_masteries_view(request, username=None, begin_index=0, end_index=20):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # try:
    #     summoner_name = User.objects.get(
    #         username=username
    #     ).league_of_legends_profile_name
    # except (User.DoesNotExist, LeagueOfLegendsProfile.DoesNotExist):
    #     return JsonResponse({"detail": ""}, status=status.HTTP_404_NOT_FOUND)

    if begin_index > end_index:
        return JsonResponse(
            {"detail": "Bad indices"}, status=status.HTTP_400_BAD_REQUEST
        )

    summoner = cass.get_summoner(name="bigfatlp", region="NA")
    champion_masteries = summoner.champion_masteries[begin_index:end_index]
    # champion_masteries = summoner.champion_masteries
    champion_mastery_by_level = dict()

    for champion_mastery in champion_masteries:
        if str(champion_mastery.level) not in champion_mastery_by_level.keys():
            champion_mastery_by_level[str(champion_mastery.level)] = []
        champion_mastery_dict = dict()
        champion_mastery_dict["champion"] = {
            "name": champion_mastery.champion.name,
            "image": champion_mastery.champion.image.url,
            "key": champion_mastery.champion.key,
        }
        champion_mastery_dict["level"] = champion_mastery.level
        champion_mastery_by_level[str(champion_mastery.level)].append(
            champion_mastery_dict
        )

    champion_masteries_list = list()
    for key, value in champion_mastery_by_level.items():
        champion_masteries_list.append({"level": key, "champion_masteries": value})

    def levelFunc(obj):
        return obj["level"]

    champion_masteries_list.sort(
        reverse=True,
        key=levelFunc,
    )

    return JsonResponse(
        {
            "detail": "{}'s champion masteries".format(summoner.name),
            "payload": {
                "champion_masteries": champion_masteries_list,
                "count": len(champion_masteries),
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def champion_view(request, key=None):
    if key is None:
        return JsonResponse(
            {"detail": "champion.key is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    champion = cass.get_champion(key=key)
    champion_dict = dict()
    champion_dict["blurb"] = champion.blurb
    champion_dict["ally_tips"] = champion.ally_tips
    champion_dict["enemy_tips"] = champion.enemy_tips
    champion_dict["info"] = champion.info.to_dict()

    return JsonResponse(
        {
            "detail": "{}'s data".format(champion.name),
            "payload": {"champion": champion_dict},
        },
        status=status.HTTP_200_OK,
    )
