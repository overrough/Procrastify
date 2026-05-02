import bcrypt
import jwt
from datetime import datetime, date, timedelta
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'procrastify-super-secret-key-2026')
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'jwt-procrastify-secret-2026')
JWT_EXPIRY_DAYS = 7
DEFAULT_POMODORO = 15
DEFAULT_BREAK = 5

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token(user_id, email):
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRY_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        request.user_id = payload['user_id']
        request.email = payload['email']
        return f(*args, **kwargs)
    return decorated

def calculate_priority(deadline, complexity):
    if isinstance(deadline, str):
        deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
    elif isinstance(deadline, datetime):
        deadline = deadline.date()
    days_remaining = (deadline - date.today()).days
    if days_remaining <= 0:
        return 0
    return round(days_remaining / complexity)

def get_urgency_level(priority_score, days_remaining):
    if priority_score == 0 or days_remaining <= 0:
        return ('OVERDUE', '#FF0000')
    elif priority_score <= 3:
        return ('HIGH', '#FF4444')
    elif priority_score <= 8:
        return ('MEDIUM', '#FFB347')
    elif priority_score <= 15:
        return ('LOW', '#77DD77')
    else:
        return ('RELAXED', '#90EE90')

def calculate_focus_score(productive_time, total_time):
    if total_time <= 0:
        return (0, 'N/A', '#CCCCCC')
    score = int((productive_time / total_time) * 100)
    if score >= 80:
        return (score, 'EXCELLENT 🌟', '#4CAF50')
    elif score >= 60:
        return (score, 'GOOD 👍', '#8BC34A')
    elif score >= 40:
        return (score, 'FAIR ⚠️', '#FF9800')
    else:
        return (score, 'POOR ❌', '#F44336')

def get_task_priority_summary(tasks):
    summary = {
        'overdue': 0, 'high': 0, 'medium': 0,
        'low': 0, 'completed': 0, 'total': len(tasks)
    }
    for task in tasks:
        level = task.get('urgency_level', 'LOW').upper()
        if level == 'COMPLETED':
            summary['completed'] += 1
        elif level == 'OVERDUE':
            summary['overdue'] += 1
        elif level == 'HIGH':
            summary['high'] += 1
        elif level == 'MEDIUM':
            summary['medium'] += 1
        else:
            summary['low'] += 1
    return summary
