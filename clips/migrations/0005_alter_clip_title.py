# Generated by Django 3.2.4 on 2021-11-21 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0004_auto_20211121_0428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clip',
            name='title',
            field=models.CharField(max_length=30),
        ),
    ]
