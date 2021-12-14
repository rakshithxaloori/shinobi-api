from django.contrib import admin

from profiles.models import Profile, Game, Following, PlaysGame

# Register your models here.
admin.site.register(Profile)
admin.site.register(Game)
admin.site.register(PlaysGame)
admin.site.register(Following)
