from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import*
from devices.models import SensorData
from django.http import HttpResponse
# Create your views here.
@login_required(login_url="login")
def lp_current_list(request):
    """
    直接顯示 LocationPatient 資料表
    """
    lp_records = LocationPatient.objects.select_related("patient").all().order_by("location")
    return render(request, "rooms/lp_current_list.html", {
        "lp_records": lp_records,
        "username": request.user.username,
        "role": request.user.role
    })

@login_required(login_url="login")
def admit_patient(request, location):
    """
    允許使用者編輯 LocationPatient 記錄，設定某房間的病患入住。
    當設定完成後，同時在 LocationPatientHistory 中記錄入院日期。
    """
    lp_record = get_object_or_404(LocationPatient, location=location)
    
    # 取得所有可供選擇的病患（此處可依需求限制，例如只顯示未入院者）
    patients = PatientData.objects.all()
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        if not patient_id:
            messages.error(request, "請選擇一位病患")
        else:
            try:
                patient = PatientData.objects.get(patient_id=patient_id)
            except PatientData.DoesNotExist:
                messages.error(request, "指定的病患不存在")
                return redirect('admit_patient', location=location)
            if LocationPatient.objects.filter(patient_id=patient_id).exists():
                messages.error(request,"該病患現在住院中")
            else:
                lp_record.patient = patient
                lp_record.save()
            
                # 在歷史紀錄中記錄入院時間（若已存在同房間相同病患的記錄且尚未出院，可視需求更新或跳過）
                LocationPatientHistory.objects.create(
                    location=lp_record.location,
                    patient=patient,
                    start_date=timezone.now(),
                    end_date=None  # 尚未出院
                )
                messages.success(request, f"病患 {patient.name} 已入院，入院時間記錄成功。")
                return redirect('lp_current_list')
    return render(request, "rooms/admit_patient_formn.html", {
        "lp_record": lp_record,
        "patients": patients,
        "username": request.user.username,
        "role": request.user.role
    })

@login_required(login_url="login")
def discharge_patient(request, location):
    """
    處理出院動作：
    - 將指定房間的 LocationPatient 記錄中的病患欄位清除（保留房間資料）
    - 並更新對應的 LocationPatientHistory 記錄，記錄出院時間
    """
    lp_record = get_object_or_404(LocationPatient, location=location)
    if not lp_record.patient:
        messages.error(request, "該病房無住院病患。")
        return redirect('lp_current_list')
    
    discharge_time = timezone.now()  # 已經是 timezone aware 的 datetime 物件
    # 將 discharge_time 轉換為當前時區的時間
    local_discharge_time = timezone.localtime(discharge_time)
    # 格式化成字串
    formatted_time = local_discharge_time.strftime('%Y-%m-%d %H:%M:%S')
    # 更新歷史紀錄：找到最近一筆尚未出院的記錄，並填入出院時間
    history_record = LocationPatientHistory.objects.filter(
        location=lp_record.location,
        patient=lp_record.patient,
        end_date__isnull=True
    ).order_by('-start_date').first()
    
    if history_record:
        history_record.end_date = discharge_time
        history_record.save()
    
    # 清除 LocationPatient 的病患欄位
    lp_record.patient = None
    lp_record.save()
    
    # ---------- 2) 從 session 移除裝置 ----------
    # 找出這位病患最後使用的 chip_id（若有多筆可取最新時間）
    chip_ids = (SensorData.objects
                .filter(patient=history_record.patient.patient_id)
                .order_by("-timestamp")
                .values_list("chip_id", flat=True)
                .distinct())

    if chip_ids:
        selected = request.session.get("selected_devices", [])
        # 去掉在 chip_ids 裏的那些裝置
        new_selected = [cid for cid in selected if cid not in chip_ids]
        if len(new_selected) != len(selected):            # 有變動才寫回
            request.session["selected_devices"] = new_selected
    
    messages.success(request, f"{history_record.patient}病患已於 {formatted_time} 出院。")#discharge_time.strftime('%Y-%m-%d %H:%M:%S')
    return redirect('lp_current_list')

