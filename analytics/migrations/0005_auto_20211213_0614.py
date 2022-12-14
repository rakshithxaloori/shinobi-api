# Generated by Django 3.2.4 on 2021-12-13 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0004_dailyanalytics_total_views'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dailyanalytics',
            old_name='total_clips',
            new_name='total_clips_m',
        ),
        migrations.AddField(
            model_name='dailyanalytics',
            name='total_clips_w',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
