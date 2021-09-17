# Generated by Django 3.2.4 on 2021-09-15 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('league_of_legends', '0003_auto_20210915_1659'),
    ]

    operations = [
        migrations.RenameField(
            model_name='match',
            old_name='region',
            new_name='platform',
        ),
        migrations.RemoveField(
            model_name='lolprofile',
            name='region',
        ),
        migrations.RemoveField(
            model_name='verifylolprofile',
            name='region',
        ),
        migrations.AddField(
            model_name='lolprofile',
            name='platform',
            field=models.CharField(choices=[('BR1', 'BR1'), ('EUN1', 'EUN1'), ('EUW1', 'EUW1'), ('JP1', 'JP1'), ('KR', 'KR'), ('LA1', 'LA1'), ('LA2', 'LA2'), ('NA1', 'NA1'), ('OC1', 'OC1'), ('TR1', 'TR1'), ('RU', 'RU')], default='NA1', max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='verifylolprofile',
            name='platform',
            field=models.CharField(choices=[('BR1', 'BR1'), ('EUN1', 'EUN1'), ('EUW1', 'EUW1'), ('JP1', 'JP1'), ('KR', 'KR'), ('LA1', 'LA1'), ('LA2', 'LA2'), ('NA1', 'NA1'), ('OC1', 'OC1'), ('TR1', 'TR1'), ('RU', 'RU')], default='NA1', max_length=5),
            preserve_default=False,
        ),
    ]