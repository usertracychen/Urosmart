from devices.models import *
from datetime import datetime, time
from django.utils import timezone
def calculate_daily_urine_volume(patient_id, target_date, tolerance=5):
       

    # 如果 target_date 為字串，轉換為 date 物件
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    # 建立當天的開始與結束時間（timezone aware）
    start_dt = timezone.make_aware(datetime.combine(target_date, time.min))
    end_dt = timezone.make_aware(datetime.combine(target_date, time.max))
   
    records=list(SensorData.objects.filter(patient=patient_id,timestamp__range=(start_dt,end_dt)).order_by('timestamp'))
    if len(records) == 0:
        return 0
    previous_value=records[0].value
    daily_volume=0
    for record in records:
        current_value=record.value
        diff=current_value-previous_value
        if(diff<-tolerance):
            daily_volume+=abs(diff)
        previous_value=current_value    
        
    if daily_volume==0:
        daily_volume=records[-1].value            
 
    return daily_volume
