from chat.models import Chat, ChatUser


def create_chat(following_user, follower_user):
    # Create chat only if bidirectional follow
    if (
        following_user.profile.following.filter(pk=follower_user.pk).exists()
        and not Chat.objects.filter(users__in=[follower_user, following_user])
        .distinct()
        .exists()
    ):
        print("CREATING CHAT", follower_user.username, following_user.username)
        new_chat = Chat.objects.create()
        new_chat.save()
        new_chat.users.add(follower_user, following_user)
        new_chat_user_1 = ChatUser.objects.create(user=following_user, chat=new_chat)
        new_chat_user_2 = ChatUser.objects.create(user=follower_user, chat=new_chat)
        new_chat_user_1.save()
        new_chat_user_2.save()


def delete_chat(following_user, follower_user):
    chat = Chat.objects.filter(users__in=[following_user, follower_user]).distinct()
    if chat.exists():
        print("DELETING CHAT", following_user.username, follower_user.username)
        chat[0].delete()
