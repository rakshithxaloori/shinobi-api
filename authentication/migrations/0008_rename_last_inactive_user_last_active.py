# Generated by Django 3.2.4 on 2021-07-21 06:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_rename_last_active_user_last_open'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='last_inactive',
            new_name='last_active',
        ),
    ]
