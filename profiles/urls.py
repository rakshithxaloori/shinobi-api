from django.urls import path

from profiles import views

urlpatterns = [
    path("trending/", views.trending_profiles_view, name="trending profiles"),
    path("my/", views.my_profile_view, name="my profile"),
    path("update/", views.update_profile_view, name="update profile"),
    path("u/<str:username>/", views.profile_view, name="profile"),
    path("search/<str:username>/", views.search_view, name="search"),
    path("follow/<str:username>/", views.follow_user_view, name="follow user"),
    path("unfollow/<str:username>/", views.unfollow_user_view, name="unfollow user"),
    path(
        "remove_follower/<str:username>/",
        views.remove_follower_view,
        name="remove follower",
    ),
    path(
        "followers/<str:username>/<int:begin_index>/<int:end_index>/",
        views.followers_list_view,
        name="followers",
    ),
]
