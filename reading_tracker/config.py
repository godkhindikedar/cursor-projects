import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    # Azure will provide SQLCONNSTR_DefaultConnection, we'll transform it
    database_url = os.environ.get('DATABASE_URL')
    
    # Azure App Service provides connection strings in a specific format
    if not database_url:
        # Check for Azure SQL connection string format
        azure_sql = os.environ.get('SQLCONNSTR_DefaultConnection')
        if azure_sql:
            # Transform Azure connection string to SQLAlchemy format
            # Azure format: Server=tcp:server.database.windows.net,1433;Database=dbname;User ID=user;Password=pass;
            import re
            if azure_sql.startswith('Server='):
                # Parse Azure connection string
                server_match = re.search(r'Server=tcp:([^,]+),1433', azure_sql)
                db_match = re.search(r'Database=([^;]+)', azure_sql)
                user_match = re.search(r'User ID=([^;]+)', azure_sql)
                pass_match = re.search(r'Password=([^;]+)', azure_sql)
                
                if all([server_match, db_match, user_match, pass_match]):
                    server = server_match.group(1)
                    database = db_match.group(1)
                    username = user_match.group(1)
                    password = pass_match.group(1)
                    database_url = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    
    # Fallback to SQLite for development
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///reading_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    
    # Azure-specific settings
    AZURE_DEPLOYMENT = os.environ.get('WEBSITE_SITE_NAME') is not None  # Azure App Service sets this
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    # Additional production settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
class AzureConfig(ProductionConfig):
    # Azure-specific production settings
    pass
