from django.contrib import admin

from profiles.models import Profile, Game, TwitchProfile, YouTubeProfile, TwitchStream

# Register your models here.
admin.site.register(Profile)
admin.site.register(Game)
admin.site.register(TwitchProfile)
admin.site.register(TwitchStream)
admin.site.register(YouTubeProfile)
