# Generated by Django 4.0.1 on 2022-05-09 22:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0005_remove_site_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='archive.sitecategoty', verbose_name='Категория сайта'),
        ),
    ]
