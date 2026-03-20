
# backend config

import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class Config:
    # flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'procrastify-super-secret-key-2026')
    DEBUG = True
    
    # jwt settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-procrastify-secret-2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # db settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'procrastify')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    
    # cors settings
    CORS_ORIGINS = ['*']
    
    # app settings
    DEFAULT_POMODORO_DURATION = 15
    DEFAULT_BREAK_DURATION = 5
    DISTRACTION_THRESHOLD = 300 


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')


# current config
current_config = ProductionConfig() if os.environ.get("RENDER") else DevelopmentConfig()
