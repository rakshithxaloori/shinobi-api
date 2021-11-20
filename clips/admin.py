from django.contrib import admin

from clips.models import Clip, ClipToUpload

# Register your models here.
admin.site.register(Clip)
admin.site.register(ClipToUpload)
