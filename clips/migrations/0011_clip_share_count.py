# Generated by Django 3.2.4 on 2021-11-24 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0010_auto_20211123_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='clip',
            name='share_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
