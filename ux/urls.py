from django.urls import path

from ux import views


urlpatterns = [path("updates/", views.get_updates_view, name="app updates")]
