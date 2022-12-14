from django.dispatch import receiver

from django.db.models.signals import post_save

from authentication.models import User
from profiles.models import Profile
from socials.models import Socials
from settings.models import PrivacySettings
from analytics.tasks import new_user_joined_task


@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created and not instance.is_staff:
        socials = Socials.objects.create()
        socials.save()
        profile = Profile.objects.create(user=instance, socials=socials)
        profile.save()
        privacy = PrivacySettings.objects.create(profile=profile)
        privacy.save()
        new_user_joined_task.delay()
