POST_TITLE_LENGTH = 80


def is_upload_count_zero(user):
    return user.posts.count() == 0
