from django.contrib import admin

from profiles.models import (
    Profile,
    Game,
    Following,
    TwitchProfile,
    YouTubeProfile,
    TwitchStream,
)

# Register your models here.
admin.site.register(Profile)
admin.site.register(Game)
admin.site.register(Following)
admin.site.register(TwitchProfile)
admin.site.register(TwitchStream)
admin.site.register(YouTubeProfile)
