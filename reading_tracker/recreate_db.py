#!/usr/bin/env python3
"""
Database recreation script for Reading Tracker
Safely recreates the database with fresh schema
"""

import os
import sys
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

def recreate_database():
    """Recreate the database with fresh schema"""
    
    print("🗄️ Reading Tracker Database Recreation")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv('local_config.env')
    
    # Database configuration
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///reading_tracker_local.db')
    
    # Extract database path from URL
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
    else:
        db_path = 'reading_tracker_local.db'
    
    print(f"📍 Database path: {db_path}")
    
    # Create a completely new database file
    fresh_db_path = 'reading_tracker_fresh.db'
    
    try:
        # Remove fresh db if it exists
        if os.path.exists(fresh_db_path):
            os.remove(fresh_db_path)
            print(f"🧹 Removed existing fresh database: {fresh_db_path}")
        
        # Create new database connection
        print(f"✨ Creating fresh database: {fresh_db_path}")
        conn = sqlite3.connect(fresh_db_path)
        cursor = conn.cursor()
        
        # Create tables with the schema from your app
        print("🏗️ Creating database schema...")
        
        # Users table
        cursor.execute('''
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                google_id VARCHAR(100) UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_approved BOOLEAN DEFAULT 0 NOT NULL,
                is_admin BOOLEAN DEFAULT 0 NOT NULL,
                approval_requested_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Books table
        cursor.execute('''
            CREATE TABLE book (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                author VARCHAR(100),
                summary TEXT,
                date_read DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        
        # Study sessions table
        cursor.execute('''
            CREATE TABLE study_session (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject VARCHAR(50) NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                duration_minutes INTEGER,
                notes TEXT,
                user_id INTEGER NOT NULL,
                book_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (book_id) REFERENCES book (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX idx_user_email ON user(email)')
        cursor.execute('CREATE INDEX idx_user_google_id ON user(google_id)')
        cursor.execute('CREATE INDEX idx_book_user_id ON book(user_id)')
        cursor.execute('CREATE INDEX idx_book_date_read ON book(date_read)')
        cursor.execute('CREATE INDEX idx_session_user_id ON study_session(user_id)')
        cursor.execute('CREATE INDEX idx_session_start_time ON study_session(start_time)')
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print("✅ Fresh database created successfully!")
        print(f"📊 Database file: {fresh_db_path}")
        print(f"💾 Size: {os.path.getsize(fresh_db_path)} bytes")
        
        # Update the local config to use the fresh database
        print("🔧 Updating local configuration...")
        
        # Read current config
        with open('local_config.env', 'r') as f:
            config_content = f.read()
        
        # Update database URL
        updated_config = config_content.replace(
            f'DATABASE_URL={db_url}',
            f'DATABASE_URL=sqlite:///{fresh_db_path}'
        )
        
        # Write updated config
        with open('local_config.env', 'w') as f:
            f.write(updated_config)
        
        print("✅ Configuration updated!")
        print(f"🔄 New DATABASE_URL: sqlite:///{fresh_db_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def verify_database(db_path):
    """Verify the database was created correctly"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['user', 'book', 'study_session']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        print("✅ All required tables found:")
        for table in expected_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   📋 {table}: {count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

if __name__ == '__main__':
    success = recreate_database()
    
    if success:
        # Verify the database
        fresh_db_path = 'reading_tracker_fresh.db'
        if verify_database(fresh_db_path):
            print("\n🎉 Database recreation completed successfully!")
            print("\n📋 Next steps:")
            print("1. Run: python run_local.py")
            print("2. Visit: http://localhost:5000")
            print("3. Sign in with Google OAuth")
            print("4. Start tracking your reading!")
        else:
            print("\n💥 Database verification failed!")
            sys.exit(1)
    else:
        print("\n💥 Database recreation failed!")
        sys.exit(1)
