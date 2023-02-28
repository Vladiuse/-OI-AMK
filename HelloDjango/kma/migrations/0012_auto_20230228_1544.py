# Generated by Django 3.2.10 on 2023-02-28 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kma', '0011_country_iso3'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('name', models.CharField(max_length=60, verbose_name='Название валюты')),
                ('iso', models.CharField(max_length=3, primary_key=True, serialize=False, unique=True, verbose_name='Код валюты')),
                ('iso_3366', models.CharField(blank=True, max_length=3, null=True, unique=True, verbose_name='ISO 3166-1')),
            ],
        ),
        migrations.AlterField(
            model_name='country',
            name='phone',
            field=models.CharField(blank=True, max_length=15, verbose_name='Валидный номер'),
        ),
    ]
