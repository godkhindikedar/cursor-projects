#!/usr/bin/env python3
"""
Manual user approval script for Reading Tracker
Use this to manually approve users or check user status
"""

import os
import sys
import sqlite3
from dotenv import load_dotenv
from datetime import datetime, timezone

def load_database():
    """Load database configuration"""
    load_dotenv('local_config.env')
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///reading_tracker_fresh.db')
    db_path = db_url.replace('sqlite:///', '')
    return db_path

def list_users():
    """List all users and their approval status"""
    db_path = load_database()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, google_id, is_approved, is_admin, created_at
            FROM user
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("📭 No users found in the database.")
            return []
        
        print("👥 Current Users:")
        print("-" * 80)
        for user in users:
            user_id, name, email, google_id, is_approved, is_admin, created_at = user
            status = "✅ Approved" if is_approved else "⏳ Pending"
            admin = "👑 Admin" if is_admin else "👤 User"
            print(f"ID: {user_id} | {name} ({email}) | {status} | {admin}")
            print(f"     Google ID: {google_id}")
            print(f"     Created: {created_at}")
            print("-" * 80)
        
        conn.close()
        return users
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return []

def approve_user(user_id):
    """Approve a specific user by ID"""
    db_path = load_database()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT name, email FROM user WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User with ID {user_id} not found.")
            return False
        
        name, email = user
        
        # Approve the user
        cursor.execute("""
            UPDATE user 
            SET is_approved = 1 
            WHERE id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ User approved: {name} ({email})")
        return True
        
    except Exception as e:
        print(f"❌ Error approving user: {e}")
        return False

def make_admin(user_id):
    """Make a user an admin"""
    db_path = load_database()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT name, email FROM user WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User with ID {user_id} not found.")
            return False
        
        name, email = user
        
        # Make admin and approve
        cursor.execute("""
            UPDATE user 
            SET is_admin = 1, is_approved = 1 
            WHERE id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        print(f"👑 User promoted to admin: {name} ({email})")
        return True
        
    except Exception as e:
        print(f"❌ Error making user admin: {e}")
        return False

def create_test_user():
    """Create a test user for kedargit@gmail.com if it doesn't exist"""
    db_path = load_database()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM user WHERE email = ?", ("kedargit@gmail.com",))
        existing = cursor.fetchone()
        
        if existing:
            print(f"✅ User kedargit@gmail.com already exists with ID {existing[0]}")
            return existing[0]
        
        # Create the user
        cursor.execute("""
            INSERT INTO user (email, name, google_id, is_approved, is_admin, created_at, approval_requested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "kedargit@gmail.com",
            "Kedar",
            "test_google_id_123",
            1,  # approved
            1,  # admin
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat()
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Created and approved admin user: kedargit@gmail.com (ID: {user_id})")
        return user_id
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None

def main():
    """Main function with interactive menu"""
    print("🔧 Reading Tracker - Manual User Management")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. List all users")
        print("2. Approve user by ID")
        print("3. Make user admin by ID")
        print("4. Create test user for kedargit@gmail.com")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            list_users()
        
        elif choice == "2":
            try:
                user_id = int(input("Enter user ID to approve: "))
                approve_user(user_id)
            except ValueError:
                print("❌ Please enter a valid number.")
        
        elif choice == "3":
            try:
                user_id = int(input("Enter user ID to make admin: "))
                make_admin(user_id)
            except ValueError:
                print("❌ Please enter a valid number.")
        
        elif choice == "4":
            create_test_user()
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == '__main__':
    main()