# =============== 5. lp_history_list (病患住出院歷史列表) ===============
@login_required(login_url="login")
def lp_history_list(request):
    """
    直接顯示 LocationPatientHistory 資料表
    """
    text_patient_id=request.GET.get("patient_id")
    admit_date_str=request.GET.get("admit_date")
    discharge_date_str=request.GET.get("discharged_date")
  
    search_params = {
        "patient_id": text_patient_id,
        "admit_date": admit_date_str,
        "discharge_date": discharge_date_str
    }
    
     # 建立篩選條件字典
    filters = {}
    if text_patient_id:
        # 假設 PatientData 的主鍵為 patient_id，且 LocationPatientHistory 中的外鍵欄位名稱為 patient
        filters['patient__patient_id'] = text_patient_id
    if admit_date_str:
        filters['start_date__gte'] = admit_date_str
    if discharge_date_str:
        filters['end_date__lte'] = discharge_date_str

    # 如果至少有一個篩選條件，則執行查詢
    if filters:
        history_records = LocationPatientHistory.objects.select_related("patient").filter(**filters).order_by("-start_date")
    else:
        history_records = LocationPatientHistory.objects.all().order_by("-start_date")
    return render(request, "rooms/lp_history_list.html", {
        "history_records": history_records,
        "username": request.user.username,
        "role": request.user.role,
        "search_params":search_params
    })
    
###############################################################################################################
@login_required(login_url="login")
def roomconfig_list(request):
    """
    顯示所有房間設定資料
    """
    roomconfigs = RoomConfig.objects.all().order_by('room_number')
    return render(request, 'rooms/roomconfig_list.html', {
        'roomconfigs': roomconfigs,
        'username': request.user.username,
        'role': request.user.role
    })

@login_required(login_url="login")
def roomconfig_add(request):
    """
    新增房間設定
    """
    if request.method == 'POST':
        room_number = request.POST.get('room_number', '').strip()
        is_active = True if request.POST.get('is_active') == 'on' else False
        if not room_number:
            messages.error(request, "房間號碼不可為空")
        else:
            if RoomConfig.objects.filter(room_number=room_number).exists():
                messages.error(request, "房間號碼已存在")
            else:
                RoomConfig.objects.create(room_number=room_number, is_active=is_active)
                messages.success(request, "房間已新增")
                return redirect('roomconfig_list')
    return render(request, 'rooms/roomconfig_form.html', {
        'roomconfig': None,
        'username': request.user.username,
        'role': request.user.role
    })

@login_required(login_url="login")
def roomconfig_edit(request, room_id):
    """
    編輯房間設定 (僅允許修改是否顯示，房間號碼設為唯讀)
    """
    roomconfig = get_object_or_404(RoomConfig, id=room_id)
    if request.method == 'POST':
        is_active = True if request.POST.get('is_active') == 'on' else False
        roomconfig.is_active = is_active
        roomconfig.save()
        messages.success(request, "房間設定已更新")
        return redirect('roomconfig_list')
    return render(request, 'rooms/roomconfig_form.html', {
        'roomconfig': roomconfig,
        'username': request.user.username,
        'role': request.user.role
    })

@login_required(login_url="login")
def roomconfig_delete(request, room_id):
    """
    刪除房間設定 (提供刪除確認)
    """
    roomconfig = get_object_or_404(RoomConfig, id=room_id)
    if request.method == 'POST':
        # has_patient=LocationPatient.objects.get(location=id)
        # if not has_patient:
        #     roomconfig.delete()
        #     messages.success(request, "房間已刪除")
        #     return redirect('roomconfig_list')
        # else:
        #     return HttpResponse("THE ROOM HAS PATIENT")
        has_patient = LocationPatient.objects.filter(
            location=roomconfig.room_number,     # ← 依你的資料設計調整
            patient_id__isnull=False             # 只看仍在住院的紀錄（可選）
        ).exists()

        if not has_patient:
            roomconfig.delete()
            messages.success(request, "房間已刪除")
        else:
            messages.error(request, "該房間仍有病患，請先解除綁定後再刪除。")
        return redirect("roomconfig_list")
    return render(request, 'rooms/roomconfig_delete.html', {
        'roomconfig': roomconfig,
        'username': request.user.username,
        'role': request.user.role
    })