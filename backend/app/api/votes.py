"""
Votes API - Voting on complaints
"""

from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Complaint, ComplaintVote, Notification, NotificationType, KarmaLog, KarmaReason
from app.utils import (
    jwt_required_custom, get_current_user, same_society_required,
    APIResponse, validate_request, VoteSchema
)

votes_bp = Blueprint('votes', __name__)


@votes_bp.route('/complaints/<int:complaint_id>/vote', methods=['POST'])
@jwt_required_custom
def vote_on_complaint(complaint_id):
    """Vote on a complaint (support or oppose)."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Verify same society
    if complaint.society_id != user.society_id and not user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    # Can't vote on own complaint
    if complaint.complainant_id == user.id:
        return APIResponse.error('You cannot vote on your own complaint', 400)
    
    data, errors = validate_request(VoteSchema)
    if errors:
        return APIResponse.error('Validation failed', 400, errors)
    
    try:
        vote, is_new = complaint.add_vote(
            user,
            data['vote_type'],
            data.get('is_anonymous', True)
        )
        
        # Award karma for helpful vote (only on first vote)
        if is_new:
            user.update_karma(
                KarmaLog.get_points_for_reason(KarmaReason.HELPFUL_VOTE),
                KarmaReason.HELPFUL_VOTE,
                complaint.id
            )
            
            # Notify complainant about new support (if not anonymous)
            if data['vote_type'] == 'support' and not data.get('is_anonymous', True):
                Notification.create_notification(
                    user_id=complaint.complainant_id,
                    title='New Support on Your Complaint',
                    message=f'{user.full_name} supported your complaint "{complaint.title}"',
                    notification_type=NotificationType.VOTE,
                    complaint_id=complaint.id
                )
        
        db.session.commit()
        
        action = 'recorded' if is_new else 'updated'
        return jsonify({
            'success': True,
            'message': f'Vote {action} successfully',
            'data': {
                'vote_type': vote.vote_type,
                'support_count': complaint.support_count,
                'oppose_count': complaint.oppose_count
            }
        }), 201 if is_new else 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to record vote', 500)


@votes_bp.route('/complaints/<int:complaint_id>/vote', methods=['DELETE'])
@jwt_required_custom
def remove_vote(complaint_id):
    """Remove vote from a complaint."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Verify same society
    if complaint.society_id != user.society_id and not user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    try:
        removed = complaint.remove_vote(user)
        
        if not removed:
            return APIResponse.error('You have not voted on this complaint', 404)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vote removed successfully',
            'data': {
                'support_count': complaint.support_count,
                'oppose_count': complaint.oppose_count
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to remove vote', 500)


@votes_bp.route('/complaints/<int:complaint_id>/vote', methods=['GET'])
@jwt_required_custom
def get_my_vote(complaint_id):
    """Get current user's vote on a complaint."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(complaint_id)
    
    vote = complaint.get_user_vote(user.id)
    
    return jsonify({
        'success': True,
        'data': {
            'has_voted': vote is not None,
            'vote_type': vote.vote_type if vote else None,
            'is_anonymous': vote.is_anonymous if vote else None
        }
    }), 200


@votes_bp.route('/complaints/<int:complaint_id>/votes', methods=['GET'])
@jwt_required_custom
def get_complaint_votes(complaint_id):
    """Get all votes on a complaint (secretary only sees details)."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Verify same society
    if complaint.society_id != user.society_id and not user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    votes = ComplaintVote.query.filter_by(complaint_id=complaint_id).all()
    
    # Only secretary can see voter details
    show_user = user.is_secretary()
    
    return jsonify({
        'success': True,
        'data': {
            'support_count': complaint.support_count,
            'oppose_count': complaint.oppose_count,
            'total_votes': len(votes),
            'votes': [v.to_dict(show_user=show_user) for v in votes]
        }
    }), 200
