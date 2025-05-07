from django.shortcuts import render, get_object_or_404, redirect
from devices.models import *
from rooms.models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import json

# from rest_framework.decorators import api_view
# from .serializers import SensorUploadSerializer, SensorUploadResponseSerializer
# from drf_spectacular.utils import extend_schema
# Create your views here.

@csrf_exempt
def register_device(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        chipid = data.get("chipID")
        if not chipid:
            return JsonResponse({"error": "chipID not provided"}, status=400)
        
        device, created = DeviceConfig.objects.get_or_create(chip_id=chipid)
        message = "New device registered." if created else "Device already registered."
        return JsonResponse({"status": message, "chip_id": device.chip_id})
    else:
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    
# 裝置列表與詳細設定 (前端介面)
def device_list(request):
    devices = DeviceConfig.objects.all().order_by("chip_id")
    devices_ids = DeviceConfig.objects.all().values_list("chip_id", flat=True)

    for dev in devices_ids:
        latest_data = SensorData.objects.filter(chip_id=dev).order_by("-timestamp").first()
        device = DeviceConfig.objects.get(chip_id=dev)
        
        if latest_data is None:
            # 若沒有任何感測資料，視為離線（或依需求處理）
            device.status = "disconnect"
        else:
            diff_seconds = (now() - latest_data.timestamp).total_seconds()
            if diff_seconds > 10:
                device.status = "disconnect"
            else:
                device.status = "connect"
        device.save()
    return render(request, "devices/device_list.html", {"devices": devices,'username': request.user.username,'role': request.user.role})

@login_required(login_url="login")
def device_detail(request, chip_id):
    """表單驗證"""
    device = get_object_or_404(DeviceConfig, chip_id=chip_id)
    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, "設定已更新")
            return redirect("device_list")  # 根據你的 URL 命名
    else:
        form = DeviceForm(instance=device)
    return render(request, "devices/device_detail.html", {"form": form, "device": device,'username': request.user.username,'role': request.user.role})

@login_required(login_url="login")    
def device_delete(request,chip_id):
    """
    刪除設備設定(提供刪除確認)
    """
    device=get_object_or_404(DeviceConfig,chip_id=chip_id)
    if request.method == 'POST':
        try:
            device.delete()
            return redirect('device_list')
        except:
            return render(request,'devices/device_delete_remind.html')
    return render(request,'devices/device_delete.html',{
        'device':device,
        'username':request.user.username,
        'role':request.user.role
    })
    
@csrf_exempt    
def sensor_data_api(request):
    
    if request.method == "POST":
        chip_id_str = request.POST.get("chip_id")
        value_str = request.POST.get("value")
        location_str=request.POST.get("location")
        status_str=request.POST.get("status")
        pla_id=request.POST.get("patient_id")
        
        if not chip_id_str or not value_str:
            return JsonResponse({"error": "missing chip_id or value"}, status=400)

        # 先取得 DeviceConfig 物件
        try:
            device = DeviceConfig.objects.get(chip_id=chip_id_str)
        except DeviceConfig.DoesNotExist:
            return JsonResponse({"error": "Device not found"}, status=404)
        
        pla=LocationPatient.objects.get(location=device.device_location)
        
        # 驗證並轉型感測值
        try:
            value = float(value_str)
        except ValueError:
            return JsonResponse({"error": "Invalid sensor value"}, status=400)

        # 正確寫法：把 DeviceConfig 物件傳入 ForeignKey
        SensorData.objects.create(chip_id=device, value=value,location=location_str,status=status_str,patient=pla_id)
        pid = pla.patient.patient_id if pla.patient else ""
        return JsonResponse({"status": "ok","threshold":device.threshold,"url":device.django_url,"room":device.device_location,"patient_id":pid})
    else:
        return JsonResponse({"error": "POST only"}, status=405)