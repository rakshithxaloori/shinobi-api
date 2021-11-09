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


from league_of_legends.models import LolProfile, Participant
from league_of_legends.serializers import ParticipationFeedSerializer
from profiles.models import Profile


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def feed_view(request):
    """Response contains the match history from all games of all the followers."""
    begin_index = request.data.get("begin_index", 0)
    end_index = request.data.get("end_index", 10)
    following_users = request.user.profile.followings.all()
    following_profiles = Profile.objects.filter(user__in=following_users)
    lol_profiles = LolProfile.objects.filter(profile__in=following_profiles)
    participations = Participant.objects.filter(summoner__in=lol_profiles).order_by(
        "-team__creation"
    )[begin_index:end_index]

    participations_data = ParticipationFeedSerializer(participations, many=True).data

    return JsonResponse(
        {
            "detail": "{}'s feed".format(request.user.username),
            "payload": {"feed": participations_data},
        },
        status=status.HTTP_200_OK,
    )
