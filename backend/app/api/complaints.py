"""
Complaints API - CRUD operations for complaints
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_, and_, desc
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import (
    Complaint, ComplaintStatus, ComplaintCategory, ComplaintPriority,
    User, Notification, NotificationType, KarmaLog, KarmaReason,
    ComplaintEvidence
)
from app.utils import (
    jwt_required_custom, get_current_user, same_society_required, committee_required,
    APIResponse, paginate_query, get_pagination_params,
    validate_request, ComplaintCreateSchema, ComplaintUpdateSchema, ComplaintStatusUpdateSchema,
    save_uploaded_file, allowed_file
)

complaints_bp = Blueprint('complaints', __name__)


@complaints_bp.route('', methods=['GET'])
@jwt_required_custom
def list_complaints():
    """List complaints with filtering and pagination."""
    user = get_current_user()
    page, per_page = get_pagination_params()
    
    # Start with base query for user's society
    query = Complaint.query.filter_by(society_id=user.society_id)
    
    # Apply filters
    status = request.args.get('status')
    if status:
        query = query.filter(Complaint.status == status)
    
    category = request.args.get('category')
    if category:
        query = query.filter(Complaint.category == category)
    
    priority = request.args.get('priority')
    if priority:
        query = query.filter(Complaint.priority == priority)
    
    # Filter by my complaints
    my_complaints = request.args.get('my_complaints', 'false').lower() == 'true'
    if my_complaints:
        query = query.filter(Complaint.complainant_id == user.id)
    
    # Filter by complaints against me
    against_me = request.args.get('against_me', 'false').lower() == 'true'
    if against_me:
        query = query.filter(
            or_(
                Complaint.accused_user_id == user.id,
                Complaint.accused_flat == user.flat_number
            )
        )
    
    # Search
    search = request.args.get('search', '').strip()
    if search:
        search_filter = f'%{search}%'
        query = query.filter(
            or_(
                Complaint.title.ilike(search_filter),
                Complaint.description.ilike(search_filter),
                Complaint.accused_flat.ilike(search_filter)
            )
        )
    
    # Sorting
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    if sort_by == 'support_count':
        order_col = Complaint.support_count
    elif sort_by == 'priority':
        order_col = Complaint.priority
    else:
        order_col = Complaint.created_at
    
    if sort_order == 'asc':
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())
    
    # Paginate
    pagination = paginate_query(query, page, per_page)
    
    return jsonify({
        'success': True,
        'data': [c.to_list_dict(user) for c in pagination['items']],
        'pagination': {
            'total': pagination['total'],
            'pages': pagination['pages'],
            'page': pagination['page'],
            'per_page': pagination['per_page'],
            'has_next': pagination['has_next'],
            'has_prev': pagination['has_prev']
        }
    }), 200


@complaints_bp.route('/<int:id>', methods=['GET'])
@jwt_required_custom
@same_society_required
def get_complaint(id):
    """Get complaint details."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(id)
    
    return jsonify({
        'success': True,
        'data': complaint.to_dict(current_user=user, include_details=True)
    }), 200


