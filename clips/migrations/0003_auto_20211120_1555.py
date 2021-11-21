# Generated by Django 3.2.4 on 2021-11-20 15:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import shinobi.utils


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clips', '0002_auto_20211119_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clip',
            name='created_date',
            field=models.DateField(default=shinobi.utils.now_date),
        ),
        migrations.AlterField(
            model_name='clip',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='game_clips', to='profiles.game'),
        ),
        migrations.AlterField(
            model_name='clip',
            name='uploader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clips', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='clip',
            name='url',
            field=models.URLField(unique=True),
        ),
        migrations.CreateModel(
            name='ClipToUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(default=shinobi.utils.now_date)),
                ('created_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('url', models.URLField(unique=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='game_clip_uploads', to='profiles.game')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clip_uploads', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]