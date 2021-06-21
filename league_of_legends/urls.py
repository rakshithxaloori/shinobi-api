from django.urls import path

from league_of_legends import views

urlpatterns = [path("my_profile/", views.my_lol_profile_view, name="my lol profile")]
