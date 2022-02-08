from authentication.models import User

POST_TITLE_LENGTH = 80
TAGS_MAX_COUNT = 10


def is_upload_count_zero(user):
    return user.posts.count() == 0


def get_users_for_tags(user, tags):
    # Make sure each tag follows user
    if tags is not None and type(tags) == list and len(tags) > 0:
        user_tags = []
        for tag_username in tags:
            try:
                tagged = User.objects.get(username=tag_username)
                # If tagged follows user, add
                if tagged.profile.followings.filter(username=user.username).exists():
                    user_tags.append(tagged)
            except Exception:
                continue
        return user_tags
    return []
