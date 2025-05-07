from django.db import models

# Create your models here.
# 病患資料
class PatientData(models.Model):
    patient_id = models.CharField(max_length=20, primary_key=True)
    identity_card = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # def __str__(self):
    #     return self.name