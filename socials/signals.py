from django.dispatch import receiver
from django.db.models.signals import post_save

from socials import twitch_tasks
from socials.models import TwitchProfile


# @receiver(post_save, sender=TwitchProfile)
# def post_save_create_twitch_profile(sender, instance, created, **kwargs):
#     if created:
#         # Create a subscription
#         twitch_tasks.create_subscription.delay(instance.pk)
