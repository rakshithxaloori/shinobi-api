# Generated by Django 3.2.4 on 2021-08-09 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0020_game_twitchstream'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='trend_score',
            field=models.IntegerField(default=0),
        ),
    ]