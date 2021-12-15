from django.db import models

from shinobi.utils import now_date


class DailyAnalytics(models.Model):
    date = models.DateField(primary_key=True, default=now_date)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    total_users = models.PositiveIntegerField(default=0)
    total_clips_m = models.PositiveIntegerField(default=0)
    total_clips_w = models.PositiveIntegerField(default=0)
    total_views = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return "{} || a: {} || n: {} || t: {} || cm: {} || cw: {} || v: {}".format(
            self.date,
            self.active_users,
            self.new_users,
            self.total_users,
            self.total_clips_m,
            self.total_clips_w,
            self.total_views,
        )
