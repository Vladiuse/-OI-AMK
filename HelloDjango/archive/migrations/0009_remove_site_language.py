# Generated by Django 4.0.1 on 2022-05-11 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0008_languege'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='language',
        ),
    ]
