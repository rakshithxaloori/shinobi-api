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

from authentication.models import User
from league_of_legends.models import LoLProfile
from league_of_legends.tasks import check_new_matches
from league_of_legends.serializers import ParticipantSerializer


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
def my_lol_profile_view(request):
    summoner = cass.get_summoner(name="bigfatlp", region="NA")
    return JsonResponse(
        {
            "detail": "{}'s lol profile".format(request.user.username),
            "payload": {
                "name": summoner.name,
                "level": summoner.level,
                "region": summoner.region.value,
                "profile_icon": summoner.profile_icon.url,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, HasAPIKey])
def match_history_view(request, username=None, begin_index=0, end_index=10):
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if begin_index < 0 or begin_index >= end_index:
        return JsonResponse(
            {"detail": "Bad indices"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        lol_profile = User.objects.get(username=username).profile.lol_profile
    except (User.DoesNotExist, LoLProfile.DoesNotExist):
        return JsonResponse(
            {"detail": "League of Legends profile doesn't exist"},
            status=status.HTTP_404_NOT_FOUND,
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
    if username is None:
        return JsonResponse(
            {"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # try:
    #     summoner_name = User.objects.get(
    #         username=username
    #     ).league_of_legends_profile_name
    # except (User.DoesNotExist, LoLProfile.DoesNotExist):
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
