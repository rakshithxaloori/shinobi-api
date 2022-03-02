# Update today's clip count
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from clips.models import Clip
from clips.tasks import delete_clip_files
from shinobi.utils import get_media_file_path


@receiver(pre_delete, sender=Clip)
def pre_delete_clip(sender, instance, **kwargs):
    # Delete the clip if exists
    delete_clip_files.delay(
        instance.upload_path,
        get_media_file_path(instance.url),
        get_media_file_path(instance.thumbnail),
    )
