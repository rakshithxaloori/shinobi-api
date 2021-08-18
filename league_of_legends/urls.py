from django.urls import path

from league_of_legends import views

urlpatterns = [
    path("my_profile/", views.my_lol_profile_view, name="my lol profile"),
    path(
        "matches/<str:username>/<int:match_index>/",
        views.match_history_view,
        name="match history",
    ),
    # path(
    #     "matches/<str:username>/<int:begin_index>/<int:end_index>/",
    #     views.match_history_view,
    #     name="match history",
    # ),
    path(
        "masteries/<str:username>/<int:begin_index>/<int:end_index>/",
        views.champion_masteries_view,
        name="champion masteries",
    ),
    path("champion/<str:key>/", views.champion_view, name="champion"),
]
