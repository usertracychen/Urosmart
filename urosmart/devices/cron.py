# devices/cron.py
from django.utils import timezone
from .models import DeviceConfig,SensorData
#排程任務：定時跑 background job 更新資料庫
def update_status():
    now = timezone.now()
    for dev in DeviceConfig.objects.all():
        latest = SensorData.objects.filter(chip_id=dev.chip_id)\
                                  .order_by('-timestamp')\
                                  .first()
        new_status = "disconnect"
        if latest and (now - latest.timestamp).total_seconds() <= 10:
            new_status = "connect"
        DeviceConfig.objects.filter(pk=dev.pk).update(status=new_status)
