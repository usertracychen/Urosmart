# Generated by Django 4.2.19 on 2025-04-16 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DeviceConfig",
            fields=[
                (
                    "chip_id",
                    models.CharField(
                        max_length=32, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("device_location", models.CharField(max_length=100)),
                ("threshold", models.FloatField(default=100.0)),
                (
                    "django_url",
                    models.URLField(default="http://192.168.1.136:8080/sensor/data/"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("connect", "連線"), ("disconnect", "中斷")],
                        default="connect",
                        max_length=20,
                        verbose_name="狀態",
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="SensorData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.FloatField()),
                ("location", models.CharField(blank=True, max_length=100, null=True)),
                ("patient", models.CharField(blank=True, max_length=20, null=True)),
                ("status", models.CharField(blank=True, max_length=100, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "chip_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="data",
                        to="devices.deviceconfig",
                    ),
                ),
            ],
        ),
    ]
