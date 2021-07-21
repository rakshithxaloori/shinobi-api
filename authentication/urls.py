from django.urls import path

from authentication import views

urlpatterns = [
    path("login/google/", views.google_login_view, name="google login"),
    path("signup/google/", views.google_signup_view, name="google signup"),
    path("logout/", views.logout_view, name="logout"),
    path("check_username/", views.check_username_view, name="check username"),
    path("token_valid/", views.token_valid_view, name="token valid"),
    path("active/", views.active_view, name="active"),
    path("inactive/", views.inactive_view, name="inactive"),
]
