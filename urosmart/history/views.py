from django.shortcuts import render
from myapp.helper import calculate_daily_urine_volume
from datetime import timedelta,datetime, time
from devices.models import *
from django.contrib.auth.decorators import login_required
from patients.models import *
from django.utils import timezone
# Create your views here.
def show_daily_urine_volumes(request):
    """
    根據 GET 參數 patient_id、start_date 與 end_date，
    計算該日期範圍內每天的累積尿量（針對累積讀數情形）。
    若某天無資料，累積尿量為 0。
    """
    # 從 GET 參數取得病患編號與日期範圍
    patient_id = request.GET.get("patient_id")
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    # 基本檢查：若缺少必要參數則提示錯誤（可依需求修改）
    if not (patient_id and start_date_str and end_date_str):
        return render(request, "history/daily_volumes.html", {
            "error": "請提供病患編號、起始日期與結束日期。",
            "username": request.user.username,
            "role": request.user.role,
        })

    # 將日期字串轉換為日期物件
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return render(request, "history/daily_volumes.html", {
            "error": "日期格式錯誤，請使用 YYYY-MM-DD。",
            "username": request.user.username,
            "role": request.user.role,
        })

    # 檢查日期範圍合理性
    if start_date > end_date:
        return render(request, "history/daily_volumes.html", {
            "error": "起始日期必須小於或等於結束日期。",
            "username": request.user.username,
            "role": request.user.role,
        })

    # 逐天計算累積尿量
    daily_volumes = []
    current_date = start_date
    while current_date <= end_date:
        volume = calculate_daily_urine_volume(patient_id, current_date, tolerance=5)
        daily_volumes.append({
            "date": current_date,
            "volume": volume
        })
        current_date += timedelta(days=1)
       
    return render(request, "history/daily_volumes.html", {
        "patient_id": patient_id,
        "daily_volumes": daily_volumes,
        "start_date": start_date,
        "end_date": end_date,
        "username": request.user.username,
        "role": request.user.role,
    })
    
# =============== 3. show_history ===============
@login_required(login_url="login")
def show_history(request):
    """
    顯示指定病患在給定時間區間內的歷史尿量與警示紀錄，
    並根據每筆 location 的 start_date 與 end_date 與 GET 傳入日期範圍的交集來篩選 SensorData。
    """
    text_patient_id = request.GET.get("patient_id")  # 前端表單中的欄位名稱
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    
    filters={}
    if text_patient_id:
        filters['patient']=text_patient_id
    # if start_date_str:
    #     filters['timestamp__gte']=start_date_str
    # if end_date_str:
    #     filters['timestamp__lte']=end_date_str
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        start_dt   = timezone.make_aware(datetime.combine(start_date, time.min))
        filters["timestamp__gte"] = start_dt

    if end_date_str:
        end_date  = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        end_dt    = timezone.make_aware(datetime.combine(end_date + timedelta(days=1), time.min))
        filters["timestamp__lt"] = end_dt 
    if filters:
        history_data=SensorData.objects.filter(**filters).order_by("-timestamp")
    else:
        history_data=SensorData.objects.all().order_by("-timestamp","patient")
     # 建立一個字典：patient_id -> patient name
    patient_names = dict(PatientData.objects.all().values_list("patient_id", "name"))
    
    # 為每筆 SensorData 記錄補上 patient_name 屬性
    for sensor in history_data:
        # sensor.patient 儲存的是 patient_id，從字典取得對應的姓名
        sensor.patient_name = patient_names.get(sensor.patient, "無資料")
    return render(request,"history/show_historyn.html",{
        "query_data":history_data,
        "username":request.user.username,
        "role":request.user.role
        })