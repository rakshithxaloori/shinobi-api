from django.contrib import admin

from profiles.models import (
    Profile,
    Game,
    Following,
)

# Register your models here.
admin.site.register(Profile)
admin.site.register(Game)
admin.site.register(Following)
