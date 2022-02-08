from django.contrib import admin

from feed.models import Post, Report, Like, Tag

admin.site.register(Post)
admin.site.register(Report)
admin.site.register(Like)
admin.site.register(Tag)
