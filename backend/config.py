"""
Procrastify Backend Configuration
"""
import os
from datetime import timedelta

class Config:
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'procrastify-super-secret-key-2026')
    DEBUG = True
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-procrastify-secret-2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # MySQL Database Settings (XAMPP Default)
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')  # XAMPP default is empty
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'procrastify')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    
    # CORS Settings
    CORS_ORIGINS = ['*']  # Allow all origins
    
    # App Settings
    DEFAULT_POMODORO_DURATION = 25  # minutes
    DEFAULT_BREAK_DURATION = 5  # minutes
    DISTRACTION_THRESHOLD = 300  # 5 minutes in seconds


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')


# Current configuration
current_config = DevelopmentConfig()
