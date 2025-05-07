from django.shortcuts import render, redirect
from itertools import groupby
from devices.models import *
from rooms.models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from myapp.helper import calculate_daily_urine_volume
from django.db.models import Sum
from datetime import datetime,time,timedelta
from types import SimpleNamespace
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.urls import reverse

# Create your views here.

@login_required(login_url="login")
def weight_display_dashboard(request):
    """
    從 RoomConfig 取得所有啟用且設定顯示在儀表板的房間，
    根據每個房間取得最新的 SensorData 與對應病患資訊，
    若該房間沒有 SensorData 或 LocationPatient 資料（或病患資料），則卡片顯示「無資料」。
    """
    # 取得啟用且設定顯示的房間，依 display_order 排序
    rooms = RoomConfig.objects.filter(is_active=True)
    now = timezone.now()
    cards = []
    normal_count = 0  # 狀態正常病患數量
    warning_count = 0  # 狀態警示病患數量
    for room in rooms:
        room_number = room.room_number
        # 嘗試取得對應的 LocationPatient 資料
           
        lp = LocationPatient.objects.filter(location=room_number).first()
        try:
        # 嘗試取得此房間最新的 SensorData
            sensor = SensorData.objects.filter(location=room_number,patient=lp.patient.patient_id).order_by("-timestamp").first()
            print(sensor)
        except :
            sensor=None
            print(f'{room_number}無病患')
           
        if sensor:
            
            device=DeviceConfig.objects.get(chip_id=sensor.chip_id.chip_id)
            
            if device.status=="connect":
                has_data = True
                card = {
                "room_number": room_number,
                "chip_id": sensor.chip_id.chip_id if hasattr(sensor.chip_id, "chip_id") else sensor.chip_id,
                "current_value": sensor.value,
                "status": sensor.status,
                "timestamp": sensor.timestamp,
                "patient_name": lp.patient.name,
                "patient_id": lp.patient.patient_id,
                "has_data": has_data,
            }
                if sensor.status == "正常":
                    normal_count += 1
                else:
                    warning_count += 1
            else:
                
                card = {
                "room_number": room_number,
                "has_data": False,
                }
            
            
            
        else:
            # 若該房間沒有 SensorData，則標記為無資料
            card = {
                "room_number": room_number,
                "has_data": False,
            }
        cards.append(card)
    
    return render(request, "urine_monitor/weight_display_dashboardnn.html", {
        "cards": cards,
        "username": request.user.username,
        "role": request.user.role,
        "normal_count":normal_count,
        "warning_count":warning_count,
    })
@require_GET
@login_required(login_url="login")
def weight_display_dashboard_api(request):
    rooms = RoomConfig.objects.filter(is_active=True)
    now = timezone.now()
    cards = []
    normal_count = 0
    warning_count = 0

    for room in rooms:
        # ① 先抓房→病患對照
        lp = (LocationPatient.objects
              .filter(location=room.room_number)
              .select_related("patient")
              .first())

        patient_id = lp.patient.patient_id if (lp and lp.patient) else None

        # ② 取最新 SensorData；有病患時再加 patient 條件
        sensor_qs = SensorData.objects.filter(location=room.room_number)
       
        if patient_id:
            sensor_qs = sensor_qs.filter(patient=patient_id)


        sensor = (sensor_qs
                .order_by("-timestamp")
                .select_related("chip_id")
                .first())
        # ④ 判斷資料是否「夠新」且裝置在線
        is_recent = sensor and (now - sensor.timestamp).total_seconds() <= 5    
        # ③ 組卡片
        if is_recent and sensor.chip_id.status=="connect" and lp and lp.patient:
            status = sensor.status
            ts_str = timezone.localtime(sensor.timestamp).strftime("%Y-%m-%d %H:%M")

            cards.append({
                "room_number"  : room.room_number,
                "chip_id"      : sensor.chip_id.chip_id,
                "current_value": sensor.value,
                "status"       : status,
                "timestamp"    : ts_str,
                "patient_name" : lp.patient.name,
                "patient_id"   : lp.patient.patient_id,
                "has_data"     : True,
                "detail_url"   : reverse("room_detail",
                                         args=[room.room_number,
                                               lp.patient.patient_id])
            })

            if status == "正常":
                normal_count += 1
            else:
                warning_count += 1

        else:
            # 沒有病患或裝置未連線 → 顯示「無資料」卡片
            cards.append({
                "room_number": room.room_number,
                "has_data"   : False,
            })
    
    
    return JsonResponse({
        "normal" : normal_count,
        "warning": warning_count,
        "cards"  : cards
    })
    
    
