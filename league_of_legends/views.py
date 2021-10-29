from league_of_legends.models import LolProfile, Match
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
from league_of_legends.serializers import (
    LolProfileSerializer,
    MatchSerializer,
    ParticipantSerializer,
    VerifyLolProfileSerializer,
)
from league_of_legends.wrapper import get_champion_masteries, get_summoner
from league_of_legends.utils import (
    get_lol_profile,
    clean_champion_mastery,
    get_random_profile_icon,
)
from league_of_legends.cache import get_champion_full
from league_of_legends.models import VerifyLolProfile


# @api_view(["POST"])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated, HasAPIKey])
# def connect_view(request):
#     # OAuth View
#     # TODO
#     # Check if the leagueoflegends profile already exists
#     # Create only if doesn't

#     # return "detail": "Fetching data, come back in a while"
#     pass


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def connect_view(request):
    summoner_name = request.data.get("summoner_name", None)
    platform: str = request.data.get("platform", None)

    if summoner_name is None:
        return JsonResponse(
            {"detail": "summoner_name required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if platform is None:
        return JsonResponse(
            {"detail": "platform required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if platform.lower() not in [
        "br1",
        "eun1",
        "euw1",
        "jp1",
        "kr",
        "la1",
        "la2",
        "na1",
        "oc1",
        "tr1",
        "ru",
    ]:
        return JsonResponse(
            {"detail": "platform invalid"}, status=status.HTTP_400_BAD_REQUEST
        )

    summoner = get_summoner(name=summoner_name, platform=platform)

    if summoner is None:
        return JsonResponse(
            {
                "detail": "Summoner not found. Make sure both summoner name and server are yours."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        LolProfile.objects.get(puuid=summoner["puuid"])
        return JsonResponse(
            {
                "detail": "League Of Legends profile with {} summoner name already exists".format(
                    summoner["name"]
                )
            }
        )
    except LolProfile.DoesNotExist:
        try:
            verify_profile = VerifyLolProfile.objects.get(user=request.user)
        except VerifyLolProfile.DoesNotExist:
            verify_profile = VerifyLolProfile.objects.create(user=request.user)

        verify_profile.summoner_name = summoner["name"]
        verify_profile.old_profile_icon = summoner["profileIconId"]
        verify_profile.new_profile_icon = get_random_profile_icon(
            str(summoner["profileIconId"])
        )
        verify_profile.platform = platform.upper()
        verify_profile.save()

        return JsonResponse(
            {
                "detail": "Verify by changing profile_icon",
                "payload": VerifyLolProfileSerializer(verify_profile).data,
            }
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def verify_view(request):
    try:
        verify_profile = VerifyLolProfile.objects.get(user=request.user)
    except VerifyLolProfile.DoesNotExist:
        return JsonResponse(
            {"detail": "No verification instance"}, status=status.HTTP_404_NOT_FOUND
        )

    summoner = get_summoner(
        name=verify_profile.summoner_name, platform=verify_profile.platform
    )
    if summoner is None:
        return JsonResponse(
            {
                "detail": "Summoner not found. Make sure both summoner name and server are yours."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if summoner["profileIconId"] == verify_profile.new_profile_icon:
        # Create LolProfile
        try:
            lol_profile = LolProfile.objects.get(puuid=summoner["puuid"])
            lol_profile.profile = request.user.profile
            lol_profile.profile_icon = summoner["profileIconId"]
            lol_profile.level = summoner["summonerLevel"]
            lol_profile.save(update_fields=["profile", "profile_icon", "level"])
        except LolProfile.DoesNotExist:
            lol_profile = LolProfile.objects.create(
                puuid=summoner["puuid"],
                profile=request.user.profile,
                name=summoner["name"],
                profile_icon=summoner["profileIconId"],
                level=summoner["summonerLevel"],
                platform=verify_profile.platform,
                summoner_id=summoner["id"],
            )
            lol_profile.save()

        verify_profile.delete()

        return JsonResponse(
            {"detail": "Verification complete"}, status=status.HTTP_200_OK
        )

    else:
        return JsonResponse(
            {"detail": "Profile Icon didn't match. Verification FAILED"},
            status=status.HTTP_409_CONFLICT,
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def disconnect_view(request):
    try:
        lol_profile = request.user.profile.lol_profile
        lol_profile.profile = None
        lol_profile.save(update_fields=["profile"])
        return JsonResponse(
            {"detail": "LolProfile disconnected"}, status=status.HTTP_200_OK
        )
    except LolProfile.DoesNotExist:
        return JsonResponse(
            {"detail": "LolProfile doesn't exist"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def lol_profile_view(request, username):
    lol_profile = get_lol_profile(username=username)
    if lol_profile is None:
        return JsonResponse(
            {"detail": "League of Legends profile not connected yet!"},
            status=status.HTTP_404_NOT_FOUND,
        )
    return JsonResponse(
        {
            "detail": "{}'s lol profile".format(request.user.username),
            "payload": LolProfileSerializer(lol_profile).data,
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

    if not lol_profile.updating:
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

    champion_masteries = get_champion_masteries(
        summoner_id=lol_profile.summoner_id, platform=lol_profile.platform
    )

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


# TODO why isn't the decorator working?
# @api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def match_view(request, match_id=None):
    if match_id is None:
        return JsonResponse(
            {"detail": "champion_key is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        match = Match.objects.get(id=match_id)
        match_data = MatchSerializer(match).data

        return JsonResponse(
            {
                "detail": "{} match data".format(match_id),
                "payload": {"match": match_data},
            },
            status=status.HTTP_200_OK,
        )
    except Match.DoesNotExist:
        return JsonResponse(
            {"detail": "match_id invalid"},
            status=status.HTTP_400_BAD_REQUEST,
        )
