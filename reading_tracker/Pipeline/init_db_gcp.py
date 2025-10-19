#!/usr/bin/env python3

"""
Database initialization script for GCP deployment
Creates the database schema and optionally seeds initial data
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db, User
from Pipeline.config.gcp_config import get_config
import logging

def init_database():
    """Initialize the database with proper schema"""
    print("🗄️ Initializing database schema...")
    
    # Configure the app with GCP settings
    app = create_app()
    app.config.from_object(get_config())
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database schema created successfully!")
            
            # Create admin user if admin emails are configured
            admin_emails = app.config.get('ADMIN_EMAILS', [])
            if admin_emails:
                print(f"👤 Admin emails configured: {', '.join(admin_emails)}")
                print("ℹ️ Admin users will be auto-approved on first login")
            else:
                print("⚠️ No admin emails configured. All users will need manual approval.")
            
            # Check database connection
            result = db.session.execute('SELECT 1').scalar()
            if result == 1:
                print("✅ Database connection test passed!")
            
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            logging.error(f"Database init error: {e}")
            return False

def seed_demo_data():
    """Add demo data for testing (optional)"""
    print("🌱 Adding demo data...")
    
    try:
        # Only add demo data if no users exist
        if User.query.count() == 0:
            print("ℹ️ No demo data added - users will be created via Google OAuth")
        else:
            print(f"ℹ️ Database already has {User.query.count()} users")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo data seeding failed: {e}")
        logging.error(f"Demo data error: {e}")
        return False

if __name__ == '__main__':
    print("🚀 GCP Database Initialization")
    print("=" * 40)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    success = init_database()
    
    if success:
        print("\n🎉 Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Deploy your application to Cloud Run")
        print("2. Users can sign in with Google OAuth")
        print("3. Admin users (if configured) will be auto-approved")
        print("4. Other users will need admin approval")
    else:
        print("\n💥 Database initialization failed!")
        sys.exit(1)
