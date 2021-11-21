# Update today's clip count
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from clips.models import Clip
from clips.tasks import delete_clip_task


@receiver(pre_delete, sender=Clip)
def pre_delete_clip(sender, instance, **kwargs):
    # Delete the clip if exists
    delete_clip_task.delay(instance.url)
