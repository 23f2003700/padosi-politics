"""
Notification Model - User notifications system
"""

from datetime import datetime
from app.extensions import db


class NotificationType:
    """Notification types."""
    COMPLAINT = 'complaint'
    VOTE = 'vote'
    COMMENT = 'comment'
    ESCALATION = 'escalation'
    KARMA = 'karma'
    SYSTEM = 'system'
    REMINDER = 'reminder'


class Notification(db.Model):
    """User notification model."""
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default=NotificationType.SYSTEM, index=True)
    
    # Related entities (optional)
    related_complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=True)
    related_user_id = db.Column(db.Integer, nullable=True)
    
    # Action URL for frontend navigation
    action_url = db.Column(db.String(500))
    
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User', back_populates='notifications')
    complaint = db.relationship('Complaint')
    
    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    @staticmethod
    def create_notification(user_id, title, message, notification_type=NotificationType.SYSTEM,
                           complaint_id=None, action_url=None):
        """Helper method to create a notification."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_complaint_id=complaint_id,
            action_url=action_url
        )
        db.session.add(notification)
        return notification
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications for a user."""
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user."""
        Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        db.session.commit()
    
    @staticmethod
    def cleanup_old_notifications(days=30):
        """Delete old read notifications."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = Notification.query.filter(
            Notification.is_read == True,
            Notification.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        return deleted
    
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'related_complaint_id': self.related_complaint_id,
            'action_url': self.action_url,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
