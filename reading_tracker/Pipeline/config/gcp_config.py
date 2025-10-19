# GCP-specific configuration for Reading Tracker
# This configuration is designed for Google Cloud Run deployment

import os
import json
from pathlib import Path

class GCPConfig:
    """Configuration class for GCP deployment"""
    
    # Project and environment
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')
    ENVIRONMENT = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Secret management - secrets are mounted as files in Cloud Run
    SECRETS_DIR = Path('/secrets')
    
    @classmethod
    def get_secret(cls, secret_name, default=None):
        """Read secret from mounted file or environment variable"""
        # Try to read from mounted secret file first (Cloud Run with secrets)
        secret_file = cls.SECRETS_DIR / secret_name
        if secret_file.exists():
            try:
                return secret_file.read_text().strip()
            except Exception as e:
                print(f"Warning: Could not read secret file {secret_file}: {e}")
        
        # Fallback to environment variable
        env_var = secret_name.upper().replace('-', '_')
        value = os.environ.get(env_var, default)
        
        if value is None:
            print(f"Warning: Secret {secret_name} not found in files or environment")
        
        return value
    
    # Application secrets - initialized at class level
    def __init__(self):
        pass
    
    @classmethod
    def get_config_dict(cls):
        """Get configuration as a dictionary for Flask"""
        config = {}
        config['SECRET_KEY'] = cls.get_secret(cls, 'secret-key') or os.environ.get('SECRET_KEY', 'dev-key-change-me')
        config['GOOGLE_CLIENT_ID'] = cls.get_secret(cls, 'google-client-id') or os.environ.get('GOOGLE_CLIENT_ID')
        admin_emails_str = cls.get_secret(cls, 'admin-emails', '') or os.environ.get('ADMIN_EMAILS', '')
        config['ADMIN_EMAILS'] = [email.strip() for email in admin_emails_str.split(',') if email.strip()]
        return config
    
    # Database configuration
    # For Cloud Run with SQLite, use persistent volume mount
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///data/reading_tracker.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 10
    }
    
    # Session configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # File upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Health check configuration
    HEALTH_CHECK_PATH = '/health'
    
    # Google Cloud specific settings
    @classmethod
    def is_cloud_run(cls):
        """Check if running on Cloud Run"""
        return bool(os.environ.get('K_SERVICE'))
    
    @classmethod
    def get_service_url(cls):
        """Get the Cloud Run service URL"""
        if cls.is_cloud_run():
            # Cloud Run automatically sets these
            service = os.environ.get('K_SERVICE', 'unknown')
            region = os.environ.get('GOOGLE_CLOUD_REGION', 'unknown')
            project = cls.GOOGLE_CLOUD_PROJECT
            return f"https://{service}-{region}.run.app"
        return "http://localhost:8080"
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        errors = []
        
        secret_key = cls.get_secret(cls, 'secret-key') or os.environ.get('SECRET_KEY', 'dev-key-change-me')
        if not secret_key or secret_key == 'dev-key-change-me':
            errors.append("SECRET_KEY must be set to a secure value")
        
        google_client_id = cls.get_secret(cls, 'google-client-id') or os.environ.get('GOOGLE_CLIENT_ID')
        if not google_client_id:
            errors.append("GOOGLE_CLIENT_ID must be set for OAuth authentication")
        
        if cls.is_cloud_run() and not cls.GOOGLE_CLOUD_PROJECT:
            errors.append("GOOGLE_CLOUD_PROJECT must be set in Cloud Run")
        
        return errors

class DevelopmentGCPConfig(GCPConfig):
    """Development configuration for GCP testing"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP for local testing
    LOG_LEVEL = 'DEBUG'

class ProductionGCPConfig(GCPConfig):
    """Production configuration for GCP"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'INFO'
    
    # Additional security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }

def get_config():
    """Get the appropriate configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'production')
    
    if env == 'development':
        return DevelopmentGCPConfig
    else:
        return ProductionGCPConfig

# Export the config
Config = get_config()
