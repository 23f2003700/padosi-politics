"""
Padosi Politics - Society Complaint Management System
Enterprise-level Flask Application Factory
Author: Aaryan (23F2003700)
Institution: IIT Madras BS in Data Science and Applications
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate

from app.extensions import db, security, jwt, mail, limiter, cache
from app.models.user import User, Role
from app.models import user_datastore
from config import config

migrate = Migrate()


def create_app(config_name=None):
    """Application factory pattern for Flask app creation."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup logging
    setup_logging(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        create_default_roles()
    
    return app


def initialize_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Setup Flask-Security
    security.init_app(app, user_datastore)
    
    # Setup JWT
    jwt.init_app(app)
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:5173', 'http://localhost:8080']),
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True
        }
    })
    
    # Setup rate limiter
    limiter.init_app(app)
    
    # Setup cache
    cache.init_app(app)
    
    # Setup mail (optional)
    if app.config.get('MAIL_SERVER'):
        mail.init_app(app)


def register_blueprints(app):
    """Register all blueprints."""
    from app.api.auth import auth_bp
    from app.api.societies import societies_bp
    from app.api.complaints import complaints_bp
    from app.api.evidence import evidence_bp
    from app.api.votes import votes_bp
    from app.api.comments import comments_bp
    from app.api.escalations import escalations_bp
    from app.api.karma import karma_bp
    from app.api.notifications import notifications_bp
    from app.api.dashboard import dashboard_bp
    from app.api.health import health_bp
    from app.api.tasks import tasks_bp
    
    # Register with /api prefix
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(societies_bp, url_prefix='/api/societies')
    app.register_blueprint(complaints_bp, url_prefix='/api/complaints')
    app.register_blueprint(evidence_bp, url_prefix='/api/evidence')
    app.register_blueprint(votes_bp, url_prefix='/api')
    app.register_blueprint(comments_bp, url_prefix='/api')
    app.register_blueprint(escalations_bp, url_prefix='/api/escalations')
    app.register_blueprint(karma_bp, url_prefix='/api')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    
    # Route to serve uploaded files
    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        """Serve uploaded files from the uploads directory."""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'success': False,
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal Server Error: {error}')
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500


def setup_logging(app):
    """Setup logging configuration."""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/padosi_politics.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Padosi Politics startup')


def create_default_roles():
    """Create default roles if they don't exist."""
    from app.models import user_datastore
    
    roles = [
        {'name': 'admin', 'description': 'Administrator with full access'},
        {'name': 'secretary', 'description': 'Society Secretary'},
        {'name': 'committee_member', 'description': 'Society Committee Member'},
        {'name': 'resident', 'description': 'Regular Resident'}
    ]
    
    for role_data in roles:
        if not Role.query.filter_by(name=role_data['name']).first():
            user_datastore.create_role(**role_data)
    
    db.session.commit()
