import rollbar
from celery import shared_task

from django.core.exceptions import ValidationError

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError

from authentication.models import User
from notification.models import Notification, ExponentPushToken


def send_push_message(token, title, message, data=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token, title=title, body=message, data=data)
        )
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        rollbar.report_exc_info(
            extra_data={
                "type": "expo_notification",
                "detail": "Encountered some likely formatting/validation error.",
                "token": token,
                "title": title,
                "message": message,
                "extra": data,
                "errors": exc.errors,
                "response_data": exc.response_data,
            }
        )
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        rollbar.report_exc_info(
            extra_data={
                "type": "expo_notification",
                "detail": "Encountered some Connection or HTTP error - retry a few times in case it is transient.",
                "token": token,
                "message": message,
                "extra": data,
            }
        )
        # TODO raise self.retry(exc=exc)

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        expo_token = ExponentPushToken.objects.get(token=token)
        expo_token.delete()
    except PushTicketError as exc:
        # Encountered some other per-notification error.
        rollbar.report_exc_info(
            extra_data={
                "type": "expo_notification",
                "detail": "Encountered some other per-notification error.",
                "token": token,
                "message": message,
                "extra": data,
                "push_response": exc.push_response._asdict(),
            }
        )
        # TODO raise self.retry(exc=exc)


# TODO override Notification's create method?
@shared_task
def create_notification(type, sender_pk, receiver_pk):
    try:
        sender = User.objects.get(pk=sender_pk)
        receiver = User.objects.get(pk=receiver_pk)
        new_notification = Notification.objects.create(
            type=type, sender=sender, receiver=receiver
        )
        new_notification.clean_fields()
        new_notification.save()
        expo_tokens = ExponentPushToken.objects.filter(user=receiver, is_active=True)
        # TODO switch case, for each type
        title = "New follower"
        message = "{} follows you".format(sender.username)
        for expo_token in expo_tokens:
            # Send a push notification
            send_push_message(
                token=expo_token.token,
                title=title,
                message=message,
                data={
                    "type": type,
                    "followee": receiver.username,
                    "follower": sender.username,
                },
            )

    except ValidationError:
        # Report the error
        rollbar.report_exc_info(
            extra_data={
                "type": "expo_notification",
                "detail": "Encountered model instance validation error.",
                "sender": sender.username,
                "receiver": receiver.username,
                "notification_type": type,
            }
        )
        return

    except User.DoesNotExist:
        return


@shared_task
def delete_push_token(user_pk, token):
    # Used in logout
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return
    if token is None or user is None:
        return
    try:
        expo_token = ExponentPushToken.objects.get(user=user, token=token)
        expo_token.delete()
    except ExponentPushToken.DoesNotExist:
        pass
