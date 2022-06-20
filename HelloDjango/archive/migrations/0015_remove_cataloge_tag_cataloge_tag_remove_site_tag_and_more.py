# Generated by Django 4.0.1 on 2022-05-13 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0014_remove_cataloge_tag_cataloge_tag_remove_site_tag_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cataloge',
            name='tag',
        ),
        migrations.AddField(
            model_name='cataloge',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='archive.tag'),
        ),
        migrations.RemoveField(
            model_name='site',
            name='tag',
        ),
        migrations.AddField(
            model_name='site',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='archive.tag'),
        ),
    ]