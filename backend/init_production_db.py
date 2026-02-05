"""
Production Database Initialization Script
Run this after first deployment to set up the database schema and seed data.

Usage:
  python init_production_db.py
"""

import os
import sys

# Ensure we're using production config
os.environ['FLASK_ENV'] = 'production'

from app import create_app
from app.extensions import db
from app.models import User, Society, Complaint, Role
from datetime import datetime
from werkzeug.security import generate_password_hash


def init_database():
    """Initialize the production database with schema and admin user."""
    app = create_app('production')
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@padosipolitics.com').first()
        if admin:
            print("Admin user already exists. Skipping seeding.")
            return
        
        print("Creating admin user...")
        
        # Create admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='System Administrator')
            db.session.add(admin_role)
        
        secretary_role = Role.query.filter_by(name='secretary').first()
        if not secretary_role:
            secretary_role = Role(name='secretary', description='Society Secretary')
            db.session.add(secretary_role)
        
        resident_role = Role.query.filter_by(name='resident').first()
        if not resident_role:
            resident_role = Role(name='resident', description='Resident')
            db.session.add(resident_role)
        
        db.session.commit()
        
        # Create system admin
        admin_user = User(
            email='admin@padosipolitics.com',
            password=generate_password_hash('AdminPassword123!'),
            full_name='System Administrator',
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        
        db.session.commit()
        print("Database initialized successfully!")
        print("\nAdmin Login:")
        print("  Email: admin@padosipolitics.com")
        print("  Password: AdminPassword123!")
        print("\n⚠️  IMPORTANT: Change the admin password immediately after first login!")


if __name__ == '__main__':
    init_database()
