from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class AppUpdate(models.Model):
    version = models.CharField(max_length=10)
    updates = ArrayField(models.CharField(max_length=200), blank=True)

    def __str__(self) -> str:
        return self.version
