from django.urls import path

from notification import views

urlpatterns = [
    path("token/create/", views.push_token_create_view, name="push token create"),
    path(
        "",
        views.notifications_view,
        name="notifications",
    ),
]
