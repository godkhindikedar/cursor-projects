#!/usr/bin/env python
"""
Update the database schema to add user approval fields
"""
import os
from datetime import datetime, timezone

# Import everything we need
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from config import DevelopmentConfig

# Create Flask app
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define updated models (copy from app.py)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    approval_requested_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    books = db.relationship('Book', backref='user', lazy=True)
    study_sessions = db.relationship('StudySession', backref='user', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    summary = db.Column(db.Text)
    date_read = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)
    
    book = db.relationship('Book', backref='study_sessions', lazy=True)

# Initialize database update
with app.app_context():
    print("Updating database schema for user approval system...")
    
    # Check if the database file exists
    import sqlite3
    db_path = 'reading_tracker.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the main app first to create the database.")
        exit(1)
    
    # Connect directly to SQLite to add columns
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = []
        if 'is_approved' not in columns:
            new_columns.append('is_approved')
        if 'is_admin' not in columns:
            new_columns.append('is_admin')
        if 'approval_requested_at' not in columns:
            new_columns.append('approval_requested_at')
            
        if new_columns:
            print(f"Adding columns: {', '.join(new_columns)}")
            
            # Add new columns
            if 'is_approved' not in columns:
                cursor.execute("ALTER TABLE user ADD COLUMN is_approved BOOLEAN DEFAULT 0 NOT NULL")
                print("✅ Added is_approved column")
                
            if 'is_admin' not in columns:
                cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
                print("✅ Added is_admin column")
                
            if 'approval_requested_at' not in columns:
                cursor.execute("ALTER TABLE user ADD COLUMN approval_requested_at DATETIME")
                # Set approval_requested_at to created_at for existing users
                cursor.execute("UPDATE user SET approval_requested_at = created_at WHERE approval_requested_at IS NULL")
                print("✅ Added approval_requested_at column")
            
            # Approve all existing users by default (so they don't get locked out)
            cursor.execute("UPDATE user SET is_approved = 1 WHERE is_approved = 0")
            existing_count = cursor.rowcount
            print(f"✅ Approved {existing_count} existing users")
            
            # Make the first user an admin (usually the creator)
            cursor.execute("UPDATE user SET is_admin = 1 WHERE id = 1")
            if cursor.rowcount > 0:
                print("✅ Made first user (ID=1) an admin")
                
            conn.commit()
            print("🎉 Database schema updated successfully!")
            
        else:
            print("✅ Database schema is already up to date!")
            
        # Show current users
        cursor.execute("SELECT id, name, email, is_approved, is_admin FROM user")
        users = cursor.fetchall()
        
        if users:
            print("\n📋 Current Users:")
            print("ID | Name | Email | Approved | Admin")
            print("-" * 50)
            for user in users:
                print(f"{user[0]:2} | {user[1][:15]:15} | {user[2][:20]:20} | {'Yes' if user[3] else 'No':8} | {'Yes' if user[4] else 'No'}")
        else:
            print("\n📋 No users found in database")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

print("\n🚀 Ready to use the approval system!")
print("   - New users will need approval before accessing the app")
print("   - Existing users have been automatically approved") 
print("   - The first user has been made an admin")
print("   - Admins can manage approvals at /admin")
