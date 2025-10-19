#!/usr/bin/env python3
"""
Local development runner for Reading Tracker
Loads environment variables and starts the Flask development server
"""

import os
import sys
from dotenv import load_dotenv

# Load local environment variables
print("🔧 Loading local environment configuration...")
load_dotenv('local_config.env')

# Verify required environment variables
required_vars = ['SECRET_KEY', 'GOOGLE_CLIENT_ID', 'ADMIN_EMAILS']
missing_vars = []

for var in required_vars:
    if not os.environ.get(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

print("✅ Environment variables loaded successfully!")
print(f"📊 Database: {os.environ.get('DATABASE_URL', 'Not set')}")
print(f"🔑 Google Client ID: {os.environ.get('GOOGLE_CLIENT_ID')[:20]}...")
print(f"👥 Admin Emails: {os.environ.get('ADMIN_EMAILS')}")

# Set environment variables for the app before importing
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///reading_tracker_fresh.db')
os.environ['FLASK_ENV'] = 'development'
os.environ['DEBUG'] = 'True'

# Initialize database
print("\n🗄️ Initializing local database...")
try:
    from app import app, db
    
    print(f"📊 App using database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    with app.app_context():
        db.create_all()
    print("✅ Database initialized successfully!")
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    sys.exit(1)

# Start the Flask development server
print("\n🚀 Starting Flask development server...")
print("📱 The application will be available at:")
print("   http://localhost:5000")
print("   http://127.0.0.1:5000")
print("\n💡 Press Ctrl+C to stop the server")
print("="*50)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )
