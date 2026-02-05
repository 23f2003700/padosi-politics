"""
Celery Configuration and Tasks for Padosi Politics
Optional background job processing
"""

from celery import Celery
from celery.schedules import crontab

def make_celery(app=None):
    """Create and configure Celery instance."""
    celery = Celery(
        'padosi_politics',
        broker=app.config['CELERY_BROKER_URL'] if app else 'redis://localhost:6379/0',
        backend=app.config['CELERY_RESULT_BACKEND'] if app else 'redis://localhost:6379/0',
        include=['app.tasks.scheduled', 'app.tasks.email_tasks']
    )
    
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Kolkata',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        beat_schedule={
            # Auto-escalate old complaints - runs daily at midnight
            'auto-escalate-complaints': {
                'task': 'app.tasks.scheduled.auto_escalate_old_complaints',
                'schedule': crontab(hour=0, minute=0),
            },
            # Send reminder notifications - runs daily at 9 AM
            'send-reminders': {
                'task': 'app.tasks.scheduled.send_reminder_notifications',
                'schedule': crontab(hour=9, minute=0),
            },
            # Calculate monthly karma - runs on 1st of every month at midnight
            'monthly-karma': {
                'task': 'app.tasks.scheduled.calculate_monthly_karma',
                'schedule': crontab(day_of_month=1, hour=0, minute=0),
            },
            # Generate weekly report - runs every Monday at 9 AM
            'weekly-report': {
                'task': 'app.tasks.scheduled.generate_weekly_report',
                'schedule': crontab(day_of_week=1, hour=9, minute=0),
            },
            # Cleanup old notifications - runs weekly on Sunday at midnight
            'cleanup-notifications': {
                'task': 'app.tasks.scheduled.cleanup_old_notifications',
                'schedule': crontab(day_of_week=0, hour=0, minute=0),
            },
        }
    )
    
    if app:
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery


# Create default celery instance
celery = make_celery()
