# Generated by Django 3.2.4 on 2021-11-23 15:43

import clips.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0007_remove_clip_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clip',
            name='id',
            field=models.CharField(default=clips.models.generate_random_id, max_length=12, primary_key=True, serialize=False),
        ),
    ]