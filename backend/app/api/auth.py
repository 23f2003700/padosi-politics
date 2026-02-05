"""
Authentication API - User registration, login, logout, profile management
"""

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, limiter
from app.models import User, Society, Role, user_datastore, Notification, NotificationType
from app.utils import (
    jwt_required_custom, get_current_user, validate_json,
    APIResponse, validate_request,
    UserRegistrationSchema, UserLoginSchema, UserUpdateSchema
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register a new user."""
    # Validate request data
    data, errors = validate_request(UserRegistrationSchema)
    if errors:
        return APIResponse.error('Validation failed', 400, errors)
    
    # Check if email already exists
    if User.query.filter_by(email=data['email'].lower()).first():
        return APIResponse.error('Email already registered', 409)
    
    # Verify society exists
    society = Society.query.get(data['society_id'])
    if not society:
        return APIResponse.error('Society not found', 404)
    
    # Check if flat number already taken in this society
    existing_flat = User.query.filter_by(
        society_id=data['society_id'],
        flat_number=data['flat_number'].upper()
    ).first()
    if existing_flat:
        return APIResponse.error('This flat is already registered in the society', 409)
    
    try:
        # Create user with Flask-Security
        user = user_datastore.create_user(
            email=data['email'].lower(),
            password=generate_password_hash(data['password']),
            full_name=data['full_name'].strip(),
            flat_number=data['flat_number'].upper(),
            wing=data.get('wing', '').strip() if data.get('wing') else None,
            society_id=data['society_id'],
            phone=data.get('phone'),
            fs_uniquifier=str(uuid.uuid4()),
            karma_score=0
        )
        
        # Assign default resident role
        resident_role = Role.query.filter_by(name='resident').first()
        if resident_role:
            user_datastore.add_role_to_user(user, resident_role)
        
        db.session.commit()
        
        # Create welcome notification
        Notification.create_notification(
            user_id=user.id,
            title='Welcome to Padosi Politics!',
            message=f'Welcome to {society.name}. Start by exploring complaints in your society.',
            notification_type=NotificationType.SYSTEM
        )
        db.session.commit()
        
        # Generate tokens (identity must be string in flask-jwt-extended 4.x)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'data': {
                'user': user.to_dict(include_private=True),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Registration error: {str(e)}')
        return APIResponse.error('Registration failed. Please try again.', 500)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate user and return tokens."""
    data, errors = validate_request(UserLoginSchema)
    if errors:
        return APIResponse.error('Validation failed', 400, errors)
    
    user = User.query.filter_by(email=data['email'].lower()).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return APIResponse.error('Invalid email or password', 401)
    
    if not user.active:
        return APIResponse.error('Account is deactivated. Contact administrator.', 403)
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    db.session.commit()
    
    # Generate tokens (identity must be string in flask-jwt-extended 4.x)
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'data': {
            'user': user.to_dict(include_private=True),
            'society': user.society.to_dict() if user.society else None,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 86400  # 24 hours in seconds
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required_custom
def logout():
    """Logout user (client should discard tokens)."""
    # In a production app, you might want to blacklist the token
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required_custom
def refresh_token():
    """Refresh access token."""
    current_user = get_current_user()
    access_token = create_access_token(identity=str(current_user.id))
    
    return jsonify({
        'success': True,
        'data': {
            'access_token': access_token,
            'token_type': 'Bearer'
        }
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required_custom
def get_profile():
    """Get current user's profile."""
    user = get_current_user()
    
    # Get additional stats
    complaints_filed = user.complaints_filed.count()
    complaints_against = user.complaints_against.count()
    unread_notifications = Notification.get_unread_count(user.id)
    
    profile_data = user.to_dict(include_private=True)
    profile_data.update({
        'complaints_filed': complaints_filed,
        'complaints_against': complaints_against,
        'unread_notifications': unread_notifications,
        'society': user.society.to_dict() if user.society else None
    })
    
    return jsonify({
        'success': True,
        'data': profile_data
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required_custom
def update_profile():
    """Update current user's profile."""
    user = get_current_user()
    
    data, errors = validate_request(UserUpdateSchema, partial=True)
    if errors:
        return APIResponse.error('Validation failed', 400, errors)
    
    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name'].strip()
    if 'phone' in data:
        user.phone = data['phone']
    if 'wing' in data:
        user.wing = data['wing'].strip() if data['wing'] else None
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': user.to_dict(include_private=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Profile update error: {str(e)}')
        return APIResponse.error('Failed to update profile', 500)


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required_custom
@validate_json('current_password', 'new_password')
def change_password():
    """Change user's password."""
    user = get_current_user()
    data = request.get_json()
    
    # Verify current password
    if not check_password_hash(user.password, data['current_password']):
        return APIResponse.error('Current password is incorrect', 400)
    
    # Validate new password
    new_password = data['new_password']
    if len(new_password) < 8:
        return APIResponse.error('New password must be at least 8 characters', 400)
    
    try:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return APIResponse.error('Failed to change password', 500)


@auth_bp.route('/me', methods=['GET'])
@jwt_required_custom
def me():
    """Alias for get_profile - returns current user info."""
    return get_profile()
