# Generated by Django 3.2.4 on 2021-07-21 06:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_user_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='last_active',
            new_name='last_open',
        ),
    ]