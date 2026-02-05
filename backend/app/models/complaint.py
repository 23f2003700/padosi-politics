"""
Complaint Model - Core model for complaint management
"""

from datetime import datetime
from enum import Enum
from app.extensions import db


class ComplaintCategory(str, Enum):
    """Complaint categories enum."""
    NOISE = 'noise'
    PARKING = 'parking'
    PET = 'pet'
    MAINTENANCE = 'maintenance'
    CLEANLINESS = 'cleanliness'
    SECURITY = 'security'
    WATER = 'water'
    ELECTRICITY = 'electricity'
    HARASSMENT = 'harassment'
    OTHER = 'other'


class ComplaintStatus(str, Enum):
    """Complaint status enum."""
    OPEN = 'open'
    ACKNOWLEDGED = 'acknowledged'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    ESCALATED = 'escalated'
    CLOSED = 'closed'
    REJECTED = 'rejected'


class ComplaintPriority(str, Enum):
    """Complaint priority enum."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class Complaint(db.Model):
    """Main complaint model."""
    __tablename__ = 'complaint'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic info
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default=ComplaintCategory.OTHER.value, index=True)
    
    # Complainant (who filed)
    complainant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    complainant = db.relationship('User', foreign_keys=[complainant_id], back_populates='complaints_filed')
    
    # Accused (optional - who the complaint is against)
    accused_flat = db.Column(db.String(20))  # Can file against a flat even if user not registered
    accused_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    accused_user = db.relationship('User', foreign_keys=[accused_user_id], back_populates='complaints_against')
    
    # Society
    society_id = db.Column(db.Integer, db.ForeignKey('society.id'), nullable=False, index=True)
    society = db.relationship('Society', back_populates='complaints')
    
    # Privacy and status
    is_anonymous = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default=ComplaintStatus.OPEN.value, index=True)
    priority = db.Column(db.String(20), default=ComplaintPriority.MEDIUM.value, index=True)
    
    # Voting
    support_count = db.Column(db.Integer, default=0)
    oppose_count = db.Column(db.Integer, default=0)
    
    # Resolution
    resolution_note = db.Column(db.Text)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolved_by = db.relationship('User', foreign_keys=[resolved_by_id])
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    evidence = db.relationship('ComplaintEvidence', back_populates='complaint', 
                              cascade='all, delete-orphan', lazy='dynamic')
    votes = db.relationship('ComplaintVote', back_populates='complaint',
                           cascade='all, delete-orphan', lazy='dynamic')
    comments = db.relationship('ComplaintComment', back_populates='complaint',
                              cascade='all, delete-orphan', lazy='dynamic',
                              order_by='ComplaintComment.created_at.desc()')
    escalations = db.relationship('Escalation', back_populates='complaint',
                                 cascade='all, delete-orphan', lazy='dynamic')
    karma_logs = db.relationship('KarmaLog', back_populates='complaint', lazy='dynamic')
    
    def __repr__(self):
        return f'<Complaint {self.id}: {self.title[:30]}>'
    
    def get_complainant_display_name(self):
        """Get complainant name considering anonymity."""
        if self.is_anonymous:
            return f"Anonymous ({self.complainant.wing or 'Unknown Wing'})"
        return self.complainant.full_name
    
    def can_be_edited_by(self, user):
        """Check if user can edit this complaint."""
        # Owner can edit if still open
        if self.complainant_id == user.id and self.status == ComplaintStatus.OPEN.value:
            return True
        # Admin/secretary can always edit
        return user.is_secretary()
    
    def can_be_deleted_by(self, user):
        """Check if user can delete this complaint."""
        # Owner can delete if still open
        if self.complainant_id == user.id and self.status == ComplaintStatus.OPEN.value:
            return True
        # Admin can always delete
        return user.is_admin()
    
    def can_change_status(self, user):
        """Check if user can change complaint status."""
        return user.is_committee_member()
    
    def update_status(self, new_status, user, resolution_note=None):
        """Update complaint status with tracking."""
        old_status = self.status
        self.status = new_status
        
        if new_status == ComplaintStatus.RESOLVED.value:
            self.resolved_at = datetime.utcnow()
            self.resolved_by_id = user.id
            if resolution_note:
                self.resolution_note = resolution_note
        
        self.updated_at = datetime.utcnow()
        
        # Create notification for complainant
        from app.models.notification import Notification
        notification = Notification(
            user_id=self.complainant_id,
            title='Complaint Status Updated',
            message=f'Your complaint "{self.title}" status changed from {old_status} to {new_status}',
            notification_type='complaint'
        )
        db.session.add(notification)
        
        return old_status
    
    def add_vote(self, user, vote_type, is_anonymous=True):
        """Add or update a vote on this complaint."""
        existing_vote = ComplaintVote.query.filter_by(
            complaint_id=self.id,
            user_id=user.id
        ).first()
        
        if existing_vote:
            # Update existing vote
            old_type = existing_vote.vote_type
            if old_type != vote_type:
                if old_type == 'support':
                    self.support_count = max(0, self.support_count - 1)
                else:
                    self.oppose_count = max(0, self.oppose_count - 1)
                
                if vote_type == 'support':
                    self.support_count += 1
                else:
                    self.oppose_count += 1
                
                existing_vote.vote_type = vote_type
                existing_vote.is_anonymous = is_anonymous
            return existing_vote, False
        else:
            # Create new vote
            vote = ComplaintVote(
                complaint_id=self.id,
                user_id=user.id,
                vote_type=vote_type,
                is_anonymous=is_anonymous
            )
            if vote_type == 'support':
                self.support_count += 1
            else:
                self.oppose_count += 1
            db.session.add(vote)
            return vote, True
    
    def remove_vote(self, user):
        """Remove user's vote from this complaint."""
        vote = ComplaintVote.query.filter_by(
            complaint_id=self.id,
            user_id=user.id
        ).first()
        
        if vote:
            if vote.vote_type == 'support':
                self.support_count = max(0, self.support_count - 1)
            else:
                self.oppose_count = max(0, self.oppose_count - 1)
            db.session.delete(vote)
            return True
        return False
    
    def get_user_vote(self, user_id):
        """Get a specific user's vote on this complaint."""
        return ComplaintVote.query.filter_by(
            complaint_id=self.id,
            user_id=user_id
        ).first()
    
    def to_dict(self, current_user=None, include_details=False):
        """Convert complaint to dictionary."""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'accused_flat': self.accused_flat,
            'is_anonymous': self.is_anonymous,
            'status': self.status,
            'priority': self.priority,
            'support_count': self.support_count,
            'oppose_count': self.oppose_count,
            'society_id': self.society_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_note': self.resolution_note
        }
        
        # Handle complainant info (respect anonymity)
        if self.is_anonymous and (not current_user or (current_user.id != self.complainant_id and not current_user.is_secretary())):
            data['complainant'] = {
                'display_name': self.get_complainant_display_name(),
                'wing': self.complainant.wing
            }
        else:
            data['complainant'] = {
                'id': self.complainant_id,
                'display_name': self.complainant.full_name,
                'flat_number': self.complainant.flat_number,
                'wing': self.complainant.wing
            }
        
        # Accused user info (if available)
        if self.accused_user:
            data['accused_user'] = {
                'id': self.accused_user_id,
                'full_name': self.accused_user.full_name,
                'flat_number': self.accused_user.flat_number
            }
        
        # Include current user's vote if logged in
        if current_user:
            user_vote = self.get_user_vote(current_user.id)
            data['user_vote'] = user_vote.vote_type if user_vote else None
            data['can_edit'] = self.can_be_edited_by(current_user)
            data['can_delete'] = self.can_be_deleted_by(current_user)
        
        if include_details:
            data['evidence'] = [e.to_dict() for e in self.evidence.all()]
            data['comments'] = [c.to_dict(current_user) for c in self.comments.limit(10).all()]
            data['comments_count'] = self.comments.count()
            data['evidence_count'] = self.evidence.count()
            data['escalations'] = [e.to_dict() for e in self.escalations.all()]
        
        return data
    
    def to_list_dict(self, current_user=None):
        """Minimal dict for list views."""
        data = {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'support_count': self.support_count,
            'is_anonymous': self.is_anonymous,
            'accused_flat': self.accused_flat,
            'comments_count': self.comments.count(),
            'evidence_count': self.evidence.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'complainant': {
                'display_name': self.get_complainant_display_name() if self.is_anonymous else self.complainant.full_name,
                'wing': self.complainant.wing,
                'flat_number': None if self.is_anonymous else self.complainant.flat_number
            }
        }
        
        if current_user:
            user_vote = self.get_user_vote(current_user.id)
            data['user_vote'] = user_vote.vote_type if user_vote else None
        
        return data


