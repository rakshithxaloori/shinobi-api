from django.contrib import admin

from chat.models import Chat, ChatUser, Message

# # Register your models here.
admin.site.register(Chat)
admin.site.register(ChatUser)
admin.site.register(Message)
