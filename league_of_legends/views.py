from league_of_legends.cache import get_champion_full
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


from league_of_legends.tasks import check_new_matches
from league_of_legends.serializers import ParticipantSerializer
from league_of_legends.wrapper import get_summoner, get_champion_masteries
from league_of_legends.utils import get_lol_profile, clean_champion_mastery
from league_of_legends.cache import get_champion_full


# @api_view(["GET"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, HasAPIKey])
# def oauth_view(request):
#     # TODO
#     # Check if the leagueoflegends profile already exists
#     # Create only if doesn't
#     # TODO get all of match history - SUPER IMPORTANT, use signals

#     # return "detail": "Fetching data, come back in a while"
#     pass


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
    print(summoner)
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


# TODO why isn't the decorator working?
# @api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
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

    champion_masteries = get_champion_masteries(lol_profile.summoner_id)

    if begin_index > len(champion_masteries):
        pass

    if end_index < len(champion_masteries):
        champion_masteries = champion_masteries[begin_index:end_index]
    else:
        champion_masteries = champion_masteries[begin_index:]

    champion_masteries = list(map(clean_champion_mastery, champion_masteries))

    return JsonResponse(
        {
            "detail": "{}'s champion masteries".format(lol_profile.name),
            "payload": {
                "champion_masteries": champion_masteries,
                "count": len(champion_masteries),
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def champion_view(request, champion_key=None):
    if champion_key is None:
        return JsonResponse(
            {"detail": "champion_key is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    champion = get_champion_full(champion_key)

    if champion is None:
        return JsonResponse(
            {"detail": "champion_key invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return JsonResponse(
        {
            "detail": "{}'s data".format(champion["name"]),
            "payload": {"champion": champion},
        },
        status=status.HTTP_200_OK,
    )
