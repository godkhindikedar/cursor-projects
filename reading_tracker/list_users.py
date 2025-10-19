#!/usr/bin/env python3
"""
Quick script to list all users in the database
"""

import os
import sqlite3
from dotenv import load_dotenv

# Load environment
load_dotenv('local_config.env')
db_url = os.environ.get('DATABASE_URL', 'sqlite:///reading_tracker_fresh.db')
db_path = db_url.replace('sqlite:///', '')

print(f"🔍 Checking users in database: {db_path}")

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
        print("\n💡 This means you haven't tried to log in with Google OAuth yet.")
        print("🔧 Next steps:")
        print("   1. Start the Flask app: python run_local.py")
        print("   2. Visit http://localhost:5000")
        print("   3. Click 'Sign in with Google'")
        print("   4. Use kedargit@gmail.com")
        print("   5. Come back here to approve the user")
    else:
        print("\n👥 Current Users:")
        print("-" * 80)
        for user in users:
            user_id, name, email, google_id, is_approved, is_admin, created_at = user
            status = "✅ Approved" if is_approved else "⏳ Pending Approval"
            admin = "👑 Admin" if is_admin else "👤 Regular User"
            print(f"ID: {user_id}")
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Status: {status}")
            print(f"Role: {admin}")
            print(f"Created: {created_at}")
            print("-" * 80)
        
        # Show pending users that need approval
        pending_users = [u for u in users if not u[4]]  # is_approved is at index 4
        if pending_users:
            print(f"\n⚠️  {len(pending_users)} user(s) need approval!")
            for user in pending_users:
                print(f"   - {user[2]} (ID: {user[0]}) - Use: python -c \"import sqlite3; conn=sqlite3.connect('{db_path}'); conn.execute('UPDATE user SET is_approved=1, is_admin=1 WHERE id={user[0]}'); conn.commit(); print('✅ Approved {user[2]}')\"")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

