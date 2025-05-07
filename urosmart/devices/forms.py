from .models import DeviceConfig
from rooms.models import RoomConfig
from django import forms
class DeviceForm(forms.ModelForm):
    class Meta:
        model = DeviceConfig
        fields = ['device_location', 'threshold', 'django_url']
        widgets = {
            'device_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入設備放置地點'
            }),
            'threshold': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入 Threshold'
            }),
            'django_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入 URL'
            }),
        }
    
    def clean_device_location(self):
        location = self.cleaned_data.get("device_location")
        # 從 RoomConfig 模型中取得所有有效的地點名稱
        valid_locations = list(RoomConfig.objects.values_list('room_number', flat=True))
        if location not in valid_locations:
            raise forms.ValidationError("請輸入正確的地點")
        return location