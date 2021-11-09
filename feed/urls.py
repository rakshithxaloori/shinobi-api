from django.urls import path

from feed import views

urlpatterns = [
    path("", views.feed_view, name="feed"),
]
