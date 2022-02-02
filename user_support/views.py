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


from user_support.models import GameRequest


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def game_request_view(request):
    game_name = request.data.get("game_name", None)
    if game_name is None:
        return JsonResponse(
            {"detail": "game name is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    new_game_request = GameRequest.objects.create(game_name=game_name)
    new_game_request.save()
    return JsonResponse(
        {"detail": "The game will be added soon!"}, status=status.HTTP_200_OK
    )
