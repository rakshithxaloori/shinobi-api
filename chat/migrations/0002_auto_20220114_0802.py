# Generated by Django 3.2.4 on 2022-01-14 08:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatuser',
            name='chat',
        ),
        migrations.RemoveField(
            model_name='chatuser',
            name='user',
        ),
        migrations.RemoveField(
            model_name='message',
            name='chat',
        ),
        migrations.RemoveField(
            model_name='message',
            name='sent_by',
        ),
        migrations.DeleteModel(
            name='Chat',
        ),
        migrations.DeleteModel(
            name='ChatUser',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]