# =============== 1. weight_display ===============
@login_required(login_url="login")
def weight_display(request):
    currentpatient = list(LocationPatient.objects.filter(patient_id__isnull=False).values_list("patient_id", flat=True))
    # activeroom = list(RoomConfig.objects.filter(is_active=True).values_list("room_number", flat=True))
    # condevice = list(DeviceConfig.objects.filter(status="connect").values_list("chip_id", flat=True))
   
    # 這裡 time 是一個字典，映射 patient_id 到 start_date
    qs = LocationPatientHistory.objects.filter(end_date__isnull=True).values_list("patient_id", "start_date","location")
    time = {
    pid: {"start_date": start, "location": loc}
    for pid, start, loc in qs
    }
    # print(time)
    display_data = SensorData.objects.filter(
        patient__in=currentpatient,
        # location__in=activeroom,
        # chip_id__in=condevice
    ).order_by("patient", "-timestamp")

    filtered_display = []
    for record in display_data:
        admission_date = time.get(record.patient).get("start_date")
        
        # 如果沒有 admission date 或 record.timestamp 在 admission_date 之後，才保留這筆資料
        if admission_date is None or record.timestamp >= admission_date:
            filtered_display.append(record)

    # 建立一個字典: patient_id -> patient name
    patient_names = dict(PatientData.objects.all().values_list("patient_id", "name"))

    # 利用 groupby 分組 (前提是 filtered_display 已經依 patient 升序排序)
    show = []
    fresh_window=timedelta(seconds=20)# 幾秒內算「最新」
    for patient,group in groupby(filtered_display, key=lambda x: x.patient):
        latest_record = next(group)#從這個迭代器中取出第一筆。把它賦值給 latest_record，就得到了該病患最新的一筆感測紀錄。
        if (timezone.now()-latest_record.timestamp)<=fresh_window:
            latest_record.patient_name = patient_names.get(latest_record.patient, "無資料")
            # show.append(latest_record)
            # 計算當天累積尿量
            today = timezone.now().date()
            daily_vol = calculate_daily_urine_volume(latest_record.patient, today, tolerance=5)
            latest_record.daily_volume = daily_vol
            
            show.append(latest_record)
        else:
            show.append(SimpleNamespace(
                chip_id      = None,
                location     = time.get(patient).get("location"),
                patient      = patient,
                patient_name = patient_names.get(latest_record.patient, "無資料"),
                value        = None,
                daily_volume = None,
                status       = "無設備資料",
                timestamp    = None,
            ))
    
    return render(request, "urine_monitor/weight_displaynn.html", {
        "display_data": show,
        "username": request.user.username,
        "role": request.user.role,
    })
    
@login_required(login_url="login")
def weight_display_submit(request):
    """
    接收 weight_display 頁面的勾選項目，儲存到 session，然後導向 nurse 頁面
    """
    if request.method == "POST":
        # 假設前端的勾選框 name="selected_devices" value=chip_id
        selected_list = request.POST.getlist("selected_devices")
        print("POST list :", selected_list)
        # 依據 chip_id 去查詢並存到 session
        request.session["selected_devices"] = selected_list
        print(request.session["selected_devices"])
        return redirect("weight_display_nurse")

    return redirect("weight_display")

