"""
User Model - Flask-Security compatible user model with karma system
"""

from datetime import datetime
from flask_security import UserMixin, RoleMixin
from app.extensions import db


# Association table for many-to-many relationship between users and roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    """Role model for RBAC."""
    __tablename__ = 'role'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class User(db.Model, UserMixin):
    """User model with Flask-Security integration."""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    
    # Personal information
    full_name = db.Column(db.String(150), nullable=False)
    flat_number = db.Column(db.String(20), nullable=False)
    wing = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(500))
    
    # Society relationship
    society_id = db.Column(db.Integer, db.ForeignKey('society.id'), nullable=False, index=True)
    society = db.relationship('Society', back_populates='residents')
    
    # Karma system
    karma_score = db.Column(db.Integer, default=0, index=True)
    
    # Flask-Security required fields
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    
    # Roles relationship
    roles = db.relationship('Role', secondary=roles_users,
                           backref=db.backref('users', lazy='dynamic'))
    
    # Complaint relationships
    complaints_filed = db.relationship('Complaint', foreign_keys='Complaint.complainant_id',
                                       back_populates='complainant', lazy='dynamic')
    complaints_against = db.relationship('Complaint', foreign_keys='Complaint.accused_user_id',
                                         back_populates='accused_user', lazy='dynamic')
    
    # Other relationships
    votes = db.relationship('ComplaintVote', back_populates='user', lazy='dynamic',
                           cascade='all, delete-orphan')
    comments = db.relationship('ComplaintComment', back_populates='user', lazy='dynamic',
                              cascade='all, delete-orphan')
    karma_logs = db.relationship('KarmaLog', back_populates='user', lazy='dynamic',
                                cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic',
                                   cascade='all, delete-orphan')
    evidence_uploaded = db.relationship('ComplaintEvidence', back_populates='uploader', lazy='dynamic')
    escalations_initiated = db.relationship('Escalation', back_populates='escalated_by_user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)
    
    def is_admin(self):
        """Check if user is admin."""
        return self.has_role('admin')
    
    def is_secretary(self):
        """Check if user is secretary."""
        return self.has_role('secretary') or self.has_role('admin')
    
    def is_committee_member(self):
        """Check if user is committee member or above."""
        return self.has_role('committee_member') or self.is_secretary()
    
    def get_display_name(self, anonymous=False):
        """Get display name, considering anonymity."""
        if anonymous:
            return f"Anonymous ({self.wing or 'Unknown Wing'})"
        return self.full_name
    
    def update_karma(self, points, reason, complaint_id=None):
        """Update karma score and log the change."""
        self.karma_score += points
        
        karma_log = KarmaLog(
            user_id=self.id,
            points=points,
            reason=reason,
            related_complaint_id=complaint_id
        )
        db.session.add(karma_log)
        return karma_log
    
    def to_dict(self, include_private=False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'full_name': self.full_name,
            'flat_number': self.flat_number,
            'wing': self.wing,
            'society_id': self.society_id,
            'karma_score': self.karma_score,
            'avatar_url': self.avatar_url,
            'roles': [role.name for role in self.roles],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_private:
            data.update({
                'email': self.email,
                'phone': self.phone,
                'active': self.active,
                'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
                'complaints_filed_count': self.complaints_filed.count(),
                'complaints_against_count': self.complaints_against.count()
            })
        
        return data
    
    def to_public_dict(self):
        """Public info only - for other users."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'flat_number': self.flat_number,
            'wing': self.wing,
            'karma_score': self.karma_score,
            'avatar_url': self.avatar_url
        }


# Import KarmaLog here to avoid circular imports
from app.models.karma import KarmaLog
