# Generated by Django 3.2.4 on 2021-12-06 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_auto_20211124_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyanalytics',
            name='total_views',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
