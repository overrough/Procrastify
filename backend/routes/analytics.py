# analytics routesscreen time, focus scores and productivity
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
import sys
sys.path.append('..')
from models.models import (
    log_app_usage, get_app_usage_today, get_daily_stats,
    get_weekly_stats, update_daily_stats, get_app_category,
    get_distraction_apps, create_distraction_alert
)
from utils.auth_utils import token_required
from utils.priority import calculate_focus_score

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/daily', methods=['GET'])
@token_required
# get todayanalytics summary
def get_daily_analytics():
    user_id = request.user_id
    
    # Get daily stats
    stats = get_daily_stats(user_id)
    
    if not stats:
        # Return empty stats for new day
        stats = {
            'date': date.today().isoformat(),
            'total_screen_time': 0,
            'productive_time': 0,
            'distraction_time': 0,
            'focus_score': 0,
            'tasks_completed': 0,
            'focus_sessions_completed': 0
        }
    
    # Calculate focus score with rating
    score, rating, color = calculate_focus_score(
        stats.get('productive_time', 0),
        stats.get('total_screen_time', 0)
    )
    
    # Get top apps
    app_usage = get_app_usage_today(user_id) or []
    top_apps = app_usage[:5] if app_usage else []
    
    # Format times nicely
    def format_minutes(minutes):
        if minutes < 60:
            return f"{minutes}m"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m" if mins else f"{hours}h"
    
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


@analytics_bp.route('/weekly', methods=['GET'])
@token_required
# get weekly analytics breakdown
def get_weekly_analytics():
    user_id = request.user_id
    
    # Get weekly stats
    weekly_data = get_weekly_stats(user_id) or []
    
    if not weekly_data:
        return jsonify({
            'days': [],
            'average_focus_score': 0,
            'total_productive_time': 0,
            'total_distraction_time': 0,
            'best_day': None
        }), 200
    
    # Calculate averages
    total_focus = sum(d.get('focus_score', 0) for d in weekly_data)
    avg_focus = total_focus // len(weekly_data) if weekly_data else 0
    
    total_productive = sum(d.get('productive_time', 0) for d in weekly_data)
    total_distraction = sum(d.get('distraction_time', 0) for d in weekly_data)
    
    # Find best day
    best_day = max(weekly_data, key=lambda x: x.get('focus_score', 0)) if weekly_data else None
    
    # Format dates
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


@analytics_bp.route('/app-usage', methods=['POST'])
@token_required
# log app usage from mobile monitoring
def log_app_usage_endpoint():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    app_name = data.get('app_name', '').strip()
    duration_seconds = data.get('duration_seconds', 0)
    session_id = data.get('session_id')
    
    if not app_name:
        return jsonify({'error': 'App name is required'}), 400
    
    # Get app category
    category = get_app_category(request.user_id, app_name)
    
    # Log usage
    log_app_usage(
        user_id=request.user_id,
        app_name=app_name,
        app_category=category,
        duration_seconds=duration_seconds,
        session_id=session_id
    )
    
    # Update daily stats
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


@analytics_bp.route('/check-distraction', methods=['POST'])
@token_required
# check if current app is a distraction
def check_distraction():
    data = request.get_json()
    
    if not data:
        return jsonify({'should_alert': False}), 200
    
    app_name = data.get('app_name', '')
    time_on_app = data.get('time_on_app', 0)
    session_id = data.get('session_id')
    threshold = data.get('threshold', 300)
    
    # Get distraction apps
    distraction_apps = get_distraction_apps(request.user_id)
    
    # Check if app is distracting and over threshold
    is_distraction = app_name in distraction_apps
    over_threshold = time_on_app >= threshold
    
    if is_distraction and over_threshold:
        # Create alert record
        alert_type = 'critical' if time_on_app > 600 else 'warning'
        message = f"You've spent {time_on_app // 60} minutes on {app_name}. Time to refocus!"
        
        alert_id = create_distraction_alert(
            user_id=request.user_id,
            session_id=session_id,
            app_name=app_name,
            alert_type=alert_type,
            message=message,
            time_on_app=time_on_app
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


@analytics_bp.route('/focus-score', methods=['GET'])
@token_required
# get current focus score with breakdown
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
    
    # Generate personalized message
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
