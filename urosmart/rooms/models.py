from django.db import models
from patients.models import*
# Create your models here.
# 病房與病患對應表（LocationPatient），以 location 對應 DeviceConfig.device_location
class LocationPatient(models.Model):
    location = models.CharField(max_length=100, primary_key=True)
    patient = models.ForeignKey(PatientData, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.location} - {self.patient.name if self.patient else '未指定'}"

class LocationPatientHistory(models.Model):
    """過去所有歷史紀錄"""
    location = models.CharField(max_length=100)
    patient = models.ForeignKey(PatientData, on_delete=models.PROTECT)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.location} - {self.patient.name} (from {self.start_date} to {self.end_date or 'Now'})"
    
    #病房管理
class RoomConfig(models.Model):
    """
    房間設定模型，用來記錄哪些房間要在系統中顯示
    """
    room_number = models.CharField(max_length=20, unique=True, verbose_name="房間號碼")
    is_active = models.BooleanField(default=True, verbose_name="是否顯示在列表")

    def __str__(self):
        return f"{self.room_number} - {'顯示' if self.is_active else '隱藏'}"
    
# Signals：當 RoomConfig 有新增或刪除時，自動同步更新 LocationPatient 表
"""在 Django 中，信號（Signals）是一種鬆散耦合的通知機制，用於讓不同部分的程式碼在某些事件發生時自動互相通知，而無需直接調用對方的函式。
例如：
當一個模型被儲存（save）或刪除（delete）時，Django 會發出相應的信號（如 post_save、post_delete）。
其他模組可以「監聽」這些信號，並在事件發生時自動執行特定的操作（例如，自動建立關聯資料、發送通知郵件、記錄日誌等）。"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
@receiver(post_save, sender=RoomConfig)
def create_or_update_location_patient(sender, instance, created, **kwargs):
    """
    當新增 RoomConfig 時，自動在 LocationPatient 建立一筆相同 room_number 的記錄（若不存在）。
    若是更新也可以在此處擴充其他邏輯。
    """
    if created:
        LocationPatient.objects.get_or_create(location=instance.room_number)
    else:
        # 若房間號碼更新，則可能需要同步修改 LocationPatient（此處示範僅以建立為主）
        LocationPatient.objects.get_or_create(location=instance.room_number)

@receiver(post_delete, sender=RoomConfig)
def delete_location_patient(sender, instance, **kwargs):
    """
    當 RoomConfig 刪除時，自動刪除對應的 LocationPatient 記錄
    """
    LocationPatient.objects.filter(location=instance.room_number).delete()