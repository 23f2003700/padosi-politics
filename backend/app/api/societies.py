"""
Society API - Society management endpoints
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from app.extensions import db
from app.models import Society, User
from app.utils import (
    jwt_required_custom, get_current_user, admin_required,
    APIResponse, paginate_query, get_pagination_params,
    validate_request, SocietyCreateSchema
)

societies_bp = Blueprint('societies', __name__)


@societies_bp.route('', methods=['GET'])
def list_societies():
    """List all societies (public endpoint for registration)."""
    page, per_page = get_pagination_params()
    
    query = Society.query.order_by(Society.name)
    pagination = paginate_query(query, page, per_page)
    
    return jsonify({
        'success': True,
        'data': [s.to_dict() for s in pagination['items']],
        'pagination': {
            'total': pagination['total'],
            'pages': pagination['pages'],
            'page': pagination['page'],
            'per_page': pagination['per_page'],
            'has_next': pagination['has_next'],
            'has_prev': pagination['has_prev']
        }
    }), 200


@societies_bp.route('/<int:id>', methods=['GET'])
def get_society(id):
    """Get society details."""
    society = Society.query.get_or_404(id)
    
    include_stats = request.args.get('include_stats', 'false').lower() == 'true'
    
    return jsonify({
        'success': True,
        'data': society.to_dict(include_stats=include_stats)
    }), 200


@societies_bp.route('', methods=['POST'])
@admin_required
def create_society():
    """Create a new society (Admin only)."""
    data, errors = validate_request(SocietyCreateSchema)
    if errors:
        return APIResponse.error('Validation failed', 400, errors)
    
    # Check if society with same name exists in city
    existing = Society.query.filter_by(
        name=data['name'],
        city=data['city']
    ).first()
    if existing:
        return APIResponse.error('Society with this name already exists in the city', 409)
    
    try:
        society = Society(
            name=data['name'],
            address=data.get('address'),
            city=data['city'],
            state=data.get('state'),
            pincode=data.get('pincode'),
            total_flats=data.get('total_flats', 0)
        )
        db.session.add(society)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Society created successfully',
            'data': society.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to create society', 500)


@societies_bp.route('/<int:id>', methods=['PUT'])
@admin_required
def update_society(id):
    """Update society details (Admin only)."""
    society = Society.query.get_or_404(id)
    data = request.get_json() or {}
    
    # Update fields
    if 'name' in data:
        society.name = data['name']
    if 'address' in data:
        society.address = data['address']
    if 'city' in data:
        society.city = data['city']
    if 'state' in data:
        society.state = data['state']
    if 'pincode' in data:
        society.pincode = data['pincode']
    if 'total_flats' in data:
        society.total_flats = data['total_flats']
    if 'contact_email' in data:
        society.contact_email = data['contact_email']
    if 'contact_phone' in data:
        society.contact_phone = data['contact_phone']
    if 'allow_anonymous_complaints' in data:
        society.allow_anonymous_complaints = data['allow_anonymous_complaints']
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Society updated successfully',
            'data': society.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to update society', 500)


@societies_bp.route('/<int:id>/stats', methods=['GET'])
@jwt_required_custom
def get_society_stats(id):
    """Get comprehensive society statistics."""
    user = get_current_user()
    society = Society.query.get_or_404(id)
    
    # Only allow users from the same society or admins
    if user.society_id != society.id and not user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    stats = society.get_stats()
    
    return jsonify({
        'success': True,
        'data': stats
    }), 200


@societies_bp.route('/<int:id>/residents', methods=['GET'])
@jwt_required_custom
def get_society_residents(id):
    """Get list of residents in a society (for secretary/admin)."""
    user = get_current_user()
    society = Society.query.get_or_404(id)
    
    # Only secretary or admin can view full resident list
    if not user.is_secretary() and user.society_id != society.id:
        return APIResponse.error('Access denied', 403)
    
    page, per_page = get_pagination_params()
    
    query = User.query.filter_by(society_id=id, active=True).order_by(User.flat_number)
    pagination = paginate_query(query, page, per_page)
    
    # For regular users, show limited info
    if user.is_secretary():
        residents = [r.to_dict(include_private=True) for r in pagination['items']]
    else:
        residents = [r.to_public_dict() for r in pagination['items']]
    
    return jsonify({
        'success': True,
        'data': residents,
        'pagination': {
            'total': pagination['total'],
            'pages': pagination['pages'],
            'page': pagination['page'],
            'per_page': pagination['per_page']
        }
    }), 200


@societies_bp.route('/<int:id>/flats', methods=['GET'])
@jwt_required_custom
def get_society_flats(id):
    """Get list of occupied flats in society (for filing complaints)."""
    user = get_current_user()
    society = Society.query.get_or_404(id)
    
    # Only allow users from same society
    if user.society_id != society.id and not user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    # Get all occupied flats
    flats = db.session.query(
        User.flat_number,
        User.wing,
        User.full_name
    ).filter(
        User.society_id == id,
        User.active == True
    ).order_by(User.wing, User.flat_number).all()
    
    return jsonify({
        'success': True,
        'data': [
            {
                'flat_number': f.flat_number,
                'wing': f.wing,
                'resident_name': f.full_name
            } for f in flats
        ]
    }), 200
