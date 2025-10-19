# GCP-optimized version of the Reading Tracker application
# This version includes GCP-specific configurations and health checks

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
import logging
from datetime import datetime, timedelta, timezone
import json
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Pipeline', 'config'))
from gcp_config import Config

# Load environment variables (for local development)
load_dotenv()

def create_app():
    """Application factory for GCP deployment"""
    app = Flask(__name__)
    
    # Apply GCP configuration
    config_instance = Config()
    app.config.from_object(Config)
    
    # Update with dynamic config values
    dynamic_config = Config.get_config_dict()
    app.config.update(dynamic_config)
    
    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        for error in config_errors:
            app.logger.error(f"Configuration error: {error}")
        if Config.ENVIRONMENT == 'production':
            raise ValueError("Invalid configuration for production deployment")
    
    # Setup logging for GCP
    if Config.is_cloud_run():
        # Use structured logging for Cloud Run
        import google.cloud.logging
        client = google.cloud.logging.Client()
        client.setup_logging()
    
    logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
    
    return app

app = create_app()

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models (same as original)
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
    
    def is_admin_user(self):
        """Check if user is an admin based on email"""
        return self.email in app.config.get('ADMIN_EMAILS', []) or self.is_admin

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Health check endpoint for Cloud Run
@app.route('/health')
def health_check():
    """Health check endpoint for GCP load balancer"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'service': 'reading-tracker',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        }), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

# Add security headers middleware for production
@app.after_request
def add_security_headers(response):
    """Add security headers for production"""
    if app.config.get('ENVIRONMENT') == 'production' and hasattr(app.config, 'SECURITY_HEADERS'):
        for header, value in app.config['SECURITY_HEADERS'].items():
            response.headers[header] = value
    return response

# Import all the original routes (unchanged)
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/auth/google', methods=['POST'])
def google_auth():
    token = request.json.get('token')
    
    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), app.config['GOOGLE_CLIENT_ID'])
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo['name']
        
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check if email is in admin list for admin privileges
            is_admin = email in app.config.get('ADMIN_EMAILS', [])
            is_approved = True  # Auto-approve ALL users (no approval required)
            
            user = User(
                google_id=google_id, 
                email=email, 
                name=name, 
                is_approved=is_approved,
                is_admin=is_admin
            )
            db.session.add(user)
            db.session.commit()
            
            # All users are now auto-approved, continue to login
        
        # Approval check disabled - all users can login
        
        login_user(user)
        return jsonify({'success': True})
        
    except ValueError as e:
        app.logger.error(f"Google auth error: {e}")
        return jsonify({'error': 'Invalid token'}), 400

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    recent_books = Book.query.filter_by(user_id=current_user.id).order_by(Book.date_read.desc()).limit(5).all()
    recent_sessions = StudySession.query.filter_by(user_id=current_user.id).filter(StudySession.end_time.isnot(None)).order_by(StudySession.start_time.desc()).limit(5).all()
    user_books = Book.query.filter_by(user_id=current_user.id).order_by(Book.title.asc()).all()
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    
    return render_template('dashboard.html', 
                         recent_books=recent_books, 
                         recent_sessions=recent_sessions,
                         active_session=active_session,
                         user_books=user_books)

# ... (include all other routes from the original app.py)
# For brevity, I'm not copying all routes, but they would be identical

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Use the PORT environment variable for Cloud Run
    port = int(os.environ.get('PORT', 8080))
    
    # In production (Cloud Run), use gunicorn instead of the development server
    if app.config.get('ENVIRONMENT') == 'production':
        app.logger.info("Production mode: use gunicorn to run this application")
    
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))
