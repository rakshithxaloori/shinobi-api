from django.urls import path

from user_support import views

urlpatterns = [path("game/request/", views.game_request_view, name="game request")]
