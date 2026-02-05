"""
Escalations API - Complaint escalation management
"""

from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import (
    Complaint, ComplaintStatus, Escalation, 
    User, Notification, NotificationType, KarmaLog, KarmaReason
)
from app.utils import (
    jwt_required_custom, get_current_user, committee_required,
    APIResponse, paginate_query, get_pagination_params,
    validate_request, EscalationSchema
)

escalations_bp = Blueprint('escalations', __name__)


@escalations_bp.route('', methods=['GET'])
@committee_required
def list_escalations():
    """List all escalations (Committee/Secretary only)."""
    user = get_current_user()
    page, per_page = get_pagination_params()
    
    # Build query
    query = Escalation.query.join(Complaint).filter(
        Complaint.society_id == user.society_id
    )
    
    # Filter by acknowledgment status
    acknowledged = request.args.get('acknowledged')
    if acknowledged is not None:
        query = query.filter(Escalation.is_acknowledged == (acknowledged.lower() == 'true'))
    
    # Filter by escalation level
    level = request.args.get('level')
    if level:
        query = query.filter(Escalation.escalated_to == level)
    
    query = query.order_by(Escalation.escalated_at.desc())
    pagination = paginate_query(query, page, per_page)
    
    return jsonify({
        'success': True,
        'data': [{
            **e.to_dict(),
            'complaint': e.complaint.to_list_dict(user)
        } for e in pagination['items']],
        'pagination': {
            'total': pagination['total'],
            'pages': pagination['pages'],
            'page': pagination['page'],
            'per_page': pagination['per_page']
        }
    }), 200


@escalations_bp.route('/complaints/<int:complaint_id>/escalate', methods=['POST'])
@jwt_required_custom
def escalate_complaint(complaint_id):
    """Escalate a complaint."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Verify same society
    if complaint.society_id != user.society_id and not user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    # Only complainant or committee can escalate
    if complaint.complainant_id != user.id and not user.is_committee_member():
        return APIResponse.error('You cannot escalate this complaint', 403)
    
    # Can't escalate resolved/closed complaints
    if complaint.status in [ComplaintStatus.RESOLVED.value, ComplaintStatus.CLOSED.value]:
        return APIResponse.error('Cannot escalate resolved or closed complaints', 400)
    
    data, errors = validate_request(EscalationSchema)
    if errors:
        return APIResponse.error('Validation failed', 400, errors)
    
    try:
        escalation = Escalation(
            complaint_id=complaint.id,
            escalated_by_id=user.id,
            escalated_to=data['escalate_to'],
            reason=data['reason'].strip(),
            previous_status=complaint.status,
            is_auto_escalated=False
        )
        
        # Update complaint status
        complaint.status = ComplaintStatus.ESCALATED.value
        complaint.updated_at = db.func.now()
        
        db.session.add(escalation)
        
        # Find and notify appropriate users based on escalation level
        target_roles = {
            'secretary': ['secretary', 'admin'],
            'committee': ['committee_member', 'secretary', 'admin'],
            'legal': ['admin']
        }
        
        roles_to_notify = target_roles.get(data['escalate_to'], ['admin'])
        
        # Get users to notify
        from sqlalchemy import or_
        targets = User.query.join(User.roles).filter(
            User.society_id == user.society_id,
            User.active == True,
            or_(*[User.roles.any(name=role) for role in roles_to_notify])
        ).all()
        
        for target in targets:
            Notification.create_notification(
                user_id=target.id,
                title=f'Complaint Escalated to {data["escalate_to"].title()}',
                message=f'Complaint "{complaint.title}" has been escalated. Reason: {data["reason"][:100]}...',
                notification_type=NotificationType.ESCALATION,
                complaint_id=complaint.id,
                action_url=f'/complaints/{complaint.id}'
            )
        
        # Notify complainant about escalation
        if complaint.complainant_id != user.id:
            Notification.create_notification(
                user_id=complaint.complainant_id,
                title='Your Complaint Has Been Escalated',
                message=f'Your complaint "{complaint.title}" has been escalated to {data["escalate_to"]}',
                notification_type=NotificationType.ESCALATION,
                complaint_id=complaint.id
            )
        
        # Apply karma penalty for escalation (indicates system failure to resolve)
        if complaint.accused_user_id:
            complaint.accused_user.update_karma(
                KarmaLog.get_points_for_reason(KarmaReason.ESCALATION_PENALTY),
                KarmaReason.ESCALATION_PENALTY,
                complaint.id
            )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Complaint escalated to {data["escalate_to"]} successfully',
            'data': escalation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to escalate complaint', 500)


@escalations_bp.route('/<int:id>/acknowledge', methods=['PATCH'])
@committee_required
def acknowledge_escalation(id):
    """Acknowledge an escalation."""
    user = get_current_user()
    escalation = Escalation.query.get_or_404(id)
    
    # Verify same society
    if escalation.complaint.society_id != user.society_id and not user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    if escalation.is_acknowledged:
        return APIResponse.error('Escalation already acknowledged', 400)
    
    data = request.get_json() or {}
    
    try:
        escalation.acknowledge(data.get('response_note'))
        
        # Notify complainant
        Notification.create_notification(
            user_id=escalation.complaint.complainant_id,
            title='Escalation Acknowledged',
            message=f'Your escalated complaint "{escalation.complaint.title}" has been acknowledged by {user.full_name}',
            notification_type=NotificationType.ESCALATION,
            complaint_id=escalation.complaint_id
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Escalation acknowledged successfully',
            'data': escalation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to acknowledge escalation', 500)


@escalations_bp.route('/complaints/<int:complaint_id>/escalations', methods=['GET'])
@jwt_required_custom
def get_complaint_escalations(complaint_id):
    """Get all escalations for a complaint."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Verify same society
    if complaint.society_id != user.society_id and not user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    escalations = Escalation.query.filter_by(complaint_id=complaint_id)\
        .order_by(Escalation.escalated_at.desc()).all()
    
    return jsonify({
        'success': True,
        'data': [e.to_dict() for e in escalations]
    }), 200
