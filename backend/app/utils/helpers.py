"""
Utility Functions - Common helper functions for the application
"""

import os
import uuid
import re
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename
from flask import current_app, request


def generate_unique_filename(filename):
    """Generate a unique filename while preserving extension."""
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return secure_filename(unique_name)


def allowed_file(filename):
    """Check if file extension is allowed."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', set())


def get_file_type(filename):
    """Determine file type based on extension."""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    video_extensions = {'mp4', 'avi', 'mov', 'wmv', 'webm'}
    audio_extensions = {'mp3', 'wav', 'ogg', 'flac'}
    document_extensions = {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx'}
    
    if ext in image_extensions:
        return 'image'
    elif ext in video_extensions:
        return 'video'
    elif ext in audio_extensions:
        return 'audio'
    elif ext in document_extensions:
        return 'document'
    else:
        return 'other'


def save_uploaded_file(file, subfolder='uploads'):
    """Save uploaded file and return the file path."""
    if not file or not file.filename:
        return None, None
    
    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed: {file.filename}")
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename)
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    file.save(file_path)
    
    # Return relative URL path
    file_url = f"/uploads/{subfolder}/{filename}"
    file_type = get_file_type(file.filename)
    
    return file_url, file_type


def delete_uploaded_file(file_url):
    """Delete an uploaded file."""
    if not file_url:
        return False
    
    # Convert URL to file path
    file_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        file_url.replace('/uploads/', '')
    )
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_path}: {e}")
    
    return False


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate Indian phone number format."""
    if not phone:
        return True  # Phone is optional
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None


def validate_flat_number(flat_number):
    """Validate flat number format (e.g., A-101, B-402)."""
    pattern = r'^[A-Za-z]+-?\d+$'
    return re.match(pattern, flat_number) is not None


def sanitize_string(text, max_length=None):
    """Sanitize string input."""
    if not text:
        return text
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def paginate_query(query, page=1, per_page=10, max_per_page=100):
    """Paginate a SQLAlchemy query."""
    # Ensure valid page and per_page values
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    
    # Execute pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }


def get_pagination_params():
    """Get pagination parameters from request args."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return page, per_page


def format_datetime(dt, format_type='default'):
    """Format datetime for display."""
    if not dt:
        return None
    
    formats = {
        'default': '%Y-%m-%d %H:%M:%S',
        'date': '%Y-%m-%d',
        'time': '%H:%M:%S',
        'display': '%d %b %Y, %I:%M %p',
        'iso': '%Y-%m-%dT%H:%M:%S.%fZ'
    }
    
    return dt.strftime(formats.get(format_type, formats['default']))


def calculate_days_since(dt):
    """Calculate days since a given datetime."""
    if not dt:
        return None
    return (datetime.utcnow() - dt).days


def mask_email(email):
    """Mask email for privacy (e.g., j***@example.com)."""
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@')
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone):
    """Mask phone number for privacy (e.g., ******1234)."""
    if not phone or len(phone) < 4:
        return phone
    
    return '*' * (len(phone) - 4) + phone[-4:]


class APIResponse:
    """Standardized API response builder."""
    
    @staticmethod
    def success(data=None, message=None, status_code=200):
        """Return success response."""
        response = {'success': True}
        if data is not None:
            response['data'] = data
        if message:
            response['message'] = message
        return response, status_code
    
    @staticmethod
    def error(message, status_code=400, errors=None):
        """Return error response."""
        response = {
            'success': False,
            'error': message
        }
        if errors:
            response['errors'] = errors
        return response, status_code
    
    @staticmethod
    def paginated(items, pagination_info, item_transform=None):
        """Return paginated response."""
        if item_transform:
            items = [item_transform(item) for item in items]
        
        return {
            'success': True,
            'data': items,
            'pagination': {
                'total': pagination_info['total'],
                'pages': pagination_info['pages'],
                'page': pagination_info['page'],
                'per_page': pagination_info['per_page'],
                'has_next': pagination_info['has_next'],
                'has_prev': pagination_info['has_prev']
            }
        }, 200
