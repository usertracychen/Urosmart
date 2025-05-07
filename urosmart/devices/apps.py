from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler

class DevicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "devices"
    # 排程任務：定時跑 background job 更新資料庫
    def ready(self):
        from .cron import update_status
        scheduler = BackgroundScheduler()
        scheduler.add_job(update_status, 'interval', seconds=5)
        scheduler.start()
