
from captcha.fields import CaptchaField
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms

class CaptchaLoginForm(AuthenticationForm):
    captcha = CaptchaField(label='請輸入圖形驗證碼')
    
#取得自訂使用者模型
User = get_user_model()  
#定義一個 ModelForm，用於建立與編輯使用者
class CustomUserForm(forms.ModelForm):
    # 密碼欄位採用 PasswordInput 小工具，編輯時若留空可視為不更改密碼
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False, help_text="若留空則不變更密碼。")

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'employee_id',
            'email',
            'department',
            'role',
            # 'permission',
            # 'status',
            'is_active',
            'password',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            # 'permission': forms.Select(attrs={'class': 'form-control'}),
            # 'status': forms.Select(attrs={'class': 'form-control'}),
            "is_active"  : forms.Select(choices=((True, "啟用"), (False, "停用")),
                                        attrs={"class": "form-control"}),
        }
 