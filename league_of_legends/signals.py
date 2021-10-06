from django.dispatch import receiver
from django.db.models.signals import post_save


from league_of_legends.tasks import update_match_history
from league_of_legends.models import LolProfile


@receiver(post_save, sender=LolProfile)
def post_save_create_lolprofile(sender, instance, created, **kwargs):
    if created and instance.profile is not None:
        update_match_history.delay(instance.pk)
        # update_match_history(instance.pk)