@complaints_bp.route('', methods=['POST'])
@jwt_required_custom
def create_complaint():
    """Create a new complaint."""
    user = get_current_user()
    
    # Handle both JSON and FormData (multipart)
    if request.content_type and 'multipart/form-data' in request.content_type:
        # FormData from file upload
        data = {
            'title': request.form.get('title', ''),
            'description': request.form.get('description', ''),
            'category': request.form.get('category', ''),
            'priority': request.form.get('priority', 'medium'),
            'is_anonymous': request.form.get('is_anonymous', 'false').lower() in ('true', '1', 'yes'),
            'accused_flat': request.form.get('accused_flat', '')
        }
        # Manual validation for FormData
        errors = {}
        if not data['title'] or len(data['title'].strip()) < 5:
            errors['title'] = ['Title must be at least 5 characters']
        if not data['description'] or len(data['description'].strip()) < 20:
            errors['description'] = ['Description must be at least 20 characters']
        if not data['category']:
            errors['category'] = ['Category is required']
        if errors:
            return APIResponse.error('Validation failed', 400, errors)
    else:
        # JSON request
        data, errors = validate_request(ComplaintCreateSchema)
        if errors:
            return APIResponse.error('Validation failed', 400, errors)
    
    # Check if society allows anonymous complaints
    if data.get('is_anonymous') and not user.society.allow_anonymous_complaints:
        return APIResponse.error('Anonymous complaints are not allowed in your society', 400)
    
    # Find accused user if flat number provided
    accused_user_id = None
    if data.get('accused_flat'):
        accused_user = User.query.filter_by(
            society_id=user.society_id,
            flat_number=data['accused_flat'].upper()
        ).first()
        if accused_user:
            accused_user_id = accused_user.id
    
    try:
        complaint = Complaint(
            title=data['title'].strip(),
            description=data['description'].strip(),
            category=data['category'],
            complainant_id=user.id,
            accused_flat=data.get('accused_flat', '').upper() if data.get('accused_flat') else None,
            accused_user_id=accused_user_id,
            society_id=user.society_id,
            is_anonymous=data.get('is_anonymous', False),
            priority=data.get('priority', ComplaintPriority.MEDIUM.value),
            status=ComplaintStatus.OPEN.value
        )
        
        db.session.add(complaint)
        db.session.flush()  # Get the complaint ID
        
        # Handle file uploads (evidence)
        uploaded_evidence = []
        if 'evidence' in request.files:
            files = request.files.getlist('evidence')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    try:
                        file_url, file_type = save_uploaded_file(file, f'evidence/{complaint.id}')
                        if file_url:
                            evidence = ComplaintEvidence(
                                complaint_id=complaint.id,
                                uploaded_by_id=user.id,
                                file_url=file_url,
                                file_type=file_type,
                                file_name=secure_filename(file.filename),
                                file_size=file.content_length or 0
                            )
                            db.session.add(evidence)
                            uploaded_evidence.append(evidence)
                    except Exception as e:
                        current_app.logger.error(f'Failed to save evidence file: {str(e)}')
        
        # Award karma for filing a complaint
        user.update_karma(
            KarmaLog.get_points_for_reason(KarmaReason.COMPLAINT_FILED),
            KarmaReason.COMPLAINT_FILED,
            complaint.id
        )
        
        # Notify accused user if identified
        if accused_user_id and accused_user_id != user.id:
            complainant_name = 'Anonymous Resident' if data.get('is_anonymous') else user.full_name
            Notification.create_notification(
                user_id=accused_user_id,
                title='New Complaint Filed',
                message=f'A complaint "{complaint.title}" has been filed regarding your flat by {complainant_name}',
                notification_type=NotificationType.COMPLAINT,
                complaint_id=complaint.id,
                action_url=f'/complaints/{complaint.id}'
            )
        
        # Notify society secretary about high priority complaints
        if data.get('priority') in ['high', 'critical']:
            secretaries = User.query.join(User.roles).filter(
                User.society_id == user.society_id,
                User.active == True
            ).filter(
                or_(
                    User.roles.any(name='secretary'),
                    User.roles.any(name='admin')
                )
            ).all()
            
            for secretary in secretaries:
                Notification.create_notification(
                    user_id=secretary.id,
                    title='High Priority Complaint Filed',
                    message=f'A {data["priority"]} priority complaint "{complaint.title}" requires attention',
                    notification_type=NotificationType.COMPLAINT,
                    complaint_id=complaint.id,
                    action_url=f'/complaints/{complaint.id}'
                )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Complaint filed successfully',
            'data': complaint.to_dict(current_user=user)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Create complaint error: {str(e)}')
        return APIResponse.error('Failed to file complaint', 500)


