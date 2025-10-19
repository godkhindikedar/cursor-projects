#!/usr/bin/env python3
"""
Azure App Service startup script for Reading & Study Tracker
This script ensures proper initialization on Azure deployment
"""

import os
import sys
from app import app, db

def main():
    """Initialize the application for Azure deployment"""
    print("🚀 Initializing Reading & Study Tracker on Azure...")
    
    try:
        # Create database tables if they don't exist
        with app.app_context():
            db.create_all()
            print("✅ Database tables created/verified")
        
        print("✅ Application initialized successfully")
        return app
        
    except Exception as e:
        print(f"❌ Error initializing application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    app = main()
    # For Azure, the app will be served by gunicorn
    # This is just for initialization
