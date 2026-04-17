# all API routes
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta

from database import (
    create_user, get_user_by_email, get_user_by_id, update_last_login,
    setup_default_categories, create_task, get_tasks_by_user, get_task_by_id,
    update_task, complete_task, delete_task, update_daily_stats,
    create_focus_session, end_focus_session, get_user_sessions,
    get_session_streak, get_task_by_id, log_app_usage, get_app_usage_today,
    get_daily_stats, get_weekly_stats, get_app_category,
    get_distraction_apps, create_distraction_alert
)
from priority import (
    hash_password, verify_password, generate_token, token_required,
    calculate_priority, get_urgency_level, calculate_focus_score,
    get_task_priority_summary, DEFAULT_POMODORO
)

api = Blueprint('api', __name__)


# Auth Routes

@api.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()

    if not email or '@' not in email:
        return jsonify({'error': 'Valid email is required'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    # check if email exists
    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 409

    # create user
    password_hash = hash_password(password)
    user_id = create_user(email, password_hash, name)

    if not user_id:
        return jsonify({'error': 'Failed to create user'}), 500

    setup_default_categories(user_id)
    token = generate_token(user_id, email)

    return jsonify({
        'message': 'Registration successful',
        'user': {'user_id': user_id, 'email': email, 'name': name},
        'token': token
    }), 201


@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    if not verify_password(password, user['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401

    update_last_login(user['user_id'])
    token = generate_token(user['user_id'], email)

    return jsonify({
        'message': 'Login successful',
        'user': {'user_id': user['user_id'], 'email': user['email'], 'name': user['name']},
        'token': token
    }), 200


@api.route('/auth/profile', methods=['GET'])
@token_required
def get_profile():
    user = get_user_by_id(request.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user}), 200


@api.route('/auth/verify', methods=['GET'])
@token_required
def verify_token():
    return jsonify({
        'valid': True,
        'user_id': request.user_id,
        'email': request.email
    }), 200


# Task Routes

@api.route('/tasks', methods=['GET'])
@token_required
def get_all_tasks():
    status = request.args.get('status', 'pending')

    if status == 'all':
        tasks = get_tasks_by_user(request.user_id)
    else:
        tasks = get_tasks_by_user(request.user_id, status)

    if tasks is None:
        return jsonify({'error': 'Failed to fetch tasks'}), 500

    today = date.today()
    for task in tasks:
        deadline = task.get('deadline')
        if isinstance(deadline, str):
            deadline = datetime.strptime(deadline, '%Y-%m-%d').date()

        days_remaining = (deadline - today).days if deadline else 999
        task['days_remaining'] = days_remaining

        if task.get('status') == 'completed':
            task['urgency_level'] = 'COMPLETED'
            task['urgency_color'] = '#4CAF50'
        else:
            complexity = task.get('complexity', 3)
            priority_score = calculate_priority(deadline, complexity)
            task['priority_score'] = priority_score

            level, color = get_urgency_level(priority_score, days_remaining)
            task['urgency_level'] = level
            task['urgency_color'] = color

        # format dates for json
        if task.get('deadline'):
            task['deadline'] = task['deadline'].strftime('%Y-%m-%d') if hasattr(task['deadline'], 'strftime') else str(task['deadline'])
        if task.get('created_at'):
            task['created_at'] = task['created_at'].isoformat() if hasattr(task['created_at'], 'isoformat') else str(task['created_at'])
        if task.get('completed_at'):
            task['completed_at'] = task['completed_at'].isoformat() if hasattr(task['completed_at'], 'isoformat') else str(task['completed_at'])

    summary = get_task_priority_summary(tasks)
    return jsonify({'tasks': tasks, 'summary': summary}), 200


@api.route('/tasks', methods=['POST'])
@token_required
def create_new_task():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    title = data.get('title', '').strip()
    deadline = data.get('deadline', '')
    complexity = data.get('complexity')

    if not title:
        return jsonify({'error': 'Title is required'}), 400
    if not deadline:
        return jsonify({'error': 'Deadline is required'}), 400
    if not complexity or complexity not in [1, 2, 3, 4, 5]:
        return jsonify({'error': 'Complexity must be between 1-5'}), 400

    try:
        deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Deadline must be in YYYY-MM-DD format'}), 400

    priority_score = calculate_priority(deadline_date, complexity)
    category = data.get('category', 'Study')
    description = data.get('description', '')

    task_id = create_task(
        user_id=request.user_id, title=title, deadline=deadline,
        complexity=complexity, category=category,
        priority_score=priority_score, description=description
    )

    if not task_id:
        return jsonify({'error': 'Failed to create task'}), 500

    days_remaining = (deadline_date - date.today()).days
    level, color = get_urgency_level(priority_score, days_remaining)

    return jsonify({
        'message': 'Task created successfully',
        'task': {
            'task_id': task_id, 'title': title, 'deadline': deadline,
            'complexity': complexity, 'category': category,
            'priority_score': priority_score, 'urgency_level': level,
            'urgency_color': color, 'days_remaining': days_remaining,
            'status': 'pending'
        }
    }), 201


@api.route('/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_single_task(task_id):
    task = get_task_by_id(task_id, request.user_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    deadline = task.get('deadline')
    if isinstance(deadline, str):
        deadline = datetime.strptime(deadline, '%Y-%m-%d').date()

    days_remaining = (deadline - date.today()).days if deadline else 999
    priority_score = task.get('priority_score', 999)
    level, color = get_urgency_level(priority_score, days_remaining)

    task['urgency_level'] = level
    task['urgency_color'] = color
    task['days_remaining'] = days_remaining

    return jsonify({'task': task}), 200


@api.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_existing_task(task_id):
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    existing_task = get_task_by_id(task_id, request.user_id)
    if not existing_task:
        return jsonify({'error': 'Task not found'}), 404

    update_data = {}

    if 'title' in data:
        update_data['title'] = data['title'].strip()
    if 'description' in data:
        update_data['description'] = data['description']
    if 'category' in data:
        update_data['category'] = data['category']

    deadline = data.get('deadline', existing_task.get('deadline'))
    complexity = data.get('complexity', existing_task.get('complexity'))

    if 'deadline' in data:
        try:
            datetime.strptime(data['deadline'], '%Y-%m-%d')
            update_data['deadline'] = data['deadline']
        except ValueError:
            return jsonify({'error': 'Invalid deadline format'}), 400

    if 'complexity' in data:
        if data['complexity'] not in [1, 2, 3, 4, 5]:
            return jsonify({'error': 'Complexity must be between 1-5'}), 400
        update_data['complexity'] = data['complexity']

    if 'deadline' in data or 'complexity' in data:
        priority_score = calculate_priority(deadline, complexity)
        update_data['priority_score'] = priority_score

    result = update_task(task_id, request.user_id, **update_data)

    if result is None:
        return jsonify({'error': 'Failed to update task'}), 500

    return jsonify({'message': 'Task updated successfully'}), 200


@api.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_existing_task(task_id):
    existing_task = get_task_by_id(task_id, request.user_id)
    if not existing_task:
        return jsonify({'error': 'Task not found'}), 404

    result = delete_task(task_id, request.user_id)
    if result is None:
        return jsonify({'error': 'Failed to delete task'}), 500

    return jsonify({'message': 'Task deleted successfully'}), 200


@api.route('/tasks/<int:task_id>/complete', methods=['PATCH'])
@token_required
def mark_task_complete(task_id):
    existing_task = get_task_by_id(task_id, request.user_id)
    if not existing_task:
        return jsonify({'error': 'Task not found'}), 404

    if existing_task.get('status') == 'completed':
        return jsonify({'message': 'Task is already completed'}), 200

    result = complete_task(task_id, request.user_id)
    if result is None:
        return jsonify({'error': 'Failed to complete task'}), 500

    update_daily_stats(user_id=request.user_id, tasks_completed=1)
    return jsonify({'message': 'Task marked as completed! 🎉'}), 200


# Focus Session Routes

@api.route('/sessions/start', methods=['POST'])
@token_required
def start_session():
    data = request.get_json() or {}

    task_id = data.get('task_id')
    duration = data.get('duration', DEFAULT_POMODORO)

    task_info = None
    if task_id:
        task = get_task_by_id(task_id, request.user_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        task_info = {
            'task_id': task_id,
            'title': task.get('title'),
            'priority_score': task.get('priority_score')
        }

    session_id = create_focus_session(user_id=request.user_id, task_id=task_id)

    if not session_id:
        return jsonify({'error': 'Failed to start session'}), 500

    return jsonify({
        'message': 'Focus session started! 🎯',
        'session_id': session_id,
        'duration_minutes': duration,
        'task': task_info,
        'start_time': datetime.now().isoformat(),
        'tips': [
            'Put your phone face down',
            'Close unnecessary tabs',
            'Stay focused on one task',
            'You got this! 💪'
        ]
    }), 201


@api.route('/sessions/end', methods=['POST'])
@token_required
def end_session():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    session_id = data.get('session_id')
    completed = data.get('completed', False)
    interruptions = data.get('interruptions', 0)
    focus_score = data.get('focus_score', 0)

    if not session_id:
        return jsonify({'error': 'Session ID is required'}), 400

    result = end_focus_session(
        session_id=session_id, user_id=request.user_id,
        completed=completed, interruptions=interruptions,
        focus_score=focus_score
    )

    if result is None:
        return jsonify({'error': 'Failed to end session'}), 500

    # update daily stats
    if completed:
        sessions_list = get_user_sessions(request.user_id, 1)
        session_duration = 0
        if sessions_list:
            for s in sessions_list:
                if s.get('session_id') == session_id:
                    session_duration = s.get('duration_minutes', 0) or 0
                    break

        update_daily_stats(
            user_id=request.user_id,
            productive_time=session_duration,
            sessions_completed=1
        )

    streak_data = get_session_streak(request.user_id)
    streak = streak_data.get('streak', 0) if streak_data else 0

    if completed and interruptions == 0:
        feedback = "Perfect session! No interruptions! 🌟"
    elif completed:
        feedback = f"Great job completing the session! {interruptions} interruption(s). 👍"
    else:
        feedback = "Session ended early. Every bit of focus counts! 💪"

    return jsonify({
        'message': feedback,
        'session_id': session_id,
        'completed': completed,
        'interruptions': interruptions,
        'focus_score': focus_score,
        'current_streak': streak,
        'streak_message': f"🔥 {streak} day streak!" if streak > 0 else "Start a streak today!"
    }), 200


@api.route('/sessions/history', methods=['GET'])
@token_required
def get_session_history():
    limit = request.args.get('limit', 10, type=int)
    sessions = get_user_sessions(request.user_id, limit)

    if sessions is None:
        return jsonify({'error': 'Failed to fetch sessions'}), 500

    for session in sessions:
        if session.get('start_time'):
            session['start_time'] = session['start_time'].isoformat()
        if session.get('end_time'):
            session['end_time'] = session['end_time'].isoformat()

    return jsonify({'sessions': sessions, 'count': len(sessions)}), 200


@api.route('/sessions/streak', methods=['GET'])
@token_required
def get_streak():
    streak_data = get_session_streak(request.user_id)
    streak = streak_data.get('streak', 0) if streak_data else 0

    if streak >= 30:
        status = "🏆 LEGENDARY"
        message = "30+ days! You're unstoppable!"
    elif streak >= 14:
        status = "⭐ AMAZING"
        message = "2+ weeks strong!"
    elif streak >= 7:
        status = "🔥 ON FIRE"
        message = "A whole week! Keep it up!"
    elif streak >= 3:
        status = "💪 BUILDING"
        message = "Great momentum!"
    elif streak >= 1:
        status = "🌱 STARTING"
        message = "Every journey starts with day 1!"
    else:
        status = "🎯 BEGIN"
        message = "Complete a focus session to start your streak!"

    return jsonify({
        'streak': streak,
        'status': status,
        'message': message,
        'next_milestone': 7 if streak < 7 else 14 if streak < 14 else 30 if streak < 30 else streak + 10
    }), 200


@api.route('/sessions/stats', methods=['GET'])
@token_required
def get_session_stats():
    sessions = get_user_sessions(request.user_id, 100) or []

    total_sessions = len(sessions)
    completed_sessions = sum(1 for s in sessions if s.get('completed'))
    total_minutes = sum(s.get('duration_minutes', 0) for s in sessions)
    avg_focus = sum(s.get('focus_score', 0) for s in sessions) // total_sessions if total_sessions > 0 else 0

    streak_data = get_session_streak(request.user_id)
    streak = streak_data.get('streak', 0) if streak_data else 0

    return jsonify({
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'completion_rate': round(completed_sessions / total_sessions * 100, 1) if total_sessions > 0 else 0,
        'total_focus_time': total_minutes,
        'total_focus_time_formatted': f"{total_minutes // 60}h {total_minutes % 60}m",
        'average_focus_score': avg_focus,
        'current_streak': streak
    }), 200


# Analytics Routes
def format_minutes(minutes):
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m" if mins else f"{hours}h"


@api.route('/analytics/daily', methods=['GET'])
@token_required
def get_daily_analytics():
    user_id = request.user_id
    stats = get_daily_stats(user_id)

    if not stats:
        stats = {
            'date': date.today().isoformat(),
            'total_screen_time': 0,
            'productive_time': 0,
            'distraction_time': 0,
            'focus_score': 0,
            'tasks_completed': 0,
            'focus_sessions_completed': 0
        }

    score, rating, color = calculate_focus_score(
        stats.get('productive_time', 0),
        stats.get('total_screen_time', 0)
    )

    app_usage = get_app_usage_today(user_id) or []
    top_apps = app_usage[:5] if app_usage else []

    return jsonify({
        'date': date.today().isoformat(),
        'focus_score': score,
        'focus_rating': rating,
        'focus_color': color,
        'total_screen_time': stats.get('total_screen_time', 0),
        'total_screen_time_formatted': format_minutes(stats.get('total_screen_time', 0)),
        'productive_time': stats.get('productive_time', 0),
        'productive_time_formatted': format_minutes(stats.get('productive_time', 0)),
        'distraction_time': stats.get('distraction_time', 0),
        'distraction_time_formatted': format_minutes(stats.get('distraction_time', 0)),
        'tasks_completed': stats.get('tasks_completed', 0),
        'focus_sessions_completed': stats.get('focus_sessions_completed', 0),
        'top_apps': top_apps
    }), 200


@api.route('/analytics/weekly', methods=['GET'])
@token_required
def get_weekly_analytics():
    user_id = request.user_id
    weekly_data = get_weekly_stats(user_id) or []

    if not weekly_data:
        return jsonify({
            'days': [],
            'average_focus_score': 0,
            'total_productive_time': 0,
            'total_distraction_time': 0,
            'best_day': None
        }), 200

    total_focus = sum(d.get('focus_score', 0) for d in weekly_data)
    avg_focus = total_focus // len(weekly_data) if weekly_data else 0
    total_productive = sum(d.get('productive_time', 0) for d in weekly_data)
    total_distraction = sum(d.get('distraction_time', 0) for d in weekly_data)
    best_day = max(weekly_data, key=lambda x: x.get('focus_score', 0)) if weekly_data else None

    for day in weekly_data:
        if day.get('date'):
            day['date'] = day['date'].isoformat() if hasattr(day['date'], 'isoformat') else str(day['date'])

    return jsonify({
        'days': weekly_data,
        'average_focus_score': avg_focus,
        'total_productive_time': total_productive,
        'total_distraction_time': total_distraction,
        'best_day': best_day
    }), 200


@api.route('/analytics/app-usage', methods=['POST'])
@token_required
def log_app_usage_endpoint():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    app_name = data.get('app_name', '').strip()
    duration_seconds = data.get('duration_seconds', 0)
    session_id = data.get('session_id')

    if not app_name:
        return jsonify({'error': 'App name is required'}), 400

    category = get_app_category(request.user_id, app_name)

    log_app_usage(
        user_id=request.user_id, app_name=app_name,
        app_category=category, duration_seconds=duration_seconds,
        session_id=session_id
    )

    productive_time = duration_seconds // 60 if category == 'productive' else 0
    distraction_time = duration_seconds // 60 if category == 'distraction' else 0

    update_daily_stats(
        user_id=request.user_id,
        productive_time=productive_time,
        distraction_time=distraction_time
    )

    return jsonify({
        'logged': True,
        'app_name': app_name,
        'category': category,
        'is_distraction': category == 'distraction'
    }), 200


@api.route('/analytics/check-distraction', methods=['POST'])
@token_required
def check_distraction():
    data = request.get_json()

    if not data:
        return jsonify({'should_alert': False}), 200

    app_name = data.get('app_name', '')
    time_on_app = data.get('time_on_app', 0)
    session_id = data.get('session_id')
    threshold = data.get('threshold', 300)

    distraction_apps = get_distraction_apps(request.user_id)
    is_distraction = app_name in distraction_apps
    over_threshold = time_on_app >= threshold

    if is_distraction and over_threshold:
        alert_type = 'critical' if time_on_app > 600 else 'warning'
        message = f"You've spent {time_on_app // 60} minutes on {app_name}. Time to refocus!"

        alert_id = create_distraction_alert(
            user_id=request.user_id, session_id=session_id,
            app_name=app_name, alert_type=alert_type,
            message=message, time_on_app=time_on_app
        )

        return jsonify({
            'should_alert': True,
            'alert_id': alert_id,
            'alert_type': alert_type,
            'app_name': app_name,
            'time_on_app': time_on_app,
            'time_formatted': f"{time_on_app // 60} minutes",
            'message': message
        }), 200

    return jsonify({
        'should_alert': False,
        'is_distraction': is_distraction,
        'time_on_app': time_on_app
    }), 200


@api.route('/analytics/focus-score', methods=['GET'])
@token_required
def get_focus_score():
    stats = get_daily_stats(request.user_id)

    if not stats or stats.get('total_screen_time', 0) == 0:
        return jsonify({
            'focus_score': 0,
            'rating': 'N/A',
            'color': '#CCCCCC',
            'productive_time': 0,
            'distraction_time': 0,
            'message': 'Start tracking to see your focus score!'
        }), 200

    score, rating, color = calculate_focus_score(
        stats.get('productive_time', 0),
        stats.get('total_screen_time', 0)
    )

    if score >= 80:
        message = "Outstanding! You're crushing it today! 🌟"
    elif score >= 60:
        message = "Good work! Keep the momentum going! 💪"
    elif score >= 40:
        message = "Room for improvement. Try a focus session! ⚡"
    else:
        message = "Time to refocus! Your priority tasks need attention. 🎯"

    return jsonify({
        'focus_score': score,
        'rating': rating,
        'color': color,
        'productive_time': stats.get('productive_time', 0),
        'distraction_time': stats.get('distraction_time', 0),
        'message': message
    }), 200
