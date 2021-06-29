# from django.db import models
# from django.db.models.fields import EmailField

# from authentication.models import User


# class Chat(models.Model):
#     users = models.ManyToManyField(User, related_name="chats")
#     created = models.DateTimeField(auto_now_add=True)

#     # TODO limit users.count() to 2


# class Message(models.Model):
#     chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.PROTECT)
#     sent_by = models.ForeignKey(
#         User, related_name="sent_messages", on_delete=models.PROTECT
#     )
#     text = models.TextField()
#     is_read = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True)

#     # TODO sent_by__in chat.users
