# Generated by Django 3.2.4 on 2021-12-23 06:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0020_alter_clip_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clip',
            options={'ordering': ['-created_datetime']},
        ),
    ]