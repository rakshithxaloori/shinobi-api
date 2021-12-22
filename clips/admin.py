from django.contrib import admin

from clips.models import Clip, Report, Like, View

# Register your models here.
admin.site.register(Clip)
admin.site.register(Report)
admin.site.register(Like)
admin.site.register(View)
