"""
Comments API - Comment management for complaints
"""

from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Complaint, ComplaintComment, Notification, NotificationType
from app.utils import (
    jwt_required_custom, get_current_user,
    APIResponse, paginate_query, get_pagination_params,
    validate_request, CommentSchema
)

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/complaints/<int:complaint_id>/comments', methods=['GET'])
@jwt_required_custom
def get_complaint_comments(complaint_id):
    """Get all comments on a complaint."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Verify same society
    if complaint.society_id != user.society_id and not user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    page, per_page = get_pagination_params()
    
    query = ComplaintComment.query.filter_by(complaint_id=complaint_id)\
        .order_by(ComplaintComment.created_at.desc())
    
    pagination = paginate_query(query, page, per_page)
    
    return jsonify({
        'success': True,
        'data': [c.to_dict(user) for c in pagination['items']],
        'pagination': {
            'total': pagination['total'],
            'pages': pagination['pages'],
            'page': pagination['page'],
            'per_page': pagination['per_page']
        }
    }), 200


@comments_bp.route('/complaints/<int:complaint_id>/comments', methods=['POST'])
@jwt_required_custom
def add_comment(complaint_id):
    """Add a comment to a complaint."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Verify same society
    if complaint.society_id != user.society_id and not user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    data, errors = validate_request(CommentSchema)
    if errors:
        return APIResponse.error('Validation failed', 400, errors)
    
    try:
        # Determine if this is an official comment
        is_official = user.is_committee_member()
        
        comment = ComplaintComment(
            complaint_id=complaint.id,
            user_id=user.id,
            comment_text=data['comment_text'].strip(),
            is_anonymous=data.get('is_anonymous', False),
            is_official=is_official
        )
        
        db.session.add(comment)
        
        # Notify complainant about new comment (unless they're the commenter)
        if complaint.complainant_id != user.id:
            commenter_name = 'Anonymous Resident' if data.get('is_anonymous') else user.full_name
            if is_official:
                commenter_name = f'{user.full_name} (Committee)'
            
            Notification.create_notification(
                user_id=complaint.complainant_id,
                title='New Comment on Your Complaint',
                message=f'{commenter_name} commented on "{complaint.title}"',
                notification_type=NotificationType.COMMENT,
                complaint_id=complaint.id,
                action_url=f'/complaints/{complaint.id}'
            )
        
        # Notify accused user about official comments
        if is_official and complaint.accused_user_id and complaint.accused_user_id != user.id:
            Notification.create_notification(
                user_id=complaint.accused_user_id,
                title='Official Response on Complaint',
                message=f'Committee member {user.full_name} commented on complaint "{complaint.title}"',
                notification_type=NotificationType.COMMENT,
                complaint_id=complaint.id,
                action_url=f'/complaints/{complaint.id}'
            )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Comment added successfully',
            'data': comment.to_dict(user)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to add comment', 500)


@comments_bp.route('/comments/<int:id>', methods=['DELETE'])
@jwt_required_custom
def delete_comment(id):
    """Delete a comment."""
    user = get_current_user()
    comment = ComplaintComment.query.get_or_404(id)
    
    if not comment.can_be_deleted_by(user):
        return APIResponse.error('You cannot delete this comment', 403)
    
    try:
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Comment deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to delete comment', 500)


@comments_bp.route('/comments/<int:id>', methods=['PUT'])
@jwt_required_custom
def update_comment(id):
    """Update a comment (owner only)."""
    user = get_current_user()
    comment = ComplaintComment.query.get_or_404(id)
    
    # Only owner can edit
    if comment.user_id != user.id:
        return APIResponse.error('You cannot edit this comment', 403)
    
    data = request.get_json() or {}
    
    if 'comment_text' not in data:
        return APIResponse.error('Comment text is required', 400)
    
    try:
        comment.comment_text = data['comment_text'].strip()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Comment updated successfully',
            'data': comment.to_dict(user)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to update comment', 500)
