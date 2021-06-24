from django.contrib import auth
from django.http import JsonResponse

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from knox.auth import TokenAuthentication

from django_cassiopeia import cassiopeia as cass

from decouple import config


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_lol_profile_view(request):
    summoner = cass.get_summoner(name="Kalturi", region="NA")
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
@permission_classes([IsAuthenticated])
def champion_masteries_view(request, username=None):
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

    summoner = cass.get_summoner(name="Kalturi", region="NA")
    champion_masteries = summoner.champion_masteries[:10]
    champion_masteries_to_dict = list()
    for cm in champion_masteries:
        cm_dict = dict()
        cm_dict["champion"] = {
            "name": cm.champion.name,
            "image": cm.champion.image.url,
            "key": cm.champion.key,
        }
        cm_dict["level"] = cm.level
        cm_dict["points"] = cm.points

        champion_masteries_to_dict.append(cm_dict)

    return JsonResponse(
        {
            "detail": "{}'s champion masteries".format(summoner.name),
            "payload": {
                "champion_masteries": champion_masteries_to_dict,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
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
