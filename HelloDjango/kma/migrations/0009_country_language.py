# Generated by Django 3.2.10 on 2023-02-25 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kma', '0008_rename_short_country_iso'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='language',
            field=models.ManyToManyField(blank=True, to='kma.Language'),
        ),
    ]
