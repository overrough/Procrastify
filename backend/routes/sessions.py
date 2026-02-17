"""
Focus Session Routes for Procrastify
Pomodoro timer and session management
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
import sys
sys.path.append('..')
from models.models import (
    create_focus_session, end_focus_session, get_user_sessions,
    get_session_streak, update_daily_stats, get_task_by_id
)
from utils.auth_utils import token_required
from config import current_config

sessions_bp = Blueprint('sessions', __name__)


@sessions_bp.route('/start', methods=['POST'])
@token_required
def start_session():
    """
    Start a new focus session (Pomodoro)
    
    Request Body:
        - task_id: Optional task to associate with session
        - duration: Session duration in minutes (default 25)
    
    Returns:
        - Session ID and details
    """
    data = request.get_json() or {}
    
    task_id = data.get('task_id')
    duration = data.get('duration', current_config.DEFAULT_POMODORO_DURATION)
    
    # Validate task if provided
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
    
    # Create session
    session_id = create_focus_session(
        user_id=request.user_id,
        task_id=task_id
    )
    
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


@sessions_bp.route('/end', methods=['POST'])
@token_required
def end_session():
    """
    End a focus session
    
    Request Body:
        - session_id: Session to end
        - completed: Whether session was completed fully
        - interruptions: Number of interruptions
        - focus_score: Calculated focus score for this session
    
    Returns:
        - Session summary
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    session_id = data.get('session_id')
    completed = data.get('completed', False)
    interruptions = data.get('interruptions', 0)
    focus_score = data.get('focus_score', 0)
    
    if not session_id:
        return jsonify({'error': 'Session ID is required'}), 400
    
    # End session
    result = end_focus_session(
        session_id=session_id,
        user_id=request.user_id,
        completed=completed,
        interruptions=interruptions,
        focus_score=focus_score
    )
    
    if result is None:
        return jsonify({'error': 'Failed to end session'}), 500
    
    # Update daily stats
    if completed:
        update_daily_stats(
            user_id=request.user_id,
            sessions_completed=1
        )
    
    # Get streak
    streak_data = get_session_streak(request.user_id)
    streak = streak_data.get('streak', 0) if streak_data else 0
    
    # Generate feedback
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


@sessions_bp.route('/history', methods=['GET'])
@token_required
def get_session_history():
    """
    Get recent focus sessions
    
    Query Parameters:
        - limit: Number of sessions to return (default 10)
    
    Returns:
        - List of recent sessions
    """
    limit = request.args.get('limit', 10, type=int)
    
    sessions = get_user_sessions(request.user_id, limit)
    
    if sessions is None:
        return jsonify({'error': 'Failed to fetch sessions'}), 500
    
    # Format datetime objects
    for session in sessions:
        if session.get('start_time'):
            session['start_time'] = session['start_time'].isoformat()
        if session.get('end_time'):
            session['end_time'] = session['end_time'].isoformat()
    
    return jsonify({
        'sessions': sessions,
        'count': len(sessions)
    }), 200


@sessions_bp.route('/streak', methods=['GET'])
@token_required
def get_streak():
    """
    Get current focus session streak
    
    Returns:
        - Current streak count
        - Streak status
    """
    streak_data = get_session_streak(request.user_id)
    streak = streak_data.get('streak', 0) if streak_data else 0
    
    # Determine streak status
    if streak >= 30:
        status = "🏆 LEGENDARY"
        message = f"30+ days! You're unstoppable!"
    elif streak >= 14:
        status = "⭐ AMAZING"
        message = f"2+ weeks strong!"
    elif streak >= 7:
        status = "🔥 ON FIRE"
        message = f"A whole week! Keep it up!"
    elif streak >= 3:
        status = "💪 BUILDING"
        message = f"Great momentum!"
    elif streak >= 1:
        status = "🌱 STARTING"
        message = f"Every journey starts with day 1!"
    else:
        status = "🎯 BEGIN"
        message = "Complete a focus session to start your streak!"
    
    return jsonify({
        'streak': streak,
        'status': status,
        'message': message,
        'next_milestone': 7 if streak < 7 else 14 if streak < 14 else 30 if streak < 30 else streak + 10
    }), 200


@sessions_bp.route('/stats', methods=['GET'])
@token_required
def get_session_stats():
    """
    Get overall session statistics
    """
    sessions = get_user_sessions(request.user_id, 100) or []
    
    total_sessions = len(sessions)
    completed_sessions = sum(1 for s in sessions if s.get('completed'))
    total_minutes = sum(s.get('duration_minutes', 0) for s in sessions)
    avg_focus_score = sum(s.get('focus_score', 0) for s in sessions) // total_sessions if total_sessions > 0 else 0
    
    streak_data = get_session_streak(request.user_id)
    streak = streak_data.get('streak', 0) if streak_data else 0
    
    return jsonify({
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'completion_rate': round(completed_sessions / total_sessions * 100, 1) if total_sessions > 0 else 0,
        'total_focus_time': total_minutes,
        'total_focus_time_formatted': f"{total_minutes // 60}h {total_minutes % 60}m",
        'average_focus_score': avg_focus_score,
        'current_streak': streak
    }), 200
