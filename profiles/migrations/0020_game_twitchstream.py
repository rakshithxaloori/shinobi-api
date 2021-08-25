# Generated by Django 3.2.4 on 2021-07-26 11:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0019_remove_twitchprofile_is_subscription_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('logo_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='TwitchStream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stream_id', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=140)),
                ('thumbnail_url', models.URLField(blank=True, null=True)),
                ('is_streaming', models.BooleanField(default=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='twitch_streams', to='profiles.game')),
                ('twitch_profile', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='twitch_stream', to='profiles.twitchprofile')),
            ],
        ),
    ]