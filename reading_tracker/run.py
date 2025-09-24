#!/usr/bin/env python3
"""
Simple run script for the Reading & Study Tracker application
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all required environment variables are set"""
    required_vars = ['SECRET_KEY', 'DATABASE_URL', 'GOOGLE_CLIENT_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please create a .env file with these variables.")
        print("   See README.md for setup instructions.")
        return False
    
    return True

def check_database():
    """Check if database connection is working"""
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Please check your DATABASE_URL and ensure MySQL is running.")
        return False

def main():
    """Main function to start the application"""
    print("🚀 Starting Reading & Study Tracker...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check database
    if not check_database():
        sys.exit(1)
    
    # Import and run the app
    try:
        from app import app
        print("✅ All checks passed!")
        print("🌟 Starting the application...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
