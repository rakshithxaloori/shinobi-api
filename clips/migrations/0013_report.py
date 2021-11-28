# Generated by Django 3.2.4 on 2021-11-24 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0012_clip_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_not_playing', models.BooleanField(default=False)),
                ('is_not_game_clip', models.BooleanField(default=False)),
                ('clip', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reports', to='clips.clip')),
            ],
        ),
    ]
