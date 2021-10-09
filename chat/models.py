from django.db import models
from django.utils import timezone

from cassandra.cqlengine import columns
from django_cassandra_engine.models import DjangoCassandraModel


class UserReplica(DjangoCassandraModel):
    username = columns.Text(max_length=150)
    picture = columns.Text(required=False)
    picture = models.URLField(null=True, blank=True)


# TODO use DjangoCassandraModel for all models
class Chat(models.Model):
    # users here is redundant, but saves db time
    users = models.ManyToManyField(UserReplica, related_name="chats")
    last_updated = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(check=models.Q(), name="chat_users_count")
    #     ]

    def __str__(self):
        chat_users = self.users.all()
        return "{} || {} || {}".format(
            chat_users[0].username, chat_users[1].username, self.last_updated
        )


class ChatUser(models.Model):
    user = models.ForeignKey(
        UserReplica, related_name="chat_users", on_delete=models.PROTECT
    )
    chat = models.ForeignKey(Chat, related_name="chat_users", on_delete=models.CASCADE)
    # last_read is the last datetime when the user read the chat
    last_read = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} || {}".format(self.chat.pk, self.user.username)


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sent_by = models.ForeignKey(
        UserReplica, related_name="sent_messages", on_delete=models.PROTECT
    )
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(default=timezone.now)

    # TODO sent_by__in chat.users
