# Generated by Django 3.2.4 on 2022-02-11 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0004_alter_notification_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='extra_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
