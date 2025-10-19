from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
from datetime import datetime, timedelta, timezone
import json
import random
from dotenv import load_dotenv
from config import Config, DevelopmentConfig, ProductionConfig, AzureConfig

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Determine which config to use
    if os.environ.get('WEBSITE_SITE_NAME'):  # Azure App Service
        app.config.from_object(AzureConfig)
    elif os.environ.get('FLASK_ENV') == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    return app

app = create_app()

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
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
    subject = db.Column(db.String(50), nullable=False)  # maths, english, reading, science, writing, social_studies
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)  # calculated field
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)  # Optional book for reading sessions
    
    book = db.relationship('Book', backref='study_sessions', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/demo-login', methods=['POST'])
def demo_login():
    """Demo login endpoint that bypasses Google OAuth"""
    # Get or create demo user
    demo_user = User.query.filter_by(email='demo@example.com').first()
    if not demo_user:
        demo_user = User(
            email='demo@example.com',
            name='Alex',
            google_id='demo_user_123',
            is_approved=True,
            is_admin=False
        )
        db.session.add(demo_user)
        db.session.commit()
        
        # Add sample books
        sample_books = [
            Book(title="The Cat in the Hat", author="Dr. Seuss", 
                 summary="A super fun story about a cat who visits on a rainy day! The cat made everything messy but then cleaned it all up. I loved the Thing One and Thing Two characters!", 
                 user_id=demo_user.id),
            Book(title="Charlotte's Web", author="E.B. White", 
                 summary="This book made me cry happy tears! Charlotte the spider was so kind to Wilbur the pig. It taught me about friendship and being brave.", 
                 user_id=demo_user.id),
            Book(title="Where the Wild Things Are", author="Maurice Sendak", 
                 summary="Max went on the coolest adventure ever! The wild things looked scary but they were actually friendly. I wish I could sail to their island too!", 
                 user_id=demo_user.id)
        ]
        
        for book in sample_books:
            db.session.add(book)
        
        # Add sample study sessions
        
        subjects = ['maths', 'english', 'reading', 'science', 'writing']
        session_notes = {
            'maths': "Practiced multiplication tables and did some word problems. Getting faster!",
            'english': "Read a chapter and answered comprehension questions. Love this book!",
            'reading': "Finished reading a whole chapter today! The characters are so interesting!",
            'science': "Learned about the solar system. Jupiter is HUGE!",
            'writing': "Wrote a story about my pet hamster's adventures."
        }
        
        # Create study sessions from the past few days
        for i in range(6):
            days_ago = random.randint(0, 5)
            start_time = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(9, 16))
            duration = random.randint(15, 45)
            subject = random.choice(subjects)
            
            session = StudySession(
                subject=subject,
                start_time=start_time,
                end_time=start_time + timedelta(minutes=duration),
                duration_minutes=duration,
                notes=session_notes.get(subject, "Had a great study session!"),
                user_id=demo_user.id
            )
            db.session.add(session)
        
        db.session.commit()
    
    login_user(demo_user)
    return jsonify({'success': True})

@app.route('/auth/google', methods=['POST'])
def google_auth():
    token = request.json.get('token')
    
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), app.config['GOOGLE_CLIENT_ID'])
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo['name']
        
        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check if email is in admin list for admin privileges
            admin_emails = os.environ.get('ADMIN_EMAILS', '').split(',')
            admin_emails = [email.strip() for email in admin_emails if email.strip()]
            
            is_admin = email in admin_emails
            is_approved = True  # Auto-approve ALL users (no approval required)
            
            # Create new user
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
        
    except ValueError:
        return jsonify({'error': 'Invalid token'}), 400

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent books and study sessions
    recent_books = Book.query.filter_by(user_id=current_user.id).order_by(Book.date_read.desc()).limit(5).all()
    recent_sessions = StudySession.query.filter_by(user_id=current_user.id).filter(StudySession.end_time.isnot(None)).order_by(StudySession.start_time.desc()).limit(5).all()
    
    # Get all user's books for reading session selection
    user_books = Book.query.filter_by(user_id=current_user.id).order_by(Book.title.asc()).all()
    
    # Check for active study session
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    
    return render_template('dashboard.html', 
                         recent_books=recent_books, 
                         recent_sessions=recent_sessions,
                         active_session=active_session,
                         user_books=user_books)

@app.route('/books')
@login_required
def books():
    books_list = Book.query.filter_by(user_id=current_user.id).order_by(Book.date_read.desc()).all()
    return render_template('books.html', books=books_list)

@app.route('/books/add', methods=['POST'])
@login_required
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')
    summary = request.form.get('summary')
    
    if title:
        book = Book(title=title, author=author, summary=summary, user_id=current_user.id)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
    
    return redirect(url_for('books'))

@app.route('/study')
@login_required
def study_sessions():
    sessions = StudySession.query.filter_by(user_id=current_user.id).filter(StudySession.end_time.isnot(None)).order_by(StudySession.start_time.desc()).all()
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    
    # Get all user's books for reading session selection
    user_books = Book.query.filter_by(user_id=current_user.id).order_by(Book.title.asc()).all()
    
    return render_template('study_sessions.html', sessions=sessions, active_session=active_session, user_books=user_books)

