# Generated by Django 5.2.1 on 2025-06-03 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='animal',
            field=models.TextField(default='Not classified'),
        ),
    ]
