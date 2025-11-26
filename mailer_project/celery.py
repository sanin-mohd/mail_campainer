import os
from celery import Celery

from mailer_project.settings import TIME_ZONE

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mailer_project.settings")
app = Celery("mailer_project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()  # autodiscover tasks in installed apps

# Celery timezone configuration (CRITICAL: Must match Django's TIME_ZONE)
app.conf.timezone = TIME_ZONE
app.conf.enable_utc = False  # Use local timezone (IST), not UTC

# Schedule periodic task to check for scheduled campaigns every minute
app.conf.beat_schedule = {
    "check-scheduled-campaigns-every-minute": {
        "task": "campaigns.tasks.check_scheduled_campaigns",
        "schedule": 60.0,  # Run every 60 seconds
        "options": {
            "expires": 50.0,  # Task expires after 50 seconds (prevents queue buildup)
        }
    }
}
