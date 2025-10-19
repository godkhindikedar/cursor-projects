#!/usr/bin/env python3
"""
Main entry point for Reading & Study Tracker
Handles both development and production environments
"""

import os
from app import app, db

def main():
    """Main entry point for the application"""
    # Initialize database tables
    with app.app_context():
        db.create_all()
    
    # Get port from environment (Azure sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )

if __name__ == '__main__':
    main()
