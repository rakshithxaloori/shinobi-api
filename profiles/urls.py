from django.urls import path

from profiles import views

urlpatterns = [
    path("", views.my_profile_view, name="my profile"),
    path("<str:username>/", views.profile_view, name="profile"),
    path("follow/<str:username>/", views.follow_user_view, name="follow user"),
    path("unfollow/<str:username>/", views.unfollow_user_view, name="unfollow user"),
    path(
        "remove_follower/<str:username>/",
        views.views.remove_follower_view,
        name="remove follower",
    ),
]
