# Generated by Django 3.2.4 on 2022-02-28 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("clips", "0028_auto_20220228_0832"),
    ]

    operations = [
        migrations.RenameField(
            model_name="clip",
            old_name="compressed_verified",
            new_name="convert_verified",
        ),
    ]
