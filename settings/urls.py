from unicodedata import name
from django.urls import path

from settings import views

urlpatterns = [
    path("get/privacy/", views.get_privacy_settings, name="get privacy settings"),
    path(
        "update/privacy/", views.update_privacy_settings, name="update privacy settings"
    ),
]
