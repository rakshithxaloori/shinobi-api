# Generated by Django 3.2.4 on 2021-07-27 07:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0004_alter_message_sent_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_read', models.DateTimeField(default=django.utils.timezone.now)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_users', to='chat.chat')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chat_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
