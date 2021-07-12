def add_profile_picture(user, picture):
    """ Add the picture to user if a picture doesn't exist. """
    if user.picture is None or user.picture == "":
        user.picture = picture
        user.save()
