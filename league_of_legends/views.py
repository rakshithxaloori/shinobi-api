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
    kalturi = cass.get_summoner(name="Kalturi", region="NA")
    print(kalturi)
    return JsonResponse(
        {"detail": "{}'s lol profile".format(request.user.username)},
        status=status.HTTP_200_OK,
    )
