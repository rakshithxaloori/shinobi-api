from django.db import models
from django.utils import timezone
from django.db.models.fields import EmailField

from authentication.models import User


class Chat(models.Model):
    users = models.ManyToManyField(User, related_name="chats")
    last_updated = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)

    # TODO limit users.count() to 2
    def __str__(self):
        users = self.users.all()
        return "{} || {}".format(users[0].username, users[1].username)


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sent_by = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.PROTECT
    )
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    # TODO sent_by__in chat.users