class ComplaintEvidence(db.Model):
    """Evidence attached to complaints (images, videos, documents)."""
    __tablename__ = 'complaint_evidence'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False, index=True)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    file_url = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # image, video, audio, document
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)  # in bytes
    description = db.Column(db.String(500))
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    complaint = db.relationship('Complaint', back_populates='evidence')
    uploader = db.relationship('User', back_populates='evidence_uploaded')
    
    def __repr__(self):
        return f'<Evidence {self.id} for Complaint {self.complaint_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'description': self.description,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'uploaded_by': {
                'id': self.uploader.id,
                'name': self.uploader.full_name
            } if self.uploader else None
        }


class ComplaintVote(db.Model):
    """Votes on complaints (support/oppose)."""
    __tablename__ = 'complaint_vote'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    vote_type = db.Column(db.String(10), nullable=False)  # 'support' or 'oppose'
    is_anonymous = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('complaint_id', 'user_id', name='unique_user_vote'),
    )
    
    # Relationships
    complaint = db.relationship('Complaint', back_populates='votes')
    user = db.relationship('User', back_populates='votes')
    
    def __repr__(self):
        return f'<Vote {self.vote_type} on Complaint {self.complaint_id} by User {self.user_id}>'
    
    def to_dict(self, show_user=False):
        data = {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'vote_type': self.vote_type,
            'is_anonymous': self.is_anonymous,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if show_user and not self.is_anonymous:
            data['user'] = {
                'id': self.user_id,
                'name': self.user.full_name,
                'flat_number': self.user.flat_number
            }
        
        return data


class ComplaintComment(db.Model):
    """Comments on complaints."""
    __tablename__ = 'complaint_comment'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    comment_text = db.Column(db.Text, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    is_official = db.Column(db.Boolean, default=False)  # Official response from committee
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    complaint = db.relationship('Complaint', back_populates='comments')
    user = db.relationship('User', back_populates='comments')
    
    def __repr__(self):
        return f'<Comment {self.id} on Complaint {self.complaint_id}>'
    
    def can_be_deleted_by(self, user):
        """Check if user can delete this comment."""
        return self.user_id == user.id or user.is_secretary()
    
    def to_dict(self, current_user=None):
        """Convert comment to dictionary."""
        data = {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'comment_text': self.comment_text,
            'is_anonymous': self.is_anonymous,
            'is_official': self.is_official,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Handle anonymity
        if self.is_anonymous and (not current_user or (current_user.id != self.user_id and not current_user.is_secretary())):
            data['user'] = {
                'display_name': 'Anonymous Resident',
                'wing': self.user.wing
            }
        else:
            data['user'] = {
                'id': self.user_id,
                'display_name': self.user.full_name,
                'flat_number': self.user.flat_number,
                'wing': self.user.wing
            }
        
        if current_user:
            data['can_delete'] = self.can_be_deleted_by(current_user)
        
        return data
