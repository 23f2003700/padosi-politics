"""
Notifications API - User notification management
"""

from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Notification
from app.utils import (
    jwt_required_custom, get_current_user,
    APIResponse, paginate_query, get_pagination_params
)

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('', methods=['GET'])
@jwt_required_custom
def get_notifications():
    """Get user's notifications."""
    user = get_current_user()
    page, per_page = get_pagination_params()
    
    # Filter options
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    notification_type = request.args.get('type')
    
    # Build query
    query = Notification.query.filter_by(user_id=user.id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    if notification_type:
        query = query.filter_by(notification_type=notification_type)
    
    query = query.order_by(Notification.created_at.desc())
    
    pagination = paginate_query(query, page, per_page)
    
    # Get unread count
    unread_count = Notification.get_unread_count(user.id)
    
    return jsonify({
        'success': True,
        'data': [n.to_dict() for n in pagination['items']],
        'unread_count': unread_count,
        'pagination': {
            'total': pagination['total'],
            'pages': pagination['pages'],
            'page': pagination['page'],
            'per_page': pagination['per_page']
        }
    }), 200


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required_custom
def get_unread_count():
    """Get count of unread notifications."""
    user = get_current_user()
    count = Notification.get_unread_count(user.id)
    
    return jsonify({
        'success': True,
        'data': {
            'unread_count': count
        }
    }), 200


@notifications_bp.route('/<int:id>/read', methods=['PATCH'])
@jwt_required_custom
def mark_as_read(id):
    """Mark a notification as read."""
    user = get_current_user()
    notification = Notification.query.get_or_404(id)
    
    # Verify ownership
    if notification.user_id != user.id:
        return APIResponse.error('Access denied', 403)
    
    try:
        notification.mark_as_read()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read',
            'data': notification.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to update notification', 500)


@notifications_bp.route('/mark-all-read', methods=['PATCH'])
@jwt_required_custom
def mark_all_as_read():
    """Mark all notifications as read."""
    user = get_current_user()
    
    try:
        Notification.mark_all_as_read(user.id)
        
        return jsonify({
            'success': True,
            'message': 'All notifications marked as read'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to update notifications', 500)


@notifications_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_custom
def delete_notification(id):
    """Delete a notification."""
    user = get_current_user()
    notification = Notification.query.get_or_404(id)
    
    # Verify ownership
    if notification.user_id != user.id:
        return APIResponse.error('Access denied', 403)
    
    try:
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification deleted'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to delete notification', 500)


@notifications_bp.route('/clear-all', methods=['DELETE'])
@jwt_required_custom
def clear_all_notifications():
    """Clear all notifications for user."""
    user = get_current_user()
    
    try:
        Notification.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All notifications cleared'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to clear notifications', 500)
