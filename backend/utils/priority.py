# priority algorithm - calculates task urgency
from datetime import datetime, date


# calculate priority score (lower = more urgent)
def calculate_priority(deadline, complexity):
    # Convert string to date if needed
    if isinstance(deadline, str):
        deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
    elif isinstance(deadline, datetime):
        deadline = deadline.date()
    
    # Calculate days remaining
    today = date.today()
    days_remaining = (deadline - today).days
    
    # Handle overdue tasks (highest priority)
    if days_remaining <= 0:
        return 0  # Overdue = maximum urgency
    
    # Calculate priority score
    priority_score = days_remaining * complexity
    
    return priority_score


# get urgency level and color for display
def get_urgency_level(priority_score, days_remaining):
    if priority_score == 0 or days_remaining <= 0:
        return ('OVERDUE', '#FF0000')  # Red
    elif days_remaining <= 2:
        return ('HIGH', '#FF4444')  # Red-Orange
    elif priority_score <= 10:
        return ('HIGH', '#FF6B35')  # Orange
    elif priority_score <= 20:
        return ('MEDIUM', '#FFB347')  # Light Orange
    elif priority_score <= 35:
        return ('LOW', '#77DD77')  # Light Green
    else:
        return ('RELAXED', '#90EE90')  # Green


# calculate focus score from productive vs total time
def calculate_focus_score(productive_time, total_time):
    if total_time <= 0:
        return (0, 'N/A', '#CCCCCC')
    
    score = int((productive_time / total_time) * 100)
    
    if score >= 80:
        rating = 'EXCELLENT 🌟'
        color = '#4CAF50'  # Green
    elif score >= 60:
        rating = 'GOOD 👍'
        color = '#8BC34A'  # Light Green
    elif score >= 40:
        rating = 'FAIR ⚠️'
        color = '#FF9800'  # Orange
    else:
        rating = 'POOR ❌'
        color = '#F44336'  # Red
    
    return (score, rating, color)


# get summary of task priorities by urgency level
def get_task_priority_summary(tasks):
    summary = {
        'overdue': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'completed': 0,
        'total': len(tasks)
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
