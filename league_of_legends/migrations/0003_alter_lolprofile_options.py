# Generated by Django 3.2.4 on 2021-11-19 16:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('league_of_legends', '0002_auto_20211013_0956'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lolprofile',
            options={'ordering': ['name']},
        ),
    ]