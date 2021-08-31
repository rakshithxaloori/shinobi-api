from django.contrib import admin

from socials.models import (
    InstagramProfile,
    TwitchProfile,
    YouTubeProfile,
    TwitchStream,
)

# Register your models here.
admin.site.register(InstagramProfile)
admin.site.register(TwitchProfile)
admin.site.register(TwitchStream)
admin.site.register(YouTubeProfile)
