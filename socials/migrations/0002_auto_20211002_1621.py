# Generated by Django 3.2.4 on 2021-10-02 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socials', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twitchprofile',
            name='stream_offline_subscription_id',
        ),
        migrations.RemoveField(
            model_name='twitchprofile',
            name='stream_online_subscription_id',
        ),
        migrations.RemoveField(
            model_name='twitchprofile',
            name='view_count',
        ),
        migrations.DeleteModel(
            name='TwitchStream',
        ),
    ]