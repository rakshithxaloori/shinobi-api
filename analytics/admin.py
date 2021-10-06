from django.contrib import admin

from analytics.models import DailyAnalytics, WeeklyAnalytics, MonthlyAnalytics

admin.site.register(DailyAnalytics)
admin.site.register(WeeklyAnalytics)
admin.site.register(MonthlyAnalytics)
