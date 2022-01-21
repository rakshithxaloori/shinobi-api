POST_TITLE_LENGTH = 80


def should_upload(user):
    return user.posts.count() == 0
