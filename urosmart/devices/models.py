from django.db import models

# Create your models here.
# 裝置設定表（DeviceConfig）
class DeviceConfig(models.Model):
    chip_id = models.CharField(max_length=32, unique=True,primary_key=True)
    device_location = models.CharField(max_length=100)  # 病房號碼
    threshold = models.FloatField(default=100.0)
    django_url = models.URLField(default="http://192.168.1.136:8080/devices/sensor/data/")
    STATUS_CHOICES = (
        ("connect", "連線"),
        ("disconnect", "中斷"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="connect", verbose_name="狀態")
    updated_at = models.DateTimeField(auto_now=True)

    # @property
    # def patient_name(self):
    #     """
    #     根據 device_location 去查詢 LocationPatient，再取得對應的病患姓名
    #     """
    #     try:
    #         lp = LocationPatient.objects.get(location=self.device_location)
    #         if lp.patient:
    #             return lp.patient.name
    #         return "未指定病患"
    #     except LocationPatient.DoesNotExist:
    #         return "未指定病患"

    # def __str__(self):
    #     return f"{self.device_location} ({self.chip_id})"

# 感測資料表（SensorData）
class SensorData(models.Model):
    chip_id = models.ForeignKey(DeviceConfig, on_delete=models.PROTECT, related_name='data')
    value = models.FloatField()
    location = models.CharField(max_length=100,null=True,blank=True)
    patient=models.CharField(max_length=20,null=True,blank=True)
    status=models.CharField(max_length=100,null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location} -{self.chip_id.chip_id} - {self.value} @ {self.timestamp}"