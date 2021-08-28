from league_of_legends.cache import get_champion_full
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

from league_of_legends.tasks import check_new_matches
from league_of_legends.serializers import ParticipantSerializer
from league_of_legends.wrapper import get_summoner
from league_of_legends.utils import get_lol_profile
from league_of_legends.cache import get_champion_full


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def oauth_view(request):
    # TODO
    # Check if the leagueoflegends profile already exists
    # Create only if doesn't
    # TODO get all of match history - SUPER IMPORTANT, use signals

    # return "detail": "Fetching data, come back in a while"
    pass


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def lol_profile_view(request, username):
    lol_profile = get_lol_profile(username=username)
    if lol_profile is None:
        return JsonResponse(
            {"detail": "LoL profile doesn't exist"}, status=status.HTTP_404_NOT_FOUND
        )
    summoner = get_summoner(puuid=lol_profile.puuid)
    return JsonResponse(
        {
            "detail": "{}'s lol profile".format(request.user.username),
            "payload": {
                "name": summoner["name"],
                "level": summoner["summonerLevel"],
                "profile_icon": "http://ddragon.leagueoflegends.com/cdn/11.16.1/img/profileicon/{}.png".format(
                    summoner["profileIconId"]
                ),
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, HasAPIKey])
def match_history_view(request, username=None, begin_index=0, end_index=10):
    if begin_index < 0 or begin_index >= end_index:
        return JsonResponse(
            {"detail": "Bad indices"}, status=status.HTTP_400_BAD_REQUEST
        )

    lol_profile = get_lol_profile(username=username)
    if lol_profile is None:
        return JsonResponse(
            {"detail": "LoL profile doesn't exist"}, status=status.HTTP_404_NOT_FOUND
        )

    if not lol_profile.active:
        return JsonResponse(
            {"detail": "Fetching data from LoL servers"},
            status=status.HTTP_412_PRECONDITION_FAILED,
        )

    check_new_matches.delay(lol_profile.pk)

    total_count = lol_profile.participations.count()
    if begin_index >= total_count or end_index > 20:
        return JsonResponse(
            {
                "detail": "{}'s match history".format(lol_profile.name),
                "payload": {
                    "new": False,
                    " ": [],
                },
            },
            status=status.HTTP_200_OK,
        )

    if end_index >= total_count:
        participations_history = lol_profile.participations.order_by("-team__creation")[
            begin_index:
        ]
    else:
        participations_history = lol_profile.participations.order_by("-team__creation")[
            begin_index:end_index
        ]

    p_history_data = ParticipantSerializer(participations_history, many=True).data

    return JsonResponse(
        {
            "detail": "{}'s match history".format(lol_profile.name),
            "payload": {
                "new": lol_profile.updating,
                "match_history": p_history_data,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def champion_masteries_view(request, username=None, begin_index=0, end_index=20):
    lol_profile = get_lol_profile(username=username)
    if lol_profile is None:
        return JsonResponse(
            {"detail": "LoL profile doesn't exist"}, status=status.HTTP_404_NOT_FOUND
        )

    if begin_index > end_index:
        return JsonResponse(
            {"detail": "Bad indices"}, status=status.HTTP_400_BAD_REQUEST
        )

    summoner = cass.get_summoner(account_id=lol_profile.account_id)
    champion_masteries = summoner.champion_masteries[begin_index:end_index]
    champion_mastery_by_level = dict()

    for champion_mastery in champion_masteries:
        if str(champion_mastery.level) not in champion_mastery_by_level.keys():
            champion_mastery_by_level[str(champion_mastery.level)] = []
        champion_mastery_dict = dict()
        champion_mastery_dict["champion"] = {
            "name": champion_mastery.champion.name,
            "image": champion_mastery.champion.image.url,
            "id": champion_mastery.champion.id,
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
def champion_view(request, champion_id=None):
    if champion_id is None:
        return JsonResponse(
            {"detail": "champion.key is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    champion = get_champion_full(champion_id)

    return JsonResponse(
        {
            "detail": "{}'s data".format(champion["name"]),
            "payload": {"champion": champion},
        },
        status=status.HTTP_200_OK,
    )
