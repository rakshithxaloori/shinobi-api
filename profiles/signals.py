from django.dispatch import receiver
from django.db.models.signals import post_save

from authentication.models import User
from profiles.models import Profile


@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
