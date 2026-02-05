"""
Models Package - Export all models and user_datastore
"""

from flask_security import SQLAlchemyUserDatastore

from app.extensions import db
from app.models.user import User, Role, roles_users
from app.models.society import Society
from app.models.complaint import (
    Complaint,
    ComplaintEvidence,
    ComplaintVote,
    ComplaintComment,
    ComplaintCategory,
    ComplaintStatus,
    ComplaintPriority
)
from app.models.escalation import Escalation, EscalationLevel
from app.models.karma import KarmaLog, KarmaReason
from app.models.notification import Notification, NotificationType

# Flask-Security user datastore
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

__all__ = [
    'db',
    'user_datastore',
    'User',
    'Role',
    'roles_users',
    'Society',
    'Complaint',
    'ComplaintEvidence',
    'ComplaintVote',
    'ComplaintComment',
    'ComplaintCategory',
    'ComplaintStatus',
    'ComplaintPriority',
    'Escalation',
    'EscalationLevel',
    'KarmaLog',
    'KarmaReason',
    'Notification',
    'NotificationType'
]
