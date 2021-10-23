from django.urls import path

from health_checks.views import health_check_view

urlpatterns = [path("", health_check_view, name="health check")]
