"""
Society Model - Represents residential societies/apartments
"""

from datetime import datetime
from app.extensions import db


class Society(db.Model):
    """Society/Apartment complex model."""
    __tablename__ = 'society'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    address = db.Column(db.Text)
    city = db.Column(db.String(100), index=True)
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    total_flats = db.Column(db.Integer, default=0)
    
    # Contact info
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(20))
    
    # Settings
    allow_anonymous_complaints = db.Column(db.Boolean, default=True)
    auto_escalate_days = db.Column(db.Integer, default=7)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    residents = db.relationship('User', back_populates='society', lazy='dynamic')
    complaints = db.relationship('Complaint', back_populates='society', lazy='dynamic')
    
    def __repr__(self):
        return f'<Society {self.name}>'
    
    @property
    def total_residents(self):
        """Get total active residents count."""
        return self.residents.filter_by(active=True).count()
    
    @property
    def total_complaints(self):
        """Get total complaints count."""
        return self.complaints.count()
    
    @property
    def open_complaints_count(self):
        """Get open complaints count."""
        return self.complaints.filter_by(status='open').count()
    
    @property
    def average_karma(self):
        """Calculate average karma of all residents."""
        from sqlalchemy import func
        result = db.session.query(func.avg(User.karma_score))\
            .filter(User.society_id == self.id, User.active == True).scalar()
        return round(result or 0, 2)
    
    def get_leaderboard(self, limit=10, order='desc'):
        """Get karma leaderboard for this society."""
        query = self.residents.filter_by(active=True)
        if order == 'desc':
            query = query.order_by(User.karma_score.desc())
        else:
            query = query.order_by(User.karma_score.asc())
        return query.limit(limit).all()
    
    def get_stats(self):
        """Get comprehensive society statistics."""
        from sqlalchemy import func
        from app.models.complaint import Complaint
        
        # Category-wise complaints
        category_stats = db.session.query(
            Complaint.category,
            func.count(Complaint.id)
        ).filter(Complaint.society_id == self.id)\
         .group_by(Complaint.category).all()
        
        # Status-wise complaints
        status_stats = db.session.query(
            Complaint.status,
            func.count(Complaint.id)
        ).filter(Complaint.society_id == self.id)\
         .group_by(Complaint.status).all()
        
        # Resolution rate
        total = self.complaints.count()
        resolved = self.complaints.filter_by(status='resolved').count()
        resolution_rate = (resolved / total * 100) if total > 0 else 0
        
        return {
            'total_residents': self.total_residents,
            'total_complaints': total,
            'open_complaints': self.open_complaints_count,
            'resolved_complaints': resolved,
            'resolution_rate': round(resolution_rate, 2),
            'average_karma': self.average_karma,
            'category_wise': dict(category_stats),
            'status_wise': dict(status_stats)
        }
    
    def to_dict(self, include_stats=False):
        """Convert society to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'total_flats': self.total_flats,
            'total_residents': self.total_residents,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'allow_anonymous_complaints': self.allow_anonymous_complaints,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_stats:
            data['stats'] = self.get_stats()
        
        return data


# Import User at the end to avoid circular imports
from app.models.user import User
