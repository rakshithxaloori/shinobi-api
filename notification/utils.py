from django.core.exceptions import ValidationError

from notification.models import Notification


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
