# Generated by Django 3.2.4 on 2021-12-02 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_auto_20211124_0710'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='game_code',
            field=models.CharField(default='LOL', max_length=5, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='game',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
