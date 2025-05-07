# devices/serializers.py
# from rest_framework import serializers
# from devices.models import DeviceConfig, SensorData

# class SensorUploadSerializer(serializers.Serializer):
#     chip_id    = serializers.CharField(help_text="ESP8266 Chip ID")
#     value      = serializers.FloatField(help_text="測量值 (g)")
#     location   = serializers.CharField(required=False, help_text="病房編號")
#     status     = serializers.ChoiceField(choices=[("正常","正常"),("警示","警示")], required=False)
#     patient_id = serializers.CharField(required=False, help_text="病歷號碼")

# class SensorUploadResponseSerializer(serializers.Serializer):
#     status      = serializers.CharField()
#     threshold   = serializers.FloatField()
#     url         = serializers.URLField()
#     room        = serializers.CharField()
#     patient_id  = serializers.CharField(allow_blank=True)
