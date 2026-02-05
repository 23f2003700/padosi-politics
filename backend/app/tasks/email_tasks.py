"""
Celery Tasks for Email Sending
"""

from app.celery_app import celery
from app.services.email_service import send_email
import logging

logger = logging.getLogger(__name__)


@celery.task(name='app.tasks.email_tasks.send_email_task', bind=True, max_retries=3)
def send_email_task(self, to, template_name, kwargs):
    """
    Async task to send email.
    Will retry up to 3 times on failure.
    """
    try:
        result = send_email(to, template_name, **kwargs)
        return result
    except Exception as e:
        logger.error(f"Email task failed: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@celery.task(name='app.tasks.email_tasks.send_bulk_email_task')
def send_bulk_email_task(recipients, template_name, common_kwargs=None, individual_kwargs=None):
    """
    Async task to send bulk emails.
    """
    from app.services.email_service import send_bulk_emails
    return send_bulk_emails(recipients, template_name, common_kwargs, individual_kwargs)


@celery.task(name='app.tasks.email_tasks.send_weekly_digest')
def send_weekly_digest():
    """
    Send weekly digest to all active users.
    """
    from app.models import User, Complaint, Society
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        societies = Society.query.all()
        emails_sent = 0
        
        for society in societies:
            # Get stats
            new_complaints = Complaint.query.filter(
                Complaint.society_id == society.id,
                Complaint.created_at >= week_ago
            ).count()
            
            resolved_complaints = Complaint.query.filter(
                Complaint.society_id == society.id,
                Complaint.resolved_at >= week_ago
            ).count()
            
            pending_complaints = Complaint.query.filter(
                Complaint.society_id == society.id,
                Complaint.status.in_(['open', 'in_progress', 'acknowledged'])
            ).count()
            
            # Get top issues (most voted complaints)
            top_issues = Complaint.query.filter(
                Complaint.society_id == society.id,
                Complaint.created_at >= week_ago
            ).order_by(Complaint.vote_count.desc()).limit(3).all()
            
            # Send to all active users in society
            users = User.query.filter_by(society_id=society.id, active=True).all()
            
            for user in users:
                send_email(
                    to=user.email,
                    template_name='weekly_digest',
                    name=user.full_name or user.username,
                    society_name=society.name,
                    new_complaints=new_complaints,
                    resolved_complaints=resolved_complaints,
                    pending_complaints=pending_complaints,
                    top_issues=[c.title for c in top_issues],
                    karma_points=user.karma_score
                )
                emails_sent += 1
        
        return {
            'success': True,
            'emails_sent': emails_sent
        }
        
    except Exception as e:
        logger.error(f"Weekly digest failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
