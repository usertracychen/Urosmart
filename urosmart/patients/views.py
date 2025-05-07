from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from devices.models import*
from .models import*
from myapp.helper import calculate_daily_urine_volume
# Create your views here.
def caregiver_login(request):
    if request.method == "POST":
        identity_card = request.POST.get("identity_card")
        if not identity_card:
            messages.error(request, "請輸入病患身分證！")
            return render(request, "patients/caregiver_login.html")
        
        try:
            patient = PatientData.objects.get(identity_card=identity_card)
        except PatientData.DoesNotExist:
            messages.error(request, "查無此病患身分證，請確認後再試！")
            return render(request, "patients/caregiver_login.html")
        
        # 登入成功後，可以將病患資訊存入 session
        request.session["patient_id"] = patient.patient_id
        request.session["patient_name"] = patient.name
        messages.success(request, f"歡迎，您正在查看 {patient.name} 的資料")
        # 導向照顧者儀表板或病患資料頁面，這裡以 'caregiver_dashboard' 為例
        return redirect("index_caregiver")
    
    return render(request, "patients/caregiver_login.html")

def caregiver_index(request):
    if "patient_id" in request.session:
        patientid=request.session["patient_id"]
        patientname=request.session["patient_name"] 
        request.session.set_expiry(120)

        daily_volumes=[]
        current_date=timezone.now().date()
        datanow=SensorData.objects.filter(patient=patientid).order_by("-timestamp").first()
        device=DeviceConfig.objects.get(chip_id=datanow.chip_id.chip_id)
        flag=True
        if (device.status == "disconnect"):
            messages.error(request,"目前無監測尿量")
            flag=False
        else:
            messages.success(request,"監測尿量中")
        for i in range(1,8):
            volume = calculate_daily_urine_volume(patientid, current_date, tolerance=5)
            daily_volumes.append({
                "date": current_date,
                "volume": volume
            })
            current_date-=timedelta(days=1)
        return render(request,"patients/index_caregiver.html",{"patient_id":patientid,"patient_name":patientname,"dailyvolumes":daily_volumes,"now":datanow,"flag":flag})
    else:
        return redirect("caregiver_login")