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


def send_push_message(token, title, message, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token, title=title, body=message, data=extra)
        )
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        # TODO
        # rollbar.report_exc_info(
        #     extra_data={
        #         "token": token,
        #         "title": title,
        #         "message": message,
        #         "extra": extra,
        #         "errors": exc.errors,
        #         "response_data": exc.response_data,
        #     }
        # )
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        # TODO
        # rollbar.report_exc_info(
        #     extra_data={"token": token, "message": message, "extra": extra}
        # )
        # raise self.retry(exc=exc)
        pass

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        expo_token = ExponentPushToken.objects.get(token=token)
        # TODO delete?
        expo_token.is_active = False
        expo_token.save()
    except PushTicketError as exc:
        # Encountered some other per-notification error.
        # TODO
        # rollbar.report_exc_info(
        #     extra_data={
        #         "token": token,
        #         "message": message,
        #         "extra": extra,
        #         "push_response": exc.push_response._asdict(),
        #     }
        # )
        # raise self.retry(exc=exc)
        print(exc.push_response._asdict())
        pass


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
            send_push_message(expo_token.token, title, message)

    except ValidationError:
        # TODO report the error
        return

    except User.DoesNotExist:
        return


@shared_task
def delete_push_token(user_pk, token):
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
