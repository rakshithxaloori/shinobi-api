from django.urls import path

from league_of_legends import views

urlpatterns = [
    path("my_profile/", views.my_lol_profile_view, name="my lol profile"),
    path(
        "champion_masteries/<str:username>/<int:beginIndex>/<int:endIndex>/",
        views.champion_masteries_view,
        name="champion masteries",
    ),
    path("champion/<str:key>/", views.champion_view, name="champion"),
]
