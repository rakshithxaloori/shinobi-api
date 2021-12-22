from django.urls import path

from feed import views

urlpatterns = [
    path("following/", views.following_feed_view, name="feed"),
    path(
        "world/",
        views.world_feed_view,
        name="world clips",
    ),
]
