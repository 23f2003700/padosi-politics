"""
Task Service - Hybrid background task execution
Works with Celery/Redis when available, falls back to synchronous execution.
Compatible with Cloudflare deployment (serverless).
"""

import os
import threading
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app

# Check if Redis/Celery is available
CELERY_ENABLED = os.environ.get('CELERY_ENABLED', 'false').lower() == 'true'

def get_celery():
    """Get Celery instance if available."""
    if CELERY_ENABLED:
        try:
            from app.celery_app import celery
            return celery
        except ImportError:
            return None
    return None


def async_task(task_name):
    """
    Decorator for async tasks that work with or without Celery.
    - If Celery is enabled: runs as Celery task
    - Otherwise: runs in a background thread (dev) or synchronously (serverless)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            celery = get_celery()
            
            if celery and CELERY_ENABLED:
                # Use Celery
                return celery.send_task(task_name, args=args, kwargs=kwargs)
            else:
                # Run in background thread for dev, or sync for serverless
                if os.environ.get('SERVERLESS', 'false').lower() == 'true':
                    # Serverless - run synchronously
                    return func(*args, **kwargs)
                else:
                    # Dev - run in background thread
                    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
                    thread.daemon = True
                    thread.start()
                    return {'status': 'started', 'thread_id': thread.ident}
            
        wrapper.delay = wrapper  # Celery-compatible API
        wrapper.apply_async = lambda args=None, kwargs=None: wrapper(*(args or []), **(kwargs or {}))
        return wrapper
    return decorator


class TaskService:
    """Service for managing background tasks."""
    
    @staticmethod
    def auto_escalate_complaints():
        """Auto-escalate old complaints (7+ days without action)."""
        from app.extensions import db
        from app.models import (
            Complaint, ComplaintStatus, Escalation, User, 
            Notification, NotificationType
        )
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            old_complaints = Complaint.query.filter(
                Complaint.status == ComplaintStatus.OPEN.value,
                Complaint.created_at < cutoff_date
            ).all()
            
            escalated_count = 0
            
            for complaint in old_complaints:
                # Check if already escalated
                existing = Escalation.query.filter_by(
                    complaint_id=complaint.id,
                    is_auto_escalated=True
                ).first()
                
                if existing:
                    continue
                
                escalation = Escalation(
                    complaint_id=complaint.id,
                    escalated_by_id=complaint.complainant_id,
                    escalated_to='secretary',
                    reason='Auto-escalated: Open for 7+ days without acknowledgment',
                    previous_status=complaint.status,
                    is_auto_escalated=True
                )
                
                complaint.status = ComplaintStatus.ESCALATED.value
                complaint.updated_at = datetime.utcnow()
                
                db.session.add(escalation)
                
                # Notify secretary
                secretaries = User.query.join(User.roles).filter(
                    User.society_id == complaint.society_id,
                    User.roles.any(name='secretary')
                ).all()
                
                for secretary in secretaries:
                    Notification.create_notification(
                        user_id=secretary.id,
                        title='Auto-Escalated Complaint',
                        message=f'Complaint "{complaint.title}" auto-escalated (7+ days)',
                        notification_type=NotificationType.ESCALATION,
                        complaint_id=complaint.id
                    )
                
                Notification.create_notification(
                    user_id=complaint.complainant_id,
                    title='Your Complaint Was Escalated',
                    message=f'"{complaint.title}" has been automatically escalated to the secretary',
                    notification_type=NotificationType.ESCALATION,
                    complaint_id=complaint.id
                )
                
                escalated_count += 1
            
            db.session.commit()
            
            return {'success': True, 'escalated': escalated_count}
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Auto-escalate error: {e}')
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def send_pending_reminders():
        """Send reminders for complaints in progress for 3+ days."""
        from app.extensions import db
        from app.models import Complaint, ComplaintStatus, User, Notification, NotificationType
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=3)
            
            stale_complaints = Complaint.query.filter(
                Complaint.status == ComplaintStatus.IN_PROGRESS.value,
                Complaint.updated_at < cutoff_date
            ).all()
            
            reminder_count = 0
            
            for complaint in stale_complaints:
                # Notify assignee/secretary
                secretaries = User.query.join(User.roles).filter(
                    User.society_id == complaint.society_id,
                    User.roles.any(name='secretary')
                ).all()
                
                for secretary in secretaries:
                    Notification.create_notification(
                        user_id=secretary.id,
                        title='Complaint Needs Attention',
                        message=f'"{complaint.title}" has been in progress for 3+ days',
                        notification_type=NotificationType.REMINDER,
                        complaint_id=complaint.id
                    )
                
                reminder_count += 1
            
            db.session.commit()
            
            return {'success': True, 'reminders_sent': reminder_count}
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Reminder error: {e}')
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def cleanup_old_notifications(days=30):
        """Delete read notifications older than specified days."""
        from app.extensions import db
        from app.models import Notification
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted = Notification.query.filter(
                Notification.is_read == True,
                Notification.created_at < cutoff_date
            ).delete()
            
            db.session.commit()
            
            return {'success': True, 'deleted': deleted}
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Cleanup error: {e}')
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def calculate_society_stats(society_id):
        """Calculate and cache society statistics."""
        from app.extensions import db, cache
        from app.models import Complaint, ComplaintStatus, User
        from sqlalchemy import func
        
        try:
            # Total complaints
            total = Complaint.query.filter_by(society_id=society_id).count()
            
            # By status
            status_counts = db.session.query(
                Complaint.status,
                func.count(Complaint.id)
            ).filter_by(society_id=society_id).group_by(Complaint.status).all()
            
            # Resolution rate
            resolved = sum(c for s, c in status_counts if s == ComplaintStatus.RESOLVED.value)
            resolution_rate = (resolved / total * 100) if total > 0 else 0
            
            # Average resolution time
            resolved_complaints = Complaint.query.filter_by(
                society_id=society_id,
                status=ComplaintStatus.RESOLVED.value
            ).all()
            
            if resolved_complaints:
                total_days = sum(
                    (c.updated_at - c.created_at).days 
                    for c in resolved_complaints if c.updated_at
                )
                avg_resolution_days = total_days / len(resolved_complaints)
            else:
                avg_resolution_days = 0
            
            stats = {
                'total_complaints': total,
                'status_breakdown': dict(status_counts),
                'resolution_rate': round(resolution_rate, 1),
                'avg_resolution_days': round(avg_resolution_days, 1),
                'calculated_at': datetime.utcnow().isoformat()
            }
            
            # Cache for 1 hour
            cache.set(f'society_stats_{society_id}', stats, timeout=3600)
            
            return {'success': True, 'stats': stats}
            
        except Exception as e:
            current_app.logger.error(f'Stats calculation error: {e}')
            return {'success': False, 'error': str(e)}


# Create task wrappers that work with or without Celery
@async_task('tasks.auto_escalate')
def auto_escalate_task():
    """Background task for auto-escalation."""
    from flask import current_app
    with current_app.app_context():
        return TaskService.auto_escalate_complaints()


@async_task('tasks.send_reminders')
def send_reminders_task():
    """Background task for sending reminders."""
    from flask import current_app
    with current_app.app_context():
        return TaskService.send_pending_reminders()


@async_task('tasks.cleanup_notifications')
def cleanup_notifications_task(days=30):
    """Background task for notification cleanup."""
    from flask import current_app
    with current_app.app_context():
        return TaskService.cleanup_old_notifications(days)


@async_task('tasks.calculate_stats')
def calculate_stats_task(society_id):
    """Background task for stats calculation."""
    from flask import current_app
    with current_app.app_context():
        return TaskService.calculate_society_stats(society_id)
