from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    employee_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="員工編號")
    email = models.EmailField('電子郵件', blank=False, null=False)
    department = models.CharField(max_length=50, blank=True, null=True, verbose_name="單位")
    ROLE_CHOICES = (
        ("nurse", "護理人員"),
        ("admin", "系統管理員"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="角色")
    # PERMISSION_CHOICES = (
    #     ("normal", "一般"),
    #     ("readonly", "唯讀"),
    # )
    # permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default="normal", verbose_name="權限")
    # STATUS_CHOICES = (
    #     ("active", "啟用"),
    #     ("inactive", "停用"),
    # )
    # status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="狀態")
    # ===== 關鍵：is_active 已經由 AbstractUser 提供 =====
    # 這裡只保留布林欄位；不要再給 choices，也不要用字串當預設值
    is_active = models.BooleanField( verbose_name="啟用")   # 預設啟用
     # 將 role 加入 REQUIRED_FIELDS
    REQUIRED_FIELDS = ['email', 'role']
    def __str__(self):
        return self.username
