"""
Email Service for Padosi Politics
Handles all email sending functionality with fallback for non-configured mail
"""

from flask import current_app, render_template_string
from flask_mail import Message
from app.extensions import mail, db
import logging

logger = logging.getLogger(__name__)

# Email Templates
TEMPLATES = {
    'welcome': {
        'subject': 'Welcome to Padosi Politics!',
        'body': '''
Hello {{ name }},

Welcome to Padosi Politics - your society's complaint management system!

You have been registered as a {{ role }} for {{ society_name }}.

Your account details:
- Email: {{ email }}
- Flat: {{ flat_number }}

You can now:
- File complaints about society issues
- Vote on complaints you agree with
- Track the status of your complaints
- Receive notifications about updates

Login at: http://localhost:5173

Best regards,
The Padosi Politics Team
'''
    },
    'complaint_filed': {
        'subject': 'New Complaint Filed: {{ title }}',
        'body': '''
Hello {{ name }},

A new complaint has been filed in your society:

Title: {{ title }}
Category: {{ category }}
Priority: {{ priority }}
Filed by: {{ filed_by }}

Description:
{{ description }}

View the complaint in your dashboard.

Best regards,
Padosi Politics
'''
    },
    'complaint_status_update': {
        'subject': 'Complaint Status Update: {{ title }}',
        'body': '''
Hello {{ name }},

Your complaint "{{ title }}" has been updated:

Previous Status: {{ old_status }}
New Status: {{ new_status }}

{% if comment %}
Comment: {{ comment }}
{% endif %}

Track your complaint in the dashboard.

Best regards,
Padosi Politics
'''
    },
    'complaint_resolved': {
        'subject': 'Complaint Resolved: {{ title }}',
        'body': '''
Hello {{ name }},

Great news! Your complaint "{{ title }}" has been resolved.

Resolution:
{{ resolution }}

Thank you for helping improve our society!

You earned {{ karma_points }} karma points for this complaint.

Best regards,
Padosi Politics
'''
    },
    'escalation_notice': {
        'subject': 'Complaint Escalated: {{ title }}',
        'body': '''
Hello {{ name }},

A complaint has been escalated and requires your attention:

Title: {{ title }}
Reason: {{ reason }}
Days Open: {{ days_open }}

Please take action as soon as possible.

Best regards,
Padosi Politics
'''
    },
    'weekly_digest': {
        'subject': 'Weekly Society Digest - {{ society_name }}',
        'body': '''
Hello {{ name }},

Here's your weekly summary for {{ society_name }}:

Complaints This Week:
- New: {{ new_complaints }}
- Resolved: {{ resolved_complaints }}
- Pending: {{ pending_complaints }}

Top Issues:
{% for issue in top_issues %}
- {{ issue }}
{% endfor %}

Your Karma: {{ karma_points }} points

Keep contributing to make our society better!

Best regards,
Padosi Politics
'''
    },
    'test_email': {
        'subject': 'Test Email from Padosi Politics',
        'body': '''
Hello {{ name }},

This is a test email from Padosi Politics application.

If you received this email, the email system is working correctly!

Timestamp: {{ timestamp }}
Server: {{ server }}

Best regards,
Padosi Politics Team
'''
    }
}


def send_email(to, template_name, **kwargs):
    """
    Send an email using a template.
    
    Args:
        to: Email address or list of addresses
        template_name: Name of the template to use
        **kwargs: Template variables
    
    Returns:
        dict: Result of the email operation
    """
    if not current_app.config.get('MAIL_SERVER'):
        logger.warning(f"Email not sent - MAIL_SERVER not configured. Would send '{template_name}' to {to}")
        return {
            'success': False,
            'message': 'Mail server not configured',
            'template': template_name,
            'to': to
        }
    
    try:
        template = TEMPLATES.get(template_name)
        if not template:
            logger.error(f"Unknown email template: {template_name}")
            return {'success': False, 'message': f'Unknown template: {template_name}'}
        
        # Render subject and body
        subject = render_template_string(template['subject'], **kwargs)
        body = render_template_string(template['body'], **kwargs)
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            body=body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        # Send email
        mail.send(msg)
        
        logger.info(f"Email sent successfully: {template_name} to {to}")
        return {
            'success': True,
            'message': 'Email sent successfully',
            'to': to,
            'subject': subject
        }
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {
            'success': False,
            'message': str(e),
            'to': to
        }


def send_email_async(to, template_name, **kwargs):
    """
    Send email asynchronously using Celery if available.
    Falls back to synchronous if Celery not available.
    """
    try:
        from app.tasks.email_tasks import send_email_task
        send_email_task.delay(to, template_name, kwargs)
        return {'success': True, 'message': 'Email queued for sending'}
    except Exception:
        # Celery not available, send synchronously
        return send_email(to, template_name, **kwargs)


def send_bulk_emails(recipients, template_name, common_kwargs=None, individual_kwargs=None):
    """
    Send emails to multiple recipients.
    
    Args:
        recipients: List of email addresses
        template_name: Template to use
        common_kwargs: Variables common to all emails
        individual_kwargs: Dict mapping email to specific variables
    """
    results = []
    common_kwargs = common_kwargs or {}
    individual_kwargs = individual_kwargs or {}
    
    for recipient in recipients:
        kwargs = {**common_kwargs, **individual_kwargs.get(recipient, {})}
        result = send_email(recipient, template_name, **kwargs)
        results.append({'to': recipient, 'result': result})
    
    return results


# Notification-triggered emails
def notify_complaint_filed(complaint, society_admins):
    """Send email notifications when a new complaint is filed."""
    for admin in society_admins:
        send_email_async(
            to=admin.email,
            template_name='complaint_filed',
            name=admin.full_name or admin.username,
            title=complaint.title,
            category=complaint.category,
            priority=complaint.priority,
            filed_by='Anonymous' if complaint.is_anonymous else complaint.complainant.username,
            description=complaint.description[:500]
        )


def notify_complaint_resolved(complaint):
    """Send email when a complaint is resolved."""
    user = complaint.complainant
    send_email_async(
        to=user.email,
        template_name='complaint_resolved',
        name=user.full_name or user.username,
        title=complaint.title,
        resolution=complaint.resolution or 'Marked as resolved',
        karma_points=10  # Default karma for resolved complaint
    )


def notify_escalation(complaint, escalation, recipients):
    """Send email notifications for escalated complaints."""
    from datetime import datetime
    days_open = (datetime.utcnow() - complaint.created_at).days
    
    for recipient in recipients:
        send_email_async(
            to=recipient.email,
            template_name='escalation_notice',
            name=recipient.full_name or recipient.username,
            title=complaint.title,
            reason=escalation.reason,
            days_open=days_open
        )
