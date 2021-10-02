from django.contrib import admin

from socials.models import (
    InstagramProfile,
    TwitchProfile,
    YouTubeProfile,
)

# Register your models here.
admin.site.register(InstagramProfile)
admin.site.register(TwitchProfile)
admin.site.register(YouTubeProfile)
