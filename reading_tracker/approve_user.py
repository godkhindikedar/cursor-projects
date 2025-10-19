#!/usr/bin/env python3
"""
Quick script to approve kedargit@gmail.com or create the user as admin
"""

import os
import sqlite3
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment
load_dotenv('local_config.env')
db_url = os.environ.get('DATABASE_URL', 'sqlite:///reading_tracker_fresh.db')
db_path = db_url.replace('sqlite:///', '')

print(f"🔧 Working with database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # First, let's see if the user exists
    cursor.execute("SELECT * FROM user WHERE email = ?", ("kedargit@gmail.com",))
    user = cursor.fetchone()
    
    if user:
        print(f"👤 Found existing user: {user}")
        print("🔧 Updating user to be approved admin...")
        
        cursor.execute("""
            UPDATE user 
            SET is_approved = 1, is_admin = 1 
            WHERE email = ?
        """, ("kedargit@gmail.com",))
        
        conn.commit()
        print("✅ Updated kedargit@gmail.com to approved admin!")
    
    else:
        print("👤 User doesn't exist, creating as approved admin...")
        
        cursor.execute("""
            INSERT INTO user (email, name, google_id, is_approved, is_admin, created_at, approval_requested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "kedargit@gmail.com",
            "Kedar",
            "temp_google_id_" + str(int(datetime.now().timestamp())),
            1,  # approved
            1,  # admin
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        print("✅ Created kedargit@gmail.com as approved admin!")
    
    # Verify the change
    cursor.execute("SELECT id, name, email, is_approved, is_admin FROM user WHERE email = ?", ("kedargit@gmail.com",))
    updated_user = cursor.fetchone()
    print(f"✅ Verification: {updated_user}")
    
    # List all users
    cursor.execute("SELECT id, name, email, is_approved, is_admin FROM user")
    all_users = cursor.fetchall()
    print(f"\n📋 All users in database:")
    for u in all_users:
        status = "✅ Approved" if u[3] else "⏳ Pending"
        role = "👑 Admin" if u[4] else "👤 User"
        print(f"   {u[0]}: {u[1]} ({u[2]}) - {status} {role}")
    
    conn.close()
    
    print("\n🎉 You should now be able to log in!")
    print("💡 Try refreshing your browser and logging in again.")
    
except Exception as e:
    print(f"❌ Error: {e}")
