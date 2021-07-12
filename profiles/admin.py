from django.contrib import admin

from profiles.models import Profile, TwitchProfile

# Register your models here.
admin.site.register(Profile)
admin.site.register(TwitchProfile)
