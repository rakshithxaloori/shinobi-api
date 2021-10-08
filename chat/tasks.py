from proeliumx.celery import app as celery_app

from authentication.models import User
from chat.models import Chat, ChatUser


@celery_app.task(queue="celery")
def create_chat(being_followed_user_pk, follower_user_pk):
    try:
        being_followed_user = User.objects.get(pk=being_followed_user_pk)
        follower_user = User.objects.get(pk=follower_user_pk)
    except User.DoesNotExist:
        return
    # Create chat only if bidirectional follow
    if (
        being_followed_user.profile.followings.filter(pk=follower_user.pk).exists()
        and not Chat.objects.filter(users__in=[follower_user, being_followed_user])
        .distinct()
        .exists()
    ):
        print("CREATING CHAT", follower_user.username, being_followed_user.username)
        new_chat = Chat.objects.create()
        new_chat.save()
        new_chat.users.add(follower_user, being_followed_user)
        new_chat_user_1 = ChatUser.objects.create(
            user=being_followed_user, chat=new_chat
        )
        new_chat_user_2 = ChatUser.objects.create(user=follower_user, chat=new_chat)
        new_chat_user_1.save()
        new_chat_user_2.save()


@celery_app.task(queue="celery")
def delete_chat(being_followed_user_pk, follower_user_pk):
    try:
        being_followed_user = User.objects.get(pk=being_followed_user_pk)
        follower_user = User.objects.get(pk=follower_user_pk)
    except User.DoesNotExist:
        return
    chat = Chat.objects.filter(
        users__in=[being_followed_user, follower_user]
    ).distinct()
    if chat.exists():
        print("DELETING CHAT", being_followed_user.username, follower_user.username)
        chat[0].delete()
