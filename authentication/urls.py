from django.urls import path

from authentication import views

urlpatterns = [
    path("login/google/", views.google_login_view, name="google login"),
    path("signup/google/", views.google_signup_view, name="google signup"),
]
