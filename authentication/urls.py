from django.urls import path

from authentication import views

urlpatterns = [
    path("login/google/", views.google_login_view, name="google login"),
    path("signup/google/", views.google_signup_view, name="google signup"),
    path("logout/", views.logout_view, name="logout"),
    path("check_username/", views.check_username_view, name="check username"),
    path("online/", views.online_view, name="online"),
    path("offline/", views.offline_view, name="offline"),
    path(
        "valid/",
        views.valid_token_view,
        name="valid token",
    ),
    path("update/country/", views.update_country_view, name="update country"),
]
