"""Celery configuration with beat schedule for monitoring tasks."""

from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery app
celery_app = Celery(
    "growth_copilot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.monitoring_tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        # Monitor websites every day at 2 AM UTC
        'monitor-websites-daily': {
            'task': 'monitor_websites',
            'schedule': crontab(hour=2, minute=0),
        },
        
        # Update competitor intelligence every day at 3 AM UTC
        'update-competitor-intelligence': {
            'task': 'update_competitor_intelligence',
            'schedule': crontab(hour=3, minute=0),
        },
        
        # Refresh benchmarks weekly on Sunday at 4 AM UTC
        'populate-benchmarks-weekly': {
            'task': 'populate_benchmarks',
            'schedule': crontab(hour=4, minute=0, day_of_week=0),
        },
        
        # Quick monitoring check every 6 hours for high-priority sites
        'monitor-priority-sites': {
            'task': 'monitor_websites',
            'schedule': crontab(minute=0, hour='*/6'),
        },
    }
)