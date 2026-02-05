"""
Dashboard API - Statistics and dashboard data
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import func, and_

from app.extensions import db
from app.models import (
    Complaint, ComplaintStatus, ComplaintCategory,
    User, Notification, KarmaLog
)
from app.utils import (
    jwt_required_custom, get_current_user, secretary_required,
    APIResponse
)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required_custom
def get_dashboard_stats():
    """Get dashboard statistics for current user."""
    user = get_current_user()
    society_id = user.society_id
    
    # Get complaint counts
    total_complaints_open = Complaint.query.filter(
        Complaint.society_id == society_id,
        Complaint.status.in_([
            ComplaintStatus.OPEN.value,
            ComplaintStatus.ACKNOWLEDGED.value,
            ComplaintStatus.IN_PROGRESS.value,
            ComplaintStatus.ESCALATED.value
        ])
    ).count()
    
    total_complaints_resolved = Complaint.query.filter(
        Complaint.society_id == society_id,
        Complaint.status == ComplaintStatus.RESOLVED.value
    ).count()
    
    my_complaints_count = user.complaints_filed.count()
    
    complaints_against_me = Complaint.query.filter(
        db.or_(
            Complaint.accused_user_id == user.id,
            Complaint.accused_flat == user.flat_number
        )
    ).count()
    
    # Get society karma average
    society_karma_avg = db.session.query(func.avg(User.karma_score)).filter(
        User.society_id == society_id,
        User.active == True
    ).scalar() or 0
    
    # Get recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    new_complaints_this_week = Complaint.query.filter(
        Complaint.society_id == society_id,
        Complaint.created_at >= week_ago
    ).count()
    
    resolved_this_week = Complaint.query.filter(
        Complaint.society_id == society_id,
        Complaint.resolved_at >= week_ago
    ).count()
    
    # My karma change this week
    my_karma_change = db.session.query(func.sum(KarmaLog.points)).filter(
        KarmaLog.user_id == user.id,
        KarmaLog.created_at >= week_ago
    ).scalar() or 0
    
    # Unread notifications count
    unread_notifications = Notification.get_unread_count(user.id)
    
    return jsonify({
        'success': True,
        'data': {
            'total_complaints_open': total_complaints_open,
            'total_complaints_resolved': total_complaints_resolved,
            'my_complaints_count': my_complaints_count,
            'complaints_against_me': complaints_against_me,
            'my_karma': user.karma_score,
            'my_karma_change_this_week': my_karma_change,
            'society_karma_average': round(society_karma_avg, 2),
            'new_complaints_this_week': new_complaints_this_week,
            'resolved_this_week': resolved_this_week,
            'unread_notifications': unread_notifications
        }
    }), 200


@dashboard_bp.route('/society-stats', methods=['GET'])
@secretary_required
def get_society_stats():
    """Get comprehensive society statistics (Secretary only)."""
    user = get_current_user()
    society_id = user.society_id
    
    # Category-wise complaints
    category_stats = db.session.query(
        Complaint.category,
        func.count(Complaint.id).label('count')
    ).filter(Complaint.society_id == society_id)\
     .group_by(Complaint.category).all()
    
    # Status-wise complaints
    status_stats = db.session.query(
        Complaint.status,
        func.count(Complaint.id).label('count')
    ).filter(Complaint.society_id == society_id)\
     .group_by(Complaint.status).all()
    
    # Priority-wise complaints
    priority_stats = db.session.query(
        Complaint.priority,
        func.count(Complaint.id).label('count')
    ).filter(
        Complaint.society_id == society_id,
        Complaint.status.notin_([ComplaintStatus.RESOLVED.value, ComplaintStatus.CLOSED.value])
    ).group_by(Complaint.priority).all()
    
    # Resolution rate
    total_complaints = Complaint.query.filter_by(society_id=society_id).count()
    resolved_complaints = Complaint.query.filter_by(
        society_id=society_id,
        status=ComplaintStatus.RESOLVED.value
    ).count()
    resolution_rate = (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
    
    # Average resolution time (for resolved complaints)
    avg_resolution_time = db.session.query(
        func.avg(
            func.julianday(Complaint.resolved_at) - func.julianday(Complaint.created_at)
        )
    ).filter(
        Complaint.society_id == society_id,
        Complaint.resolved_at.isnot(None)
    ).scalar() or 0
    
    # Repeat offenders (users with 3+ resolved complaints against them)
    repeat_offenders = db.session.query(
        User.id,
        User.full_name,
        User.flat_number,
        User.karma_score,
        func.count(Complaint.id).label('complaint_count')
    ).join(Complaint, Complaint.accused_user_id == User.id)\
     .filter(
        User.society_id == society_id,
        Complaint.status == ComplaintStatus.RESOLVED.value
    ).group_by(User.id)\
     .having(func.count(Complaint.id) >= 3)\
     .order_by(func.count(Complaint.id).desc())\
     .limit(10).all()
    
    # Most active complainers
    active_complainers = db.session.query(
        User.id,
        User.full_name,
        User.flat_number,
        func.count(Complaint.id).label('complaint_count')
    ).join(Complaint, Complaint.complainant_id == User.id)\
     .filter(User.society_id == society_id)\
     .group_by(User.id)\
     .order_by(func.count(Complaint.id).desc())\
     .limit(10).all()
    
    # Monthly trends (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_trends = db.session.query(
        func.strftime('%Y-%m', Complaint.created_at).label('month'),
        func.count(Complaint.id).label('total'),
        func.sum(
            db.case((Complaint.status == ComplaintStatus.RESOLVED.value, 1), else_=0)
        ).label('resolved')
    ).filter(
        Complaint.society_id == society_id,
        Complaint.created_at >= six_months_ago
    ).group_by(func.strftime('%Y-%m', Complaint.created_at))\
     .order_by(func.strftime('%Y-%m', Complaint.created_at)).all()
    
    return jsonify({
        'success': True,
        'data': {
            'category_wise': {stat.category: stat.count for stat in category_stats},
            'status_wise': {stat.status: stat.count for stat in status_stats},
            'priority_wise': {stat.priority: stat.count for stat in priority_stats},
            'resolution_rate': round(resolution_rate, 2),
            'average_resolution_days': round(avg_resolution_time, 1),
            'total_complaints': total_complaints,
            'resolved_complaints': resolved_complaints,
            'repeat_offenders': [
                {
                    'id': r.id,
                    'full_name': r.full_name,
                    'flat_number': r.flat_number,
                    'karma_score': r.karma_score,
                    'complaint_count': r.complaint_count
                } for r in repeat_offenders
            ],
            'most_active_complainers': [
                {
                    'id': c.id,
                    'full_name': c.full_name,
                    'flat_number': c.flat_number,
                    'complaint_count': c.complaint_count
                } for c in active_complainers
            ],
            'monthly_trends': [
                {
                    'month': t.month,
                    'total': t.total,
                    'resolved': t.resolved or 0
                } for t in monthly_trends
            ]
        }
    }), 200


@dashboard_bp.route('/recent-activity', methods=['GET'])
@jwt_required_custom
def get_recent_activity():
    """Get recent activity in the society."""
    user = get_current_user()
    society_id = user.society_id
    limit = request.args.get('limit', 10, type=int)
    limit = min(limit, 50)
    
    # Recent complaints
    recent_complaints = Complaint.query.filter_by(society_id=society_id)\
        .order_by(Complaint.created_at.desc())\
        .limit(limit).all()
    
    # Recent resolutions
    recent_resolutions = Complaint.query.filter(
        Complaint.society_id == society_id,
        Complaint.resolved_at.isnot(None)
    ).order_by(Complaint.resolved_at.desc())\
     .limit(limit).all()
    
    return jsonify({
        'success': True,
        'data': {
            'recent_complaints': [c.to_list_dict(user) for c in recent_complaints],
            'recent_resolutions': [c.to_list_dict(user) for c in recent_resolutions]
        }
    }), 200