# =============== 2. weight_display_nurse ===============
@login_required(login_url="login")
def weight_display_nurse(request):
    """
    顯示在 weight_display 頁面勾選的資料，可以在這裡刪除
    """
    selected_chips = request.session.get("selected_devices", [])
    print(selected_chips)
    devices_data = []
    today = timezone.now().date()
    for chip_id in selected_chips:
        print(chip_id)
        dev = DeviceConfig.objects.filter(chip_id=chip_id).first()
        
        if dev:
            last_data = dev.data.order_by('-timestamp').first()
            print(last_data)
            current_volume = last_data.value if last_data else 0
            sum_data =calculate_daily_urine_volume(last_data.patient, today, tolerance=5) 
            status_str = "正常" if current_volume < dev.threshold else "即將滿"

            # 病患資訊
            try:
                lp = LocationPatient.objects.get(location=dev.device_location)
                patient_obj = lp.patient
                if patient_obj:
                    patient_name = patient_obj.name
                    patient_id = patient_obj.patient_id
                else:
                    patient_name = "未指定"
                    patient_id = "N/A"
            except LocationPatient.DoesNotExist:
                patient_name = "未指定"
                patient_id = "N/A"

            devices_data.append({
                "chip_id": dev.chip_id,
                "device_location": dev.device_location,
                "patient_name": patient_name,
                "patient_id": patient_id,
                "current_volume": current_volume,
                "sum_volume": sum_data,
                "status": status_str,
                "timestamp":timezone.localtime(last_data.timestamp).strftime("%Y-%m-%d %H:%M")if last_data else "",
            })

    return render(request, "urine_monitor/weight_display_nurse.html", {
        "devices_data": devices_data,
        "username": request.user.username,
        "role": request.user.role
    })

@require_GET                          # 只接受 GET
@login_required(login_url="login")
def weight_display_nurse_api(request):
    """回傳 JSON 讓前端定時更新"""
    selected_chips = request.session.get("selected_devices", [])
    devices_data   = []
    today          = timezone.now().date()

    for chip_id in selected_chips:
        dev = DeviceConfig.objects.filter(chip_id=chip_id).first()
        if not dev:
            continue

        last_data = dev.data.order_by("-timestamp").first()  # ⇽ 若有 related_name="data" 就用 dev.data
        current   = last_data.value if last_data else 0
        sum_data  = calculate_daily_urine_volume(last_data.patient, today, tolerance=5)
        status    = "正常" if current < dev.threshold else "即將滿"

        try:
            lp = LocationPatient.objects.get(location=dev.device_location)
            patient = lp.patient
        except LocationPatient.DoesNotExist:
            patient = None

        devices_data.append({
            "chip_id"        : dev.chip_id,
            "device_location": dev.device_location,
            "patient_name"   : patient.name if patient else "未指定",
            "patient_id"     : patient.patient_id if patient else "N/A",
            "current_volume" : current,
            "sum_volume"     : sum_data,
            "status"         : status,
            "timestamp":timezone.localtime(last_data.timestamp).strftime("%Y-%m-%d %H:%M")if last_data else "",
            "delete_url"     : reverse("weight_display_nurse_delete", args=[dev.chip_id]),
        })

    return JsonResponse({"devices": devices_data})

@login_required(login_url="login")
def weight_display_nurse_delete(request, chip_id):
    """
    刪除在 nurse 頁面中的某筆裝置資料（從 session 中移除）
    """
    selected_chips = request.session.get("selected_devices", [])
    if chip_id in selected_chips:
        selected_chips.remove(chip_id)
        request.session["selected_devices"] = selected_chips
    return redirect("weight_display_nurse")

def room_detail(request, room_number,patient_id):
    # 取得今天日期
    today = timezone.now().date()
    start = timezone.make_aware(datetime.combine(today, time.min))
    end = timezone.make_aware(datetime.combine(today, time.max))

    sensor_data = SensorData.objects.filter(
        location=room_number, 
        patient=patient_id,
        timestamp__range=(start, end)
    ).order_by('timestamp')
    # 依房號取得當天的 sensor 資料 (依照你的模型關聯做適當調整)
    # sensor_data = SensorData.objects.filter(
    #     location=room_number, 
    #     timestamp__date=today
    # ).order_by('timestamp')
    
    # 取得病患資訊 (假設 SensorData 與 Patient 是 ForeignKey 關係)
    patient = sensor_data.first().patient if sensor_data.exists() else None

    context = {
        'sensor_data': sensor_data,
        'patient': patient,
        'username':request.user.username,
        'role':request.user.role,
    }
    return render(request, 'urine_monitor/room_detail.html', context)

