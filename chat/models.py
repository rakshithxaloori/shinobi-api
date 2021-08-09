from datetime import time
from django.db import models
from django.utils import timezone

from authentication.models import User


class Chat(models.Model):
    # users here is redundant, but saves db time
    users = models.ManyToManyField(User, related_name="chats")
    last_updated = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)

    # TODO limit users.count() to 2
    def __str__(self):
        chat_users = self.users.all()
        return "{} || {} || {}".format(
            chat_users[0].username, chat_users[1].username, self.last_updated
        )


class ChatUser(models.Model):
    user = models.ForeignKey(User, related_name="chat_users", on_delete=models.PROTECT)
    chat = models.ForeignKey(Chat, related_name="chat_users", on_delete=models.CASCADE)
    # last_read is the last datetime when the user read the chat
    last_read = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} || {}".format(self.chat.pk, self.user.username)


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sent_by = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.PROTECT
    )
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(default=timezone.now)

    # TODO sent_by__in chat.users
