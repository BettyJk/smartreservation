# backend/backend/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Add this if using periodic tasks
app.conf.beat_schedule = {
    'check-reservations': {
        'task': 'dashboard.tasks.check_reservation_expiry',
        'schedule': 60.0,
    },
}