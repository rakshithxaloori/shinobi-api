# Generated by Django 3.2.4 on 2021-07-20 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_user_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_active',
            field=models.DateTimeField(auto_now=True),
        ),
    ]