# Generated by Django 3.2.4 on 2021-07-25 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0013_twitchprofile_subscription_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='twitchprofile',
            old_name='subscription_id',
            new_name='stream_online_subscription_id',
        ),
    ]