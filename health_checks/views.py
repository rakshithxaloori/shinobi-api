from django.http import JsonResponse

from rest_framework import status


# Create your views here.
def health_check_view():
    return JsonResponse({"detail": "A-OKE"}, status=status.HTTP_200_OK)
