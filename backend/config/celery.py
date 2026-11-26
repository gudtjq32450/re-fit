import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("refit")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Periodic counterfeit / brand trademark scan every 6 hours
app.conf.beat_schedule = {
    "periodic-counterfeit-scan": {
        "task": "apps.ai_engine.tasks.run_periodic_counterfeit_scan",
        "schedule": crontab(minute=0, hour="*/6"),
    },
}
