from django.dispatch import receiver

from django.db.models.signals import post_save

from authentication.models import User
from profiles.models import Profile
from analytics.tasks import new_user_analytics


@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created and not instance.is_staff:
        Profile.objects.create(user=instance)
        new_user_analytics.delay()
