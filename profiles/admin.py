from django.contrib import admin

from profiles.models import Profile, TwitchProfile, YouTubeProfile

# Register your models here.
admin.site.register(Profile)
admin.site.register(TwitchProfile)
admin.site.register(YouTubeProfile)
