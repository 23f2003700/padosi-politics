"""
Health Check API - System status endpoints
"""

from flask import Blueprint, jsonify
from datetime import datetime

from app.extensions import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Padosi Politics API'
    }), 200


@health_bp.route('/health/db', methods=['GET'])
def database_health():
    """Check database connectivity."""
    try:
        # Execute a simple query to check database
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy' if db_status == 'connected' else 'unhealthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200 if db_status == 'connected' else 503
