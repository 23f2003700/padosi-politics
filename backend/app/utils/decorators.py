"""
Custom Decorators - Authentication, authorization, and validation decorators
"""

from functools import wraps
from flask import jsonify, request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User, Complaint


def jwt_required_custom(fn):
    """Custom JWT required decorator with user loading."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            # Convert to int if it's a string (JWT stores as string)
            if isinstance(user_id, str):
                user_id = int(user_id)
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 401
            
            if not user.active:
                return jsonify({
                    'success': False,
                    'error': 'Account is deactivated'
                }), 403
            
            # Store user in flask g object for easy access
            g.current_user = user
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
    
    return wrapper


def get_current_user():
    """Get the current logged in user from flask g object."""
    return getattr(g, 'current_user', None)


def admin_required(fn):
    """Decorator to require admin role."""
    @wraps(fn)
    @jwt_required_custom
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user.is_admin():
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        return fn(*args, **kwargs)
    return wrapper


def secretary_required(fn):
    """Decorator to require secretary or admin role."""
    @wraps(fn)
    @jwt_required_custom
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user.is_secretary():
            return jsonify({
                'success': False,
                'error': 'Secretary access required'
            }), 403
        return fn(*args, **kwargs)
    return wrapper


def committee_required(fn):
    """Decorator to require committee member, secretary, or admin role."""
    @wraps(fn)
    @jwt_required_custom
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user.is_committee_member():
            return jsonify({
                'success': False,
                'error': 'Committee member access required'
            }), 403
        return fn(*args, **kwargs)
    return wrapper


def same_society_required(fn):
    """Decorator to ensure user belongs to the same society as the resource."""
    @wraps(fn)
    @jwt_required_custom
    def wrapper(*args, **kwargs):
        user = get_current_user()
        
        # Check if complaint_id is in kwargs
        complaint_id = kwargs.get('complaint_id') or kwargs.get('id')
        if complaint_id:
            complaint = Complaint.query.get(complaint_id)
            if complaint and complaint.society_id != user.society_id:
                if not user.is_admin():  # Admins can access any society
                    return jsonify({
                        'success': False,
                        'error': 'Access denied: Different society'
                    }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def validate_json(*required_fields):
    """Decorator to validate required JSON fields in request."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type must be application/json'
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Request body is empty'
                }), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit_by_user(limit_string):
    """Custom rate limiter by user ID instead of IP."""
    from app.extensions import limiter
    
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Use user ID for rate limiting if authenticated
            user = get_current_user()
            if user:
                key = f"user_{user.id}"
            else:
                key = request.remote_addr
            
            # Apply rate limiting logic here
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def ownership_required(model_class, id_param='id'):
    """Decorator to ensure user owns the resource or is admin."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required_custom
        def wrapper(*args, **kwargs):
            user = get_current_user()
            resource_id = kwargs.get(id_param)
            
            if resource_id:
                resource = model_class.query.get(resource_id)
                if not resource:
                    return jsonify({
                        'success': False,
                        'error': f'{model_class.__name__} not found'
                    }), 404
                
                # Check ownership (assumes model has user_id or complainant_id)
                owner_id = getattr(resource, 'user_id', None) or getattr(resource, 'complainant_id', None)
                
                if owner_id != user.id and not user.is_secretary():
                    return jsonify({
                        'success': False,
                        'error': 'You do not have permission to access this resource'
                    }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def log_api_call(fn):
    """Decorator to log API calls for debugging."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from flask import current_app
        
        user = get_current_user()
        user_info = f"User: {user.email}" if user else "Anonymous"
        
        current_app.logger.info(
            f"API Call: {request.method} {request.path} | {user_info} | "
            f"IP: {request.remote_addr}"
        )
        
        return fn(*args, **kwargs)
    return wrapper
