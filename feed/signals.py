from django.dispatch import receiver
from django.db.models.signals import post_delete

from feed.models import Post


@receiver(post_delete, sender=Post)
def post_delete_post(sender, instance, **kwargs):
    # Delete the clip if exists
    if hasattr(instance, "clip") and instance.clip is not None:
        instance.clip.delete()
