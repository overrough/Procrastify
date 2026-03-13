# task routes - CRUD operations with priority calculation
from flask import Blueprint, request, jsonify
from datetime import datetime, date
import sys
sys.path.append('..')
from models.models import (
    create_task, get_tasks_by_user, get_task_by_id,
    update_task, complete_task, delete_task, update_daily_stats
)
from utils.auth_utils import token_required
from utils.priority import calculate_priority, get_urgency_level, get_task_priority_summary

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('', methods=['GET'])
@token_required
# get all tasks for the current user
def get_all_tasks():
    status = request.args.get('status', 'pending')
    
    if status == 'all':
        tasks = get_tasks_by_user(request.user_id)
    else:
        tasks = get_tasks_by_user(request.user_id, status)
    
    if tasks is None:
        return jsonify({'error': 'Failed to fetch tasks'}), 500
    
    # Add urgency level and color to each task
    today = date.today()
    for task in tasks:
        deadline = task.get('deadline')
        if isinstance(deadline, str):
            deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
        
        days_remaining = (deadline - today).days if deadline else 999
        task['days_remaining'] = days_remaining
        
        # Completed tasks get a COMPLETED badge, not urgency
        if task.get('status') == 'completed':
            task['urgency_level'] = 'COMPLETED'
            task['urgency_color'] = '#4CAF50'
        else:
            # Recalculate priority score dynamically based on current date
            complexity = task.get('complexity', 3)
            priority_score = calculate_priority(deadline, complexity)
            task['priority_score'] = priority_score
            
            level, color = get_urgency_level(priority_score, days_remaining)
            task['urgency_level'] = level
            task['urgency_color'] = color
        
        # Convert datetime objects to strings for JSON
        if task.get('deadline'):
            task['deadline'] = task['deadline'].strftime('%Y-%m-%d') if hasattr(task['deadline'], 'strftime') else str(task['deadline'])
        if task.get('created_at'):
            task['created_at'] = task['created_at'].isoformat() if hasattr(task['created_at'], 'isoformat') else str(task['created_at'])
        if task.get('completed_at'):
            task['completed_at'] = task['completed_at'].isoformat() if hasattr(task['completed_at'], 'isoformat') else str(task['completed_at'])
    
    # Get summary
    summary = get_task_priority_summary(tasks)
    
    return jsonify({
        'tasks': tasks,
        'summary': summary
    }), 200


@tasks_bp.route('', methods=['POST'])
@token_required
# create a new task with priority score
def create_new_task():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    title = data.get('title', '').strip()
    deadline = data.get('deadline', '')
    complexity = data.get('complexity')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    if not deadline:
        return jsonify({'error': 'Deadline is required'}), 400
    
    if not complexity or complexity not in [1, 2, 3, 4, 5]:
        return jsonify({'error': 'Complexity must be between 1-5'}), 400
    
    # Validate deadline format
    try:
        deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Deadline must be in YYYY-MM-DD format'}), 400
    
    # Calculate priority score
    priority_score = calculate_priority(deadline_date, complexity)
    
    # Get optional fields
    category = data.get('category', 'Study')
    description = data.get('description', '')
    
    # Create task
    task_id = create_task(
        user_id=request.user_id,
        title=title,
        deadline=deadline,
        complexity=complexity,
        category=category,
        priority_score=priority_score,
        description=description
    )
    
    if not task_id:
        return jsonify({'error': 'Failed to create task'}), 500
    
    # Get urgency level
    days_remaining = (deadline_date - date.today()).days
    level, color = get_urgency_level(priority_score, days_remaining)
    
    return jsonify({
        'message': 'Task created successfully',
        'task': {
            'task_id': task_id,
            'title': title,
            'deadline': deadline,
            'complexity': complexity,
            'category': category,
            'priority_score': priority_score,
            'urgency_level': level,
            'urgency_color': color,
            'days_remaining': days_remaining,
            'status': 'pending'
        }
    }), 201


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@token_required
# get a single task by its id
def get_single_task(task_id):
    task = get_task_by_id(task_id, request.user_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Add urgency info
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


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@token_required
# update an existing task
def update_existing_task(task_id):
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Check task exists
    existing_task = get_task_by_id(task_id, request.user_id)
    if not existing_task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Prepare update data
    update_data = {}
    
    if 'title' in data:
        update_data['title'] = data['title'].strip()
    
    if 'description' in data:
        update_data['description'] = data['description']
    
    if 'category' in data:
        update_data['category'] = data['category']
    
    # Recalculate priority if deadline or complexity changed
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
    
    # Recalculate priority
    if 'deadline' in data or 'complexity' in data:
        priority_score = calculate_priority(deadline, complexity)
        update_data['priority_score'] = priority_score
    
    # Update task
    result = update_task(task_id, request.user_id, **update_data)
    
    if result is None:
        return jsonify({'error': 'Failed to update task'}), 500
    
    return jsonify({'message': 'Task updated successfully'}), 200


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@token_required
# delete a task by id
def delete_existing_task(task_id):
    existing_task = get_task_by_id(task_id, request.user_id)
    if not existing_task:
        return jsonify({'error': 'Task not found'}), 404
    
    result = delete_task(task_id, request.user_id)
    
    if result is None:
        return jsonify({'error': 'Failed to delete task'}), 500
    
    return jsonify({'message': 'Task deleted successfully'}), 200


@tasks_bp.route('/<int:task_id>/complete', methods=['PATCH'])
@token_required
# mark a task as completed
def mark_task_complete(task_id):
    existing_task = get_task_by_id(task_id, request.user_id)
    if not existing_task:
        return jsonify({'error': 'Task not found'}), 404
    
    if existing_task.get('status') == 'completed':
        return jsonify({'message': 'Task is already completed'}), 200
    
    result = complete_task(task_id, request.user_id)
    
    if result is None:
        return jsonify({'error': 'Failed to complete task'}), 500
    
    # Update daily stats counter
    update_daily_stats(user_id=request.user_id, tasks_completed=1)
    
    return jsonify({'message': 'Task marked as completed! 🎉'}), 200
