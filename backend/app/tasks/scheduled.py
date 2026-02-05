"""
Scheduled Background Tasks for Padosi Politics
These tasks run on schedule via Celery Beat
"""

from datetime import datetime, timedelta
from app.celery_app import celery
from app.extensions import db


@celery.task(name='app.tasks.scheduled.auto_escalate_old_complaints')
def auto_escalate_old_complaints():
    """
    Auto-escalate complaints that have been open for more than 7 days.
    Runs daily at midnight.
    """
    from app.models import Complaint, ComplaintStatus, Escalation, User, Notification, NotificationType
    from flask import current_app
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        # Find old open complaints
        old_complaints = Complaint.query.filter(
            Complaint.status == ComplaintStatus.OPEN.value,
            Complaint.created_at < cutoff_date
        ).all()
        
        escalated_count = 0
        
        for complaint in old_complaints:
            # Create auto-escalation
            escalation = Escalation(
                complaint_id=complaint.id,
                escalated_by_id=complaint.complainant_id,
                escalated_to='secretary',
                reason='Auto-escalated: Complaint open for more than 7 days without acknowledgment',
                previous_status=complaint.status,
                is_auto_escalated=True
            )
            
            # Update complaint status
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
                    message=f'Complaint "{complaint.title}" auto-escalated due to no response for 7 days',
                    notification_type=NotificationType.ESCALATION,
                    complaint_id=complaint.id
                )
            
            # Notify complainant
            Notification.create_notification(
                user_id=complaint.complainant_id,
                title='Complaint Auto-Escalated',
                message=f'Your complaint "{complaint.title}" has been automatically escalated to the secretary',
                notification_type=NotificationType.ESCALATION,
                complaint_id=complaint.id
            )
            
            escalated_count += 1
        
        db.session.commit()
        
        return {
            'success': True,
            'escalated_count': escalated_count,
            'message': f'Auto-escalated {escalated_count} complaints'
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }


@celery.task(name='app.tasks.scheduled.send_reminder_notifications')
def send_reminder_notifications():
    """
    Send reminder notifications for complaints in progress for more than 3 days.
    Runs daily at 9 AM.
    """
    from app.models import Complaint, ComplaintStatus, User, Notification, NotificationType
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=3)
        
        # Find complaints in progress for too long
        stale_complaints = Complaint.query.filter(
            Complaint.status == ComplaintStatus.IN_PROGRESS.value,
            Complaint.updated_at < cutoff_date
        ).all()
        
        reminder_count = 0
        
        for complaint in stale_complaints:
            # Notify committee members
            committee = User.query.join(User.roles).filter(
                User.society_id == complaint.society_id,
                User.roles.any(name='committee_member')
            ).all()
            
            for member in committee:
                Notification.create_notification(
                    user_id=member.id,
                    title='Complaint Pending Reminder',
                    message=f'Complaint "{complaint.title}" has been in progress for over 3 days',
                    notification_type=NotificationType.REMINDER,
                    complaint_id=complaint.id
                )
            
            # Notify complainant about delay
            Notification.create_notification(
                user_id=complaint.complainant_id,
                title='Complaint Update',
                message=f'Your complaint "{complaint.title}" is still being processed. We apologize for the delay.',
                notification_type=NotificationType.REMINDER,
                complaint_id=complaint.id
            )
            
            reminder_count += 1
        
        db.session.commit()
        
        return {
            'success': True,
            'reminder_count': reminder_count
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }


@celery.task(name='app.tasks.scheduled.calculate_monthly_karma')
def calculate_monthly_karma():
    """
    Calculate and apply monthly karma adjustments.
    Runs on 1st of every month.
    """
    from app.models import User, Complaint, ComplaintStatus, KarmaLog, KarmaReason, Notification, NotificationType
    from sqlalchemy import func
    
    try:
        last_month = datetime.utcnow().replace(day=1) - timedelta(days=1)
        first_of_last_month = last_month.replace(day=1)
        
        # Get all active users
        users = User.query.filter_by(active=True).all()
        
        for user in users:
            bonus_points = 0
            
            # Check for resolved complaints filed by user last month
            resolved_count = Complaint.query.filter(
                Complaint.complainant_id == user.id,
                Complaint.status == ComplaintStatus.RESOLVED.value,
                Complaint.resolved_at >= first_of_last_month,
                Complaint.resolved_at <= last_month
            ).count()
            
            if resolved_count >= 3:
                bonus_points += 10  # Monthly bonus for active participation
            
            # Apply bonus if any
            if bonus_points > 0:
                user.update_karma(bonus_points, KarmaReason.MONTHLY_BONUS)
                
                Notification.create_notification(
                    user_id=user.id,
                    title='Monthly Karma Bonus',
                    message=f'You received +{bonus_points} karma points for your participation last month!',
                    notification_type=NotificationType.KARMA
                )
        
        db.session.commit()
        
        return {
            'success': True,
            'users_processed': len(users)
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }


@celery.task(name='app.tasks.scheduled.generate_weekly_report')
def generate_weekly_report():
    """
    Generate weekly report for society secretaries.
    Runs every Monday at 9 AM.
    """
    from app.models import Society, Complaint, ComplaintStatus, User, Notification, NotificationType
    from sqlalchemy import func
    
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        societies = Society.query.all()
        
        for society in societies:
            # Calculate weekly stats
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
                Complaint.status.in_([
                    ComplaintStatus.OPEN.value,
                    ComplaintStatus.IN_PROGRESS.value,
                    ComplaintStatus.ESCALATED.value
                ])
            ).count()
            
            # Get secretaries
            secretaries = User.query.join(User.roles).filter(
                User.society_id == society.id,
                User.roles.any(name='secretary')
            ).all()
            
            report_message = (
                f"Weekly Report for {society.name}:\n"
                f"• New complaints: {new_complaints}\n"
                f"• Resolved: {resolved_complaints}\n"
                f"• Pending: {pending_complaints}"
            )
            
            for secretary in secretaries:
                Notification.create_notification(
                    user_id=secretary.id,
                    title=f'Weekly Report - {society.name}',
                    message=report_message,
                    notification_type=NotificationType.SYSTEM
                )
        
        db.session.commit()
        
        return {
            'success': True,
            'societies_processed': len(societies)
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }


@celery.task(name='app.tasks.scheduled.cleanup_old_notifications')
def cleanup_old_notifications():
    """
    Delete old read notifications (older than 30 days).
    Runs weekly on Sunday.
    """
    from app.models import Notification
    
    try:
        deleted_count = Notification.cleanup_old_notifications(days=30)
        
        return {
            'success': True,
            'deleted_count': deleted_count
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }
