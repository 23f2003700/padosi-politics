"""
Karma Model - Track user reputation points
"""

from datetime import datetime
from app.extensions import db


class KarmaReason:
    """Karma change reasons."""
    COMPLAINT_FILED = 'complaint_filed'
    COMPLAINT_RESOLVED = 'complaint_resolved'
    COMPLAINT_AGAINST_RESOLVED = 'complaint_against_resolved'
    REPEAT_OFFENDER = 'repeat_offender'
    HELPFUL_VOTE = 'helpful_vote'
    FALSE_COMPLAINT = 'false_complaint'
    COMMUNITY_CONTRIBUTION = 'community_contribution'
    MONTHLY_BONUS = 'monthly_bonus'
    ESCALATION_PENALTY = 'escalation_penalty'
    MANUAL_ADJUSTMENT = 'manual_adjustment'


class KarmaLog(db.Model):
    """Log of karma point changes."""
    __tablename__ = 'karma_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    points = db.Column(db.Integer, nullable=False)  # Can be positive or negative
    reason = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    
    related_complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User', back_populates='karma_logs')
    complaint = db.relationship('Complaint', back_populates='karma_logs')
    
    def __repr__(self):
        return f'<KarmaLog {self.points:+d} for User {self.user_id}: {self.reason}>'
    
    @staticmethod
    def get_points_for_reason(reason):
        """Get default points for a karma reason."""
        points_map = {
            KarmaReason.COMPLAINT_FILED: 1,
            KarmaReason.COMPLAINT_RESOLVED: 10,
            KarmaReason.COMPLAINT_AGAINST_RESOLVED: -5,
            KarmaReason.REPEAT_OFFENDER: -50,
            KarmaReason.HELPFUL_VOTE: 2,
            KarmaReason.FALSE_COMPLAINT: -20,
            KarmaReason.COMMUNITY_CONTRIBUTION: 15,
            KarmaReason.MONTHLY_BONUS: 10,
            KarmaReason.ESCALATION_PENALTY: -10,
        }
        return points_map.get(reason, 0)
    
    @staticmethod
    def get_user_karma_history(user_id, limit=50):
        """Get karma history for a user."""
        return KarmaLog.query.filter_by(user_id=user_id)\
            .order_by(KarmaLog.created_at.desc())\
            .limit(limit).all()
    
    @staticmethod
    def calculate_monthly_karma(user_id, year, month):
        """Calculate total karma change for a specific month."""
        from sqlalchemy import func, extract
        
        result = db.session.query(func.sum(KarmaLog.points))\
            .filter(
                KarmaLog.user_id == user_id,
                extract('year', KarmaLog.created_at) == year,
                extract('month', KarmaLog.created_at) == month
            ).scalar()
        
        return result or 0
    
    def to_dict(self):
        """Convert karma log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'points': self.points,
            'reason': self.reason,
            'description': self.description,
            'related_complaint_id': self.related_complaint_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
