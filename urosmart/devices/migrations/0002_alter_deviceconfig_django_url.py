# Generated by Django 4.2.19 on 2025-04-17 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("devices", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deviceconfig",
            name="django_url",
            field=models.URLField(
                default="http://192.168.1.136:8080/devices/sensor/data/"
            ),
        ),
    ]
