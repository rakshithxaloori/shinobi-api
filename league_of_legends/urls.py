from django.urls import path

from league_of_legends import views

urlpatterns = [
    path("connect/", views.connect_view, name="lol connect"),
    path("verify/", views.verify_view, name="lol verify"),
    path("disconnect/", views.disconnect_view, name="lol disconnect"),
    path("profile/", views.lol_profile_view, name="my lol profile"),
    path(
        "matches/",
        views.match_history_view,
        name="match history",
    ),
    path(
        "masteries/",
        views.champion_masteries_view,
        name="champion masteries",
    ),
    path("champion/", views.champion_view, name="champion"),
    path("match/", views.match_view, name="match"),
]
