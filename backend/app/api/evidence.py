"""
Evidence API - File upload and management for complaints
"""

import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Complaint, ComplaintEvidence
from app.utils import (
    jwt_required_custom, get_current_user, same_society_required,
    APIResponse, save_uploaded_file, delete_uploaded_file, allowed_file
)

evidence_bp = Blueprint('evidence', __name__)


@evidence_bp.route('', methods=['POST'])
@jwt_required_custom
def upload_evidence():
    """Upload evidence for a complaint."""
    user = get_current_user()
    
    complaint_id = request.form.get('complaint_id')
    if not complaint_id:
        return APIResponse.error('Complaint ID is required', 400)
    
    complaint = Complaint.query.get_or_404(int(complaint_id))
    
    # Verify user can add evidence (complainant or committee)
    if complaint.complainant_id != user.id and not user.is_committee_member():
        return APIResponse.error('You cannot add evidence to this complaint', 403)
    
    if 'file' not in request.files:
        return APIResponse.error('No file provided', 400)
    
    file = request.files['file']
    if file.filename == '':
        return APIResponse.error('No file selected', 400)
    
    if not allowed_file(file.filename):
        return APIResponse.error('File type not allowed', 400)
    
    description = request.form.get('description', '')
    
    try:
        # Save file
        file_url, file_type = save_uploaded_file(file, f'evidence/{complaint_id}')
        
        if not file_url:
            return APIResponse.error('Failed to save file', 500)
        
        # Create evidence record
        evidence = ComplaintEvidence(
            complaint_id=complaint.id,
            uploaded_by_id=user.id,
            file_url=file_url,
            file_type=file_type,
            file_name=secure_filename(file.filename),
            file_size=file.content_length or 0,
            description=description.strip() if description else None
        )
        
        db.session.add(evidence)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evidence uploaded successfully',
            'data': evidence.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Evidence upload error: {str(e)}')
        return APIResponse.error('Failed to upload evidence', 500)


@evidence_bp.route('/<int:id>', methods=['GET'])
@jwt_required_custom
def get_evidence(id):
    """Get evidence details."""
    evidence = ComplaintEvidence.query.get_or_404(id)
    
    return jsonify({
        'success': True,
        'data': evidence.to_dict()
    }), 200


@evidence_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_custom
def delete_evidence(id):
    """Delete evidence."""
    user = get_current_user()
    evidence = ComplaintEvidence.query.get_or_404(id)
    
    # Check permissions
    if evidence.uploaded_by_id != user.id and not user.is_secretary():
        return APIResponse.error('You cannot delete this evidence', 403)
    
    try:
        # Delete file from filesystem
        delete_uploaded_file(evidence.file_url)
        
        # Delete record
        db.session.delete(evidence)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evidence deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Evidence delete error: {str(e)}')
        return APIResponse.error('Failed to delete evidence', 500)


# Complaint-specific evidence endpoints (prefixed routes)
@evidence_bp.route('/complaints/<int:complaint_id>/evidence', methods=['GET'])
@jwt_required_custom
def get_complaint_evidence(complaint_id):
    """Get all evidence for a complaint."""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    evidence_list = ComplaintEvidence.query.filter_by(complaint_id=complaint_id)\
        .order_by(ComplaintEvidence.uploaded_at.desc()).all()
    
    return jsonify({
        'success': True,
        'data': [e.to_dict() for e in evidence_list]
    }), 200


@evidence_bp.route('/complaints/<int:complaint_id>/evidence', methods=['POST'])
@jwt_required_custom
def upload_complaint_evidence(complaint_id):
    """Upload evidence for a specific complaint."""
    # Redirect to main upload with complaint_id set
    from flask import make_response
    request.form = dict(request.form)
    request.form['complaint_id'] = str(complaint_id)
    return upload_evidence()
