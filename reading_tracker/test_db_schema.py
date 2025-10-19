#!/usr/bin/env python3
"""
Test database schema to verify all columns exist
"""

import sqlite3
import os
from dotenv import load_dotenv

def test_database_schema():
    print("🔍 Testing Database Schema")
    print("=" * 30)
    
    # Load environment
    load_dotenv('local_config.env')
    
    # Get database path
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///reading_tracker_fresh.db')
    db_path = db_url.replace('sqlite:///', '')
    
    print(f"📍 Testing database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file does not exist: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check user table schema
        print("\n👤 User table schema:")
        cursor.execute("PRAGMA table_info(user)")
        user_columns = cursor.fetchall()
        
        for col in user_columns:
            print(f"   📋 {col[1]} ({col[2]}) - {col[5] if col[5] else 'nullable'}")
        
        # Check for required columns
        required_user_columns = ['id', 'email', 'name', 'google_id', 'created_at', 'is_approved', 'is_admin', 'approval_requested_at']
        existing_columns = [col[1] for col in user_columns]
        
        missing_columns = []
        for req_col in required_user_columns:
            if req_col not in existing_columns:
                missing_columns.append(req_col)
        
        if missing_columns:
            print(f"❌ Missing columns in user table: {missing_columns}")
            return False
        else:
            print("✅ All required user columns present!")
        
        # Check book table
        print("\n📚 Book table schema:")
        cursor.execute("PRAGMA table_info(book)")
        book_columns = cursor.fetchall()
        
        for col in book_columns:
            print(f"   📋 {col[1]} ({col[2]})")
        
        # Check study_session table
        print("\n⏰ Study_session table schema:")
        cursor.execute("PRAGMA table_info(study_session)")
        session_columns = cursor.fetchall()
        
        for col in session_columns:
            print(f"   📋 {col[1]} ({col[2]})")
        
        # Test a simple query
        print("\n🧪 Testing user table query...")
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"✅ User table accessible, {user_count} records")
        
        # Test the specific query that was failing
        print("\n🎯 Testing the problematic query...")
        try:
            cursor.execute("""
                SELECT user.id AS user_id, user.email AS user_email, user.name AS user_name, 
                       user.google_id AS user_google_id, user.created_at AS user_created_at, 
                       user.is_approved AS user_is_approved, user.is_admin AS user_is_admin, 
                       user.approval_requested_at AS user_approval_requested_at 
                FROM user LIMIT 1
            """)
            print("✅ Problematic query works fine!")
        except Exception as e:
            print(f"❌ Query still fails: {e}")
            return False
        
        conn.close()
        print("\n🎉 Database schema test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == '__main__':
    test_database_schema()


