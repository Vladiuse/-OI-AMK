# Generated by Django 4.0.1 on 2022-05-04 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='description',
            field=models.CharField(blank=True, max_length=200, verbose_name='Описание сайта'),
        ),
    ]