@app.route('/study/start', methods=['POST'])
@login_required
def start_study():
    subject = request.form.get('subject')
    book_id = request.form.get('book_id')
    
    # Get browser timestamp if provided, otherwise use server time
    browser_time = request.form.get('start_time')
    if browser_time:
        try:
            start_time = datetime.fromisoformat(browser_time.replace('Z', '+00:00'))
        except:
            start_time = datetime.now(timezone.utc)
    else:
        start_time = datetime.now(timezone.utc)
    
    # End any existing active session first
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    if active_session:
        end_time = datetime.now(timezone.utc) if not browser_time else start_time
        active_session.end_time = end_time
        duration = (active_session.end_time - active_session.start_time).total_seconds() / 60
        active_session.duration_minutes = int(duration)
    
    # Validate book_id if provided (for reading sessions)
    book_id = int(book_id) if book_id and book_id.isdigit() else None
    
    # Start new session
    session = StudySession(subject=subject, start_time=start_time, user_id=current_user.id, book_id=book_id)
    db.session.add(session)
    db.session.commit()
    
    return jsonify({'success': True, 'session_id': session.id, 'start_time': start_time.isoformat()})

@app.route('/study/stop', methods=['POST'])
@login_required
def stop_study():
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    
    if active_session:
        # Get browser timestamp if provided
        browser_time = request.form.get('end_time')
        if browser_time:
            try:
                end_time = datetime.fromisoformat(browser_time.replace('Z', '+00:00'))
            except:
                end_time = datetime.now(timezone.utc)
        else:
            end_time = datetime.now(timezone.utc)
            
        active_session.end_time = end_time
        duration = (active_session.end_time - active_session.start_time).total_seconds() / 60
        active_session.duration_minutes = int(duration)
        
        notes = request.form.get('notes', '')
        if notes:
            active_session.notes = notes
        
        db.session.commit()
        
        return jsonify({'success': True, 'duration': active_session.duration_minutes})
    
    return jsonify({'error': 'No active session'}), 400

@app.route('/study/current')
@login_required
def current_study():
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    
    if active_session:
        elapsed = (datetime.now(timezone.utc) - active_session.start_time).total_seconds()
        return jsonify({
            'active': True,
            'subject': active_session.subject,
            'elapsed_seconds': int(elapsed),
            'start_time': active_session.start_time.isoformat()
        })
    
    return jsonify({'active': False})

@app.route('/leaderboard')
@login_required
def leaderboard():
    # Get all users with their total study minutes
    from sqlalchemy import func
    
    # Calculate total study minutes for each user
    leaderboard_data = db.session.query(
        User.id,
        User.name,
        User.email,
        func.coalesce(func.sum(StudySession.duration_minutes), 0).label('total_minutes')
    ).outerjoin(StudySession).group_by(User.id, User.name, User.email)\
     .order_by(func.coalesce(func.sum(StudySession.duration_minutes), 0).desc()).all()
    
    # Get subject breakdown for current user
    current_user_subjects = db.session.query(
        StudySession.subject,
        func.sum(StudySession.duration_minutes).label('minutes')
    ).filter_by(user_id=current_user.id)\
     .filter(StudySession.end_time.isnot(None))\
     .group_by(StudySession.subject).all()
    
    # Calculate total users and current user rank
    total_users = len(leaderboard_data)
    current_user_rank = next((i + 1 for i, user in enumerate(leaderboard_data) 
                            if user.id == current_user.id), total_users)
    
    # Get recent achievements (users who studied today)
    from datetime import date
    today_sessions = StudySession.query.join(User)\
        .filter(func.date(StudySession.start_time) == date.today())\
        .filter(StudySession.end_time.isnot(None))\
        .with_entities(User.name, StudySession.subject, StudySession.duration_minutes)\
        .order_by(StudySession.start_time.desc()).limit(10).all()
    
    return render_template('leaderboard.html', 
                         leaderboard=leaderboard_data,
                         current_user_subjects=current_user_subjects,
                         current_user_rank=current_user_rank,
                         total_users=total_users,
                         today_sessions=today_sessions)

# Admin routes for user approval
def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Get pending users
    pending_users = User.query.filter_by(is_approved=False).order_by(User.approval_requested_at.desc()).all()
    
    # Get all users for management
    all_users = User.query.order_by(User.created_at.desc()).all()
    
    return render_template('admin.html', 
                         pending_users=pending_users,
                         all_users=all_users)

@app.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    flash(f'User {user.name} ({user.email}) has been approved!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/deny/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def deny_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Remove the user entirely (they can re-register if needed)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User request from {user.name} ({user.email}) has been denied and removed.', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin from yourself
    if user.id == current_user.id:
        flash('You cannot remove admin privileges from yourself!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for {user.name} ({user.email})', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/test-oauth')
def test_oauth():
    """Simple OAuth test page"""
    client_id = app.config.get('GOOGLE_CLIENT_ID', 'NOT_SET')
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>OAuth Test</title>
    <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>
<body>
    <h1>OAuth Test Page</h1>
    <p>Client ID: {client_id}</p>
    
    <div id="g_id_onload"
         data-client_id="{client_id}"
         data-context="signin"
         data-ux_mode="popup"
         data-callback="handleCredentialResponse"
         data-auto_prompt="false">
    </div>
    
    <div class="g_id_signin"
         data-type="standard"
         data-shape="rectangular"
         data-theme="outline"
         data-text="signin_with"
         data-size="large">
    </div>
    
    <script>
    function handleCredentialResponse(response) {{
        alert('OAuth Success! Token received: ' + response.credential.substring(0, 50) + '...');
        console.log('Token:', response.credential);
    }}
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))
