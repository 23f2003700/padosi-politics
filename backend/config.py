"""
Configuration Settings for Padosi Politics Application
Supports multiple environments: development, testing, production
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'padosi-politics-super-secret-key-change-in-production'
    
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Flask-Security
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'padosi-politics-security-salt'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'
    SECURITY_TOKEN_MAX_AGE = 86400  # 24 hours
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'wav', 'pdf', 'doc', 'docx'}
    
    # CORS
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:8080', 'http://127.0.0.1:5173']
    
    # Mail Configuration (Optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@padosipolitics.com')
    
    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Celery Configuration (Optional - for local dev with Redis)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_ENABLED = os.environ.get('CELERY_ENABLED', 'false').lower() == 'true'
    
    # Serverless/Cloudflare Configuration
    SERVERLESS = os.environ.get('SERVERLESS', 'false').lower() == 'true'
    CRON_SECRET = os.environ.get('CRON_SECRET', 'default-cron-secret-change-in-production')
    
    # Pagination
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # Karma Settings
    KARMA_COMPLAINT_RESOLVED = 10
    KARMA_REPEAT_OFFENDER_PENALTY = -50
    KARMA_HELPFUL_VOTE = 2
    KARMA_FALSE_COMPLAINT = -20
    
    # Escalation Settings
    AUTO_ESCALATE_DAYS = 7
    REMINDER_DAYS = 3
    
    @staticmethod
    def init_app(app):
        """Initialize application-specific configurations."""
        pass


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'padosi_dev.db')
    
    # More verbose logging in development
    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # Support both PostgreSQL (Render) and SQLite
    # Get database URL from environment or use SQLite
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url:
        # Render uses postgres:// but SQLAlchemy needs postgresql://
        if _db_url.startswith('postgres://'):
            _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'padosi_prod.db')
    
    # CORS - Allow Cloudflare Pages domain, PythonAnywhere, and Mobile Apps
    CORS_ORIGINS = [
        'https://padosi-politics.pages.dev',
        'https://*.padosi-politics.pages.dev',  # Preview deployments
        'https://padosipolitics.com',
        'https://www.padosipolitics.com',
        # Mobile App (Capacitor) origins
        'capacitor://localhost',
        'http://localhost',
        'https://localhost',
        'ionic://localhost',
        '*',  # Allow all origins for mobile apps (API is protected by JWT)
        os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    ]
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Cache - use simple cache if Redis not available
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
