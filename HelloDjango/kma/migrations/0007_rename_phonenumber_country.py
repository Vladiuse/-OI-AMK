# Generated by Django 3.2.10 on 2023-02-25 17:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kma', '0006_auto_20230225_1659'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PhoneNumber',
            new_name='Country',
        ),
    ]