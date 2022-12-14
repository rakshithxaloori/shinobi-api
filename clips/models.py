from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.validators import MinLengthValidator


from authentication.models import User

from shinobi.utils import now_date


def generate_random_id():
    id_str = get_random_string(length=12)
    while Clip.objects.filter(pk=id_str).exists():
        id_str = get_random_string(length=12)
    return id_str


class Clip(models.Model):
    MOBILE = "M"
    WEB = "W"
    UPLOADED_FROM_CHOICES = [(MOBILE, "Mobile"), (WEB, "Web")]

    id = models.CharField(
        max_length=12,
        primary_key=True,
        default=generate_random_id,
        validators=[MinLengthValidator(limit_value=12)],
    )
    created_date = models.DateField(default=now_date)
    created_datetime = models.DateTimeField(default=timezone.now)
    upload_verified = models.BooleanField(default=False)
    convert_verified = models.BooleanField(default=False)
    uploaded_from = models.CharField(max_length=1, choices=UPLOADED_FROM_CHOICES)
    viewed_by = models.ManyToManyField(
        User, related_name="viewed_clips", blank=True, through="View"
    )
    view_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    height = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()
    duration = models.PositiveSmallIntegerField(default=0)
    file_uuid = models.UUIDField(null=True, blank=True)
    upload_path = models.CharField(null=True, blank=True, max_length=100)
    url = models.URLField(unique=True, null=True, blank=True)
    thumbnail = models.URLField(unique=True, null=True, blank=True)
    job_id = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self) -> str:
        return "{} || {} days ago".format(
            self.id, (timezone.now() - self.created_datetime).days
        )

    class Meta:
        ordering = ["-created_datetime"]


class View(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    clip = models.ForeignKey(Clip, on_delete=models.CASCADE)
    created_date = models.DateField(default=now_date)
    created_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return "{} viewed {} clip || {}".format(
            self.user.username, self.clip.id, self.clip.clip_post.game.game_code
        )

    class Meta:
        ordering = ["-created_datetime"]
