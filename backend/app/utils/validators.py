"""
Validators - Input validation utilities
"""

import re
from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from app.models import ComplaintCategory, ComplaintStatus, ComplaintPriority


class UserRegistrationSchema(Schema):
    """Validation schema for user registration."""
    email = fields.Email(required=True, error_messages={'required': 'Email is required'})
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=128),
        error_messages={'required': 'Password is required'}
    )
    full_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=150),
        error_messages={'required': 'Full name is required'}
    )
    flat_number = fields.String(
        required=True,
        validate=validate.Length(min=1, max=20),
        error_messages={'required': 'Flat number is required'}
    )
    wing = fields.String(validate=validate.Length(max=50), load_default=None)
    society_id = fields.Integer(required=True, error_messages={'required': 'Society ID is required'})
    phone = fields.String(validate=validate.Length(max=20), load_default=None)
    
    @validates('password')
    def validate_password(self, value):
        """Validate password strength."""
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one digit')
    
    @validates('phone')
    def validate_phone(self, value):
        """Validate Indian phone number."""
        if value:
            clean_phone = value.replace(' ', '').replace('-', '').replace('+91', '')
            if not re.match(r'^[6-9]\d{9}$', clean_phone):
                raise ValidationError('Invalid phone number format')
    
    @validates('flat_number')
    def validate_flat_number(self, value):
        """Validate flat number format."""
        if not re.match(r'^[A-Za-z0-9]+-?[A-Za-z0-9]+$', value):
            raise ValidationError('Invalid flat number format (e.g., A-101, B-402)')


class UserLoginSchema(Schema):
    """Validation schema for user login."""
    email = fields.Email(required=True)
    password = fields.String(required=True)


class UserUpdateSchema(Schema):
    """Validation schema for user profile update."""
    full_name = fields.String(validate=validate.Length(min=2, max=150))
    phone = fields.String(validate=validate.Length(max=20))
    wing = fields.String(validate=validate.Length(max=50))


class ComplaintCreateSchema(Schema):
    """Validation schema for creating a complaint."""
    title = fields.String(
        required=True,
        validate=validate.Length(min=5, max=200),
        error_messages={'required': 'Title is required'}
    )
    description = fields.String(
        required=True,
        validate=validate.Length(min=20, max=5000),
        error_messages={'required': 'Description is required'}
    )
    category = fields.String(
        required=True,
        validate=validate.OneOf([c.value for c in ComplaintCategory]),
        error_messages={'required': 'Category is required'}
    )
    accused_flat = fields.String(validate=validate.Length(max=20), load_default=None)
    is_anonymous = fields.Boolean(load_default=False)
    priority = fields.String(
        validate=validate.OneOf([p.value for p in ComplaintPriority]),
        load_default=ComplaintPriority.MEDIUM.value
    )


class ComplaintUpdateSchema(Schema):
    """Validation schema for updating a complaint."""
    title = fields.String(validate=validate.Length(min=5, max=200))
    description = fields.String(validate=validate.Length(min=20, max=5000))
    category = fields.String(validate=validate.OneOf([c.value for c in ComplaintCategory]))
    priority = fields.String(validate=validate.OneOf([p.value for p in ComplaintPriority]))


class ComplaintStatusUpdateSchema(Schema):
    """Validation schema for updating complaint status."""
    status = fields.String(
        required=True,
        validate=validate.OneOf([s.value for s in ComplaintStatus]),
        error_messages={'required': 'Status is required'}
    )
    resolution_note = fields.String(validate=validate.Length(max=2000))


class VoteSchema(Schema):
    """Validation schema for voting on a complaint."""
    vote_type = fields.String(
        required=True,
        validate=validate.OneOf(['support', 'oppose']),
        error_messages={'required': 'Vote type is required'}
    )
    is_anonymous = fields.Boolean(load_default=True)


class CommentSchema(Schema):
    """Validation schema for adding a comment."""
    comment_text = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={'required': 'Comment text is required'}
    )
    is_anonymous = fields.Boolean(load_default=False)


class EscalationSchema(Schema):
    """Validation schema for escalating a complaint."""
    escalate_to = fields.String(
        required=True,
        validate=validate.OneOf(['secretary', 'committee', 'legal']),
        error_messages={'required': 'Escalation target is required'}
    )
    reason = fields.String(
        required=True,
        validate=validate.Length(min=10, max=1000),
        error_messages={'required': 'Escalation reason is required'}
    )


class SocietyCreateSchema(Schema):
    """Validation schema for creating a society."""
    name = fields.String(
        required=True,
        validate=validate.Length(min=3, max=200),
        error_messages={'required': 'Society name is required'}
    )
    address = fields.String(validate=validate.Length(max=500))
    city = fields.String(required=True, validate=validate.Length(max=100))
    state = fields.String(validate=validate.Length(max=100))
    pincode = fields.String(validate=validate.Length(max=10))
    total_flats = fields.Integer(validate=validate.Range(min=1))


class PaginationSchema(Schema):
    """Validation schema for pagination parameters."""
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=10, validate=validate.Range(min=1, max=100))


def validate_request(schema_class, data=None, partial=False):
    """Validate request data against a schema."""
    from flask import request
    
    if data is None:
        # Support both JSON and form data
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form.to_dict()
            # Convert string boolean values
            for key in data:
                if data[key] == 'true':
                    data[key] = True
                elif data[key] == 'false':
                    data[key] = False
    
    schema = schema_class()
    try:
        validated_data = schema.load(data, partial=partial)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages
