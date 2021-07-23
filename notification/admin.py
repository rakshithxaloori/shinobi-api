from django.contrib import admin

from notification.models import Notification, ExponentPushToken

# Register your models here.
admin.site.register(Notification)
admin.site.register(ExponentPushToken)
