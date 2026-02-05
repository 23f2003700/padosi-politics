"""
Escalation Model - Track complaint escalations through hierarchy
"""

from datetime import datetime
from app.extensions import db


class EscalationLevel(str):
    """Escalation levels enum."""
    SECRETARY = 'secretary'
    COMMITTEE = 'committee'
    LEGAL = 'legal'


class Escalation(db.Model):
    """Escalation tracking for complaints."""
    __tablename__ = 'escalation'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False, index=True)
    escalated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    escalated_to = db.Column(db.String(50), nullable=False)  # secretary, committee, legal
    reason = db.Column(db.Text, nullable=False)
    previous_status = db.Column(db.String(20))
    
    # Response from escalated authority
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime)
    response_note = db.Column(db.Text)
    
    # Auto-escalation flag
    is_auto_escalated = db.Column(db.Boolean, default=False)
    
    escalated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    complaint = db.relationship('Complaint', back_populates='escalations')
    escalated_by_user = db.relationship('User', back_populates='escalations_initiated')
    
    def __repr__(self):
        return f'<Escalation {self.id} for Complaint {self.complaint_id} to {self.escalated_to}>'
    
    def acknowledge(self, response_note=None):
        """Mark escalation as acknowledged."""
        self.is_acknowledged = True
        self.acknowledged_at = datetime.utcnow()
        if response_note:
            self.response_note = response_note
    
    def to_dict(self):
        """Convert escalation to dictionary."""
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'escalated_to': self.escalated_to,
            'reason': self.reason,
            'previous_status': self.previous_status,
            'is_acknowledged': self.is_acknowledged,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'response_note': self.response_note,
            'is_auto_escalated': self.is_auto_escalated,
            'escalated_at': self.escalated_at.isoformat() if self.escalated_at else None,
            'escalated_by': {
                'id': self.escalated_by_user.id,
                'name': self.escalated_by_user.full_name,
                'flat_number': self.escalated_by_user.flat_number
            } if self.escalated_by_user else None
        }
