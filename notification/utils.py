from django.core.exceptions import ValidationError

from notification.models import Notification, ExponentPushToken


def create_notification(type, sender, receiver):
    try:
        new_notification = Notification.objects.create(
            type=type, sender=sender, receiver=receiver
        )
        new_notification.clean_fields()
        new_notification.save()
    except ValidationError:
        # TODO report the error
        return


def delete_push_token(user, token):
    if token is None or user is None:
        return
    try:
        expo_token = ExponentPushToken.objects.get(user=user, token=token)
        expo_token.delete()
    except ExponentPushToken.DoesNotExist:
        pass
