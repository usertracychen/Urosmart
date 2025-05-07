from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label='您的姓名', max_length=100)
    email = forms.EmailField(label='電子郵件')
    subject = forms.CharField(label='主旨', max_length=150)
    message = forms.CharField(label='內容', widget=forms.Textarea(attrs={'rows': 5}))
