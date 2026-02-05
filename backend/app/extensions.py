"""
Flask Extensions - Centralized extension initialization
Prevents circular imports by initializing extensions without app context
"""

from flask_sqlalchemy import SQLAlchemy
from flask_security import Security
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# SQLAlchemy for database ORM
db = SQLAlchemy()

# Flask-Security for user management
security = Security()

# JWT for token-based authentication
jwt = JWTManager()

# Flask-Mail for email notifications
mail = Mail()

# Rate limiter to prevent abuse
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)

# Cache for performance optimization
cache = Cache()
