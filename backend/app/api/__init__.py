"""
API Package - Export all blueprints
"""

from app.api.health import health_bp
from app.api.auth import auth_bp
from app.api.societies import societies_bp
from app.api.complaints import complaints_bp
from app.api.evidence import evidence_bp
from app.api.votes import votes_bp
from app.api.comments import comments_bp
from app.api.escalations import escalations_bp
from app.api.karma import karma_bp
from app.api.notifications import notifications_bp
from app.api.dashboard import dashboard_bp

__all__ = [
    'health_bp',
    'auth_bp',
    'societies_bp',
    'complaints_bp',
    'evidence_bp',
    'votes_bp',
    'comments_bp',
    'escalations_bp',
    'karma_bp',
    'notifications_bp',
    'dashboard_bp'
]
