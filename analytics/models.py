from django.db import models

from shinobi.utils import now_date


class DailyAnalytics(models.Model):
    date = models.DateField(primary_key=True, default=now_date)
    new_users = models.PositiveBigIntegerField(default=0)
    active_users = models.PositiveBigIntegerField(default=0)
    total_users = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return "{} || a: {} || n: {} || t: {} || c: {}".format(
            self.date,
            self.active_users,
            self.new_users,
            self.total_users,
            self.clips_uploaded,
        )
