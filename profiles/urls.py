from django.urls import path

from profiles import views

urlpatterns = [
    path("my_profile/", views.my_profile_view, name="my profile"),
    path("follow/<str:username>/", views.follow_user_view, name="follow user"),
]
