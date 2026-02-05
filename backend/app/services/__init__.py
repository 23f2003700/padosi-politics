"""
Services Module for Padosi Politics
"""

from .email_service import (
    send_email,
    send_email_async,
    send_bulk_emails,
    notify_complaint_filed,
    notify_complaint_resolved,
    notify_escalation,
    TEMPLATES
)

__all__ = [
    'send_email',
    'send_email_async',
    'send_bulk_emails',
    'notify_complaint_filed',
    'notify_complaint_resolved',
    'notify_escalation',
    'TEMPLATES'
]
