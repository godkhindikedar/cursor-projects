from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://username:password@localhost/reading_tracker')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    books = db.relationship('Book', backref='user', lazy=True)
    study_sessions = db.relationship('StudySession', backref='user', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    summary = db.Column(db.Text)
    date_read = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)  # maths, writing, english, science, social_studies
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)  # calculated field
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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
            # Create new user
            user = User(google_id=google_id, email=email, name=name)
            db.session.add(user)
            db.session.commit()
        
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
    
    # Check for active study session
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    
    return render_template('dashboard.html', 
                         recent_books=recent_books, 
                         recent_sessions=recent_sessions,
                         active_session=active_session)

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
    
    return render_template('study_sessions.html', sessions=sessions, active_session=active_session)

@app.route('/study/start', methods=['POST'])
@login_required
def start_study():
    subject = request.form.get('subject')
    
    # End any existing active session first
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    if active_session:
        active_session.end_time = datetime.utcnow()
        duration = (active_session.end_time - active_session.start_time).total_seconds() / 60
        active_session.duration_minutes = int(duration)
    
    # Start new session
    session = StudySession(subject=subject, start_time=datetime.utcnow(), user_id=current_user.id)
    db.session.add(session)
    db.session.commit()
    
    return jsonify({'success': True, 'session_id': session.id})

@app.route('/study/stop', methods=['POST'])
@login_required
def stop_study():
    active_session = StudySession.query.filter_by(user_id=current_user.id, end_time=None).first()
    
    if active_session:
        active_session.end_time = datetime.utcnow()
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
        elapsed = (datetime.utcnow() - active_session.start_time).total_seconds()
        return jsonify({
            'active': True,
            'subject': active_session.subject,
            'elapsed_seconds': int(elapsed),
            'start_time': active_session.start_time.isoformat()
        })
    
    return jsonify({'active': False})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
