# Generated by Django 3.2.4 on 2021-09-27 07:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DailyAnalytics',
            fields=[
                ('date', models.DateField(default=django.utils.timezone.now, primary_key=True, serialize=False)),
                ('new_users', models.PositiveBigIntegerField(default=0)),
                ('active_users', models.PositiveBigIntegerField(default=0)),
                ('total_users', models.PositiveBigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyAnalytics',
            fields=[
                ('date', models.DateField(default=django.utils.timezone.now, primary_key=True, serialize=False)),
                ('new_users', models.PositiveBigIntegerField(default=0)),
                ('active_users', models.PositiveBigIntegerField(default=0)),
                ('total_users', models.PositiveBigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='WeeklyAnalytics',
            fields=[
                ('date', models.DateField(default=django.utils.timezone.now, primary_key=True, serialize=False)),
                ('new_users', models.PositiveBigIntegerField(default=0)),
                ('active_users', models.PositiveBigIntegerField(default=0)),
                ('total_users', models.PositiveBigIntegerField(default=0)),
            ],
        ),
    ]
