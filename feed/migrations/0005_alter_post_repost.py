# Generated by Django 3.2.4 on 2022-01-12 11:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0004_auto_20220108_0631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='repost',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reposts', to='feed.post'),
        ),
    ]
