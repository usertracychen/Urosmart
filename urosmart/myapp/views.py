from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import ContactForm
# Create your views here.
def home(request):
    return render(request, 'roleselection.html')

def contact_us(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(
                subject=cd['subject'],
                message=f"來自: {cd['name']} <{cd['email']}>\n\n內容:\n{cd['message']}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],  # 收件人：你系統設定的 Email
            )
            messages.success(request, "已成功送出訊息，我們會儘快與您聯絡！")
            form = ContactForm()  # 清空表單

    return render(request, 'contact.html', {'form': form})

@login_required(login_url="login")
def admin_index(request):
    # 確認使用者是否為「系統管理員」
    # 這裡以 is_superuser 為例；若你使用自訂角色欄位 (role='admin')，可改成其他判斷
    if not (request.user.is_superuser | (request.user.role == 'admin')):
        return HttpResponseForbidden("您沒有系統管理員權限，無法進入此頁面。")
    
    return render(request, 'index_admin.html', {
        'username': request.user.username,'role': request.user.role
    })
      

@login_required(login_url="login")
def nurse_index(request):
    # 假設你使用自訂欄位 role='nurse' 來判斷是否為護理人員
    # 若使用 is_superuser 或其他判斷，請自行調整
    if hasattr(request.user, 'role') and request.user.role != 'nurse':
        return HttpResponseForbidden("您沒有護理人員權限，無法進入此頁面。")
    
    return render(request, 'index_nurse.html', {
        'username': request.user.username,'role': request.user.role
    })