"""
Authentication Routes for Procrastify
Handles user registration, login, and profile
"""
from flask import Blueprint, request, jsonify
import sys
sys.path.append('..')
from models.models import create_user, get_user_by_email, get_user_by_id, update_last_login
from utils.auth_utils import hash_password, verify_password, generate_token, token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request Body:
        - email: User's email address
        - password: User's password (min 6 characters)
        - name: User's display name
    
    Returns:
        - Success: User info and JWT token
        - Error: Error message
    """
    data = request.get_json()
    
    # Validate required fields
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    
    # Validate email
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email is required'}), 400
    
    # Validate password
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Validate name
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    # Check if email already exists
    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 409
    
    # Hash password and create user
    password_hash = hash_password(password)
    user_id = create_user(email, password_hash, name)
    
    if not user_id:
        return jsonify({'error': 'Failed to create user'}), 500
    
    # Generate JWT token
    token = generate_token(user_id, email)
    
    return jsonify({
        'message': 'Registration successful',
        'user': {
            'user_id': user_id,
            'email': email,
            'name': name
        },
        'token': token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token
    
    Request Body:
        - email: User's email
        - password: User's password
    
    Returns:
        - Success: User info and JWT token
        - Error: Error message
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Get user by email
    user = get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Verify password
    if not verify_password(password, user['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Update last login
    update_last_login(user['user_id'])
    
    # Generate JWT token
    token = generate_token(user['user_id'], email)
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'user_id': user['user_id'],
            'email': user['email'],
            'name': user['name']
        },
        'token': token
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """
    Get current user's profile (requires authentication)
    
    Headers:
        - Authorization: Bearer <token>
    
    Returns:
        - User profile info
    """
    user = get_user_by_id(request.user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user
    }), 200


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    """
    Verify if the JWT token is valid
    
    Headers:
        - Authorization: Bearer <token>
    
    Returns:
        - Valid: User ID and email
        - Invalid: 401 error
    """
    return jsonify({
        'valid': True,
        'user_id': request.user_id,
        'email': request.email
    }), 200
