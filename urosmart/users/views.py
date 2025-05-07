from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from users.models import *
from django import forms
from .forms import *
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.
@never_cache
def login_view(request):
    if request.method == 'POST':
        # 使用包含 Captcha 欄位的表單
        form = CaptchaLoginForm(request, data=request.POST)
        # 驗證表單（包含驗證 captcha 與使用者名稱、密碼）
        if form.is_valid():
            # 此時表單資料已通過所有驗證，包括 Captcha 的驗證
            user = form.get_user()
            # 雖然表單驗證通過，但仍需檢查帳號狀態
            if user.is_active == False:
                messages.error(request, "您的帳號已停用，請聯絡系統管理員！")
                return render(request, 'users/login.html', {'form': form})
            
            # 登入成功，依角色導向對應頁面
            login(request, user)
            role = getattr(user, 'role', None)
            if role == 'admin':
                return redirect('index_admin')
            else:
                return redirect('index_nurse')
            
        else:
            # 表單驗證失敗時（可能包含 captcha 錯誤、帳號或密碼錯誤等）
            # 如果錯誤僅在 captcha 上，錯誤訊息會由 form 提供
            # 若欄位錯誤訊息未涵蓋帳號或密碼錯誤，可額外提示用戶
            if not form.errors.get('captcha'):
                try:
                    user = CustomUser.objects.get(username=request.POST.get('username'))
                    if user.is_active == False:#user.status == 'inactive':
                        messages.error(request, "您的帳號已停用，請聯絡系統管理員！")
                    else:
                        messages.error(request, "帳號或密碼錯誤")
                except CustomUser.DoesNotExist:
                    messages.error(request, "帳號不存在")
            return render(request, 'users/login.html', {'form': form})
    else:
        # GET 請求，登出並顯示表單
        logout(request)
        form = CaptchaLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required(login_url="login")
def logout_view(request):
    logout(request)
    messages.info(request, "您已成功登出")
    return redirect('login')

# 列出所有使用者
@login_required(login_url="login")
def user_list(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users,'username': request.user.username,'role': request.user.role})

@csrf_exempt
@login_required
def toggle_user_status(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        print(user)
        # 切換「啟用」/「停用」
        # user.status = 'inactive' if user.status == 'active' else 'active'
        # user.save()
        user.is_active = not user.is_active
        print(user.is_active)
        user.save()
        return JsonResponse({
            "is_active": user.is_active,
            "message": f"{user.username} 的狀態已切換為 {'啟用' if user.is_active else '停用'}"
        })
# 建立新使用者
@login_required(login_url="login")
def user_create(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            else:
                messages.error(request, "密碼不可為空！")
                return render(request, 'users/user_form.html', {'form': form})
            user.save()
            # messages.success(request, "使用者新增成功！")
            return redirect('user_list')
    else:
        form = CustomUserForm()
    return render(request, 'users/user_form.html', {'form': form,'username': request.user.username,'role': request.user.role})

# 編輯（更新）使用者資料
@login_required(login_url="login")
def user_detail(request, user_id):
    user_instance = get_object_or_404(User, id=user_id)
    old_password=user_instance.password
    if request.method == "POST":
        form = CustomUserForm(request.POST, instance=user_instance)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password == "":
                user.password=old_password
            else:
                user.set_password(password)
            user.save()
            messages.success(request, "使用者資料更新成功！")
            return redirect('user_list')
    else:
        form = CustomUserForm(instance=user_instance)
        
    return render(request, 'users/user_form.html', {'form': form, 'user': user_instance,'username': request.user.username,'role': request.user.role})

# 刪除使用者
@login_required(login_url="login")
def user_delete(request, user_id):
    user_instance = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user_instance.delete()
        # messages.success(request, "使用者已刪除！")
        return redirect('user_list')
    return render(request, 'users/user_confirm_delete.html', {'user': user_instance,'username': request.user.username,'role': request.user.role})