@complaints_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_custom
@same_society_required
def update_complaint(id):
    """Update a complaint."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(id)
    
    # Check permissions
    if not complaint.can_be_edited_by(user):
        return APIResponse.error('You do not have permission to edit this complaint', 403)
    
    data, errors = validate_request(ComplaintUpdateSchema, partial=True)
    if errors:
        return APIResponse.error('Validation failed', 400, errors)
    
    try:
        if 'title' in data:
            complaint.title = data['title'].strip()
        if 'description' in data:
            complaint.description = data['description'].strip()
        if 'category' in data:
            complaint.category = data['category']
        if 'priority' in data:
            complaint.priority = data['priority']
        
        complaint.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Complaint updated successfully',
            'data': complaint.to_dict(current_user=user)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to update complaint', 500)


@complaints_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_custom
@same_society_required
def delete_complaint(id):
    """Delete a complaint."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(id)
    
    if not complaint.can_be_deleted_by(user):
        return APIResponse.error('You do not have permission to delete this complaint', 403)
    
    try:
        db.session.delete(complaint)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Complaint deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to delete complaint', 500)


@complaints_bp.route('/<int:id>/status', methods=['PATCH'])
@committee_required
@same_society_required
def update_complaint_status(id):
    """Update complaint status (Committee/Secretary only)."""
    user = get_current_user()
    complaint = Complaint.query.get_or_404(id)
    
    data, errors = validate_request(ComplaintStatusUpdateSchema)
    if errors:
        return APIResponse.error('Validation failed', 400, errors)
    
    old_status = complaint.status
    new_status = data['status']
    
    try:
        complaint.update_status(new_status, user, data.get('resolution_note'))
        
        # Handle karma changes based on status
        if new_status == ComplaintStatus.RESOLVED.value:
            # Reward complainant for successful resolution
            complaint.complainant.update_karma(
                KarmaLog.get_points_for_reason(KarmaReason.COMPLAINT_RESOLVED),
                KarmaReason.COMPLAINT_RESOLVED,
                complaint.id
            )
            
            # Penalize accused if complaint was valid
            if complaint.accused_user:
                complaint.accused_user.update_karma(
                    KarmaLog.get_points_for_reason(KarmaReason.COMPLAINT_AGAINST_RESOLVED),
                    KarmaReason.COMPLAINT_AGAINST_RESOLVED,
                    complaint.id
                )
                
                # Check for repeat offender
                resolved_against = Complaint.query.filter(
                    Complaint.accused_user_id == complaint.accused_user_id,
                    Complaint.status == ComplaintStatus.RESOLVED.value
                ).count()
                
                if resolved_against >= 3:
                    complaint.accused_user.update_karma(
                        KarmaLog.get_points_for_reason(KarmaReason.REPEAT_OFFENDER),
                        KarmaReason.REPEAT_OFFENDER,
                        complaint.id
                    )
        
        elif new_status == ComplaintStatus.REJECTED.value:
            # Penalize complainant for false complaint
            complaint.complainant.update_karma(
                KarmaLog.get_points_for_reason(KarmaReason.FALSE_COMPLAINT),
                KarmaReason.FALSE_COMPLAINT,
                complaint.id
            )
        
        # Notify relevant parties
        if complaint.accused_user_id:
            Notification.create_notification(
                user_id=complaint.accused_user_id,
                title='Complaint Status Updated',
                message=f'Complaint "{complaint.title}" status changed to {new_status}',
                notification_type=NotificationType.COMPLAINT,
                complaint_id=complaint.id
            )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Complaint status updated from {old_status} to {new_status}',
            'data': complaint.to_dict(current_user=user)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Status update error: {str(e)}')
        return APIResponse.error('Failed to update status', 500)


@complaints_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get available complaint categories."""
    return jsonify({
        'success': True,
        'data': [{'value': c.value, 'label': c.value.replace('_', ' ').title()} 
                 for c in ComplaintCategory]
    }), 200


@complaints_bp.route('/statuses', methods=['GET'])
def get_statuses():
    """Get available complaint statuses."""
    return jsonify({
        'success': True,
        'data': [{'value': s.value, 'label': s.value.replace('_', ' ').title()} 
                 for s in ComplaintStatus]
    }), 200


@complaints_bp.route('/priorities', methods=['GET'])
def get_priorities():
    """Get available complaint priorities."""
    return jsonify({
        'success': True,
        'data': [{'value': p.value, 'label': p.value.title()} 
                 for p in ComplaintPriority]
    }), 200
