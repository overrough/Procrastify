"""
Database Models and Connection for Procrastify
"""
import mysql.connector
from mysql.connector import Error
from config import current_config


def get_db_connection():
    """Create and return a MySQL database connection"""
    try:
        connection = mysql.connector.connect(
            host=current_config.MYSQL_HOST,
            user=current_config.MYSQL_USER,
            password=current_config.MYSQL_PASSWORD,
            database=current_config.MYSQL_DATABASE,
            port=current_config.MYSQL_PORT
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def execute_query(query, params=None, fetch=False, fetch_one=False):
    """Execute a MySQL query with proper connection handling"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.lastrowid
        
        cursor.close()
        connection.close()
        return result
    except Error as e:
        print(f"Database error: {e}")
        return None


# User Model Functions
def create_user(email, password_hash, name):
    """Create a new user"""
    query = """
        INSERT INTO users (email, password_hash, name)
        VALUES (%s, %s, %s)
    """
    return execute_query(query, (email, password_hash, name))


def get_user_by_email(email):
    """Get user by email"""
    query = "SELECT * FROM users WHERE email = %s"
    return execute_query(query, (email,), fetch_one=True)


def get_user_by_id(user_id):
    """Get user by ID"""
    query = "SELECT user_id, email, name, created_at, last_login FROM users WHERE user_id = %s"
    return execute_query(query, (user_id,), fetch_one=True)


def update_last_login(user_id):
    """Update user's last login timestamp"""
    query = "UPDATE users SET last_login = NOW() WHERE user_id = %s"
    return execute_query(query, (user_id,))


# Task Model Functions
def create_task(user_id, title, deadline, complexity, category, priority_score, description=None):
    """Create a new task"""
    query = """
        INSERT INTO tasks (user_id, title, description, deadline, complexity, category, priority_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(query, (user_id, title, description, deadline, complexity, category, priority_score))


def get_tasks_by_user(user_id, status=None):
    """Get all tasks for a user, sorted by priority"""
    if status:
        query = """
            SELECT * FROM tasks 
            WHERE user_id = %s AND status = %s 
            ORDER BY priority_score ASC, deadline ASC
        """
        return execute_query(query, (user_id, status), fetch=True)
    else:
        query = """
            SELECT * FROM tasks 
            WHERE user_id = %s 
            ORDER BY priority_score ASC, deadline ASC
        """
        return execute_query(query, (user_id,), fetch=True)


def get_task_by_id(task_id, user_id):
    """Get a specific task"""
    query = "SELECT * FROM tasks WHERE task_id = %s AND user_id = %s"
    return execute_query(query, (task_id, user_id), fetch_one=True)


def update_task(task_id, user_id, **kwargs):
    """Update a task"""
    allowed_fields = ['title', 'description', 'deadline', 'complexity', 'category', 'priority_score', 'status']
    updates = []
    values = []
    
    for field, value in kwargs.items():
        if field in allowed_fields and value is not None:
            updates.append(f"{field} = %s")
            values.append(value)
    
    if not updates:
        return False
    
    values.extend([task_id, user_id])
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = %s AND user_id = %s"
    return execute_query(query, tuple(values))


def complete_task(task_id, user_id):
    """Mark a task as completed"""
    query = """
        UPDATE tasks 
        SET status = 'completed', completed_at = NOW() 
        WHERE task_id = %s AND user_id = %s
    """
    return execute_query(query, (task_id, user_id))


def delete_task(task_id, user_id):
    """Delete a task"""
    query = "DELETE FROM tasks WHERE task_id = %s AND user_id = %s"
    return execute_query(query, (task_id, user_id))


# Focus Session Model Functions
def create_focus_session(user_id, task_id=None):
    """Start a new focus session"""
    query = """
        INSERT INTO focus_sessions (user_id, task_id, start_time)
        VALUES (%s, %s, NOW())
    """
    return execute_query(query, (user_id, task_id))


def end_focus_session(session_id, user_id, completed, interruptions, focus_score):
    """End a focus session"""
    query = """
        UPDATE focus_sessions 
        SET end_time = NOW(), 
            duration_minutes = TIMESTAMPDIFF(MINUTE, start_time, NOW()),
            completed = %s,
            interruptions = %s,
            focus_score = %s
        WHERE session_id = %s AND user_id = %s
    """
    return execute_query(query, (completed, interruptions, focus_score, session_id, user_id))


def get_user_sessions(user_id, limit=10):
    """Get recent focus sessions for a user"""
    query = """
        SELECT fs.*, t.title as task_title 
        FROM focus_sessions fs
        LEFT JOIN tasks t ON fs.task_id = t.task_id
        WHERE fs.user_id = %s
        ORDER BY fs.start_time DESC
        LIMIT %s
    """
    return execute_query(query, (user_id, limit), fetch=True)


def get_session_streak(user_id):
    """Get consecutive days with completed sessions"""
    query = """
        SELECT COUNT(DISTINCT DATE(start_time)) as streak
        FROM focus_sessions
        WHERE user_id = %s AND completed = TRUE
        AND DATE(start_time) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    """
    return execute_query(query, (user_id,), fetch_one=True)


# App Usage Model Functions
def log_app_usage(user_id, app_name, app_category, duration_seconds, session_id=None):
    """Log app usage"""
    query = """
        INSERT INTO app_usage (user_id, session_id, app_name, app_category, duration_seconds)
        VALUES (%s, %s, %s, %s, %s)
    """
    return execute_query(query, (user_id, session_id, app_name, app_category, duration_seconds))


def get_app_usage_today(user_id):
    """Get today's app usage"""
    query = """
        SELECT app_name, app_category, SUM(duration_seconds) as total_seconds
        FROM app_usage
        WHERE user_id = %s AND DATE(timestamp) = CURDATE()
        GROUP BY app_name, app_category
        ORDER BY total_seconds DESC
    """
    return execute_query(query, (user_id,), fetch=True)


# Daily Stats Model Functions
def update_daily_stats(user_id, productive_time=0, distraction_time=0, tasks_completed=0, sessions_completed=0):
    """Update or create daily stats"""
    query = """
        INSERT INTO daily_stats (user_id, date, total_screen_time, productive_time, distraction_time, 
                                 focus_score, tasks_completed, focus_sessions_completed)
        VALUES (%s, CURDATE(), %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_screen_time = total_screen_time + %s,
            productive_time = productive_time + %s,
            distraction_time = distraction_time + %s,
            tasks_completed = tasks_completed + %s,
            focus_sessions_completed = focus_sessions_completed + %s
    """
    total_time = productive_time + distraction_time
    focus_score = int((productive_time / total_time * 100)) if total_time > 0 else 0
    
    return execute_query(query, (
        user_id, total_time, productive_time, distraction_time, focus_score, tasks_completed, sessions_completed,
        total_time, productive_time, distraction_time, tasks_completed, sessions_completed
    ))


def get_daily_stats(user_id, date=None):
    """Get daily stats"""
    if date:
        query = "SELECT * FROM daily_stats WHERE user_id = %s AND date = %s"
        return execute_query(query, (user_id, date), fetch_one=True)
    else:
        query = "SELECT * FROM daily_stats WHERE user_id = %s AND date = CURDATE()"
        return execute_query(query, (user_id,), fetch_one=True)


def get_weekly_stats(user_id):
    """Get stats for the last 7 days"""
    query = """
        SELECT * FROM daily_stats 
        WHERE user_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        ORDER BY date DESC
    """
    return execute_query(query, (user_id,), fetch=True)


# Distraction Alert Model Functions
def create_distraction_alert(user_id, session_id, app_name, alert_type, message, time_on_app):
    """Log a distraction alert"""
    query = """
        INSERT INTO distraction_alerts (user_id, session_id, app_name, alert_type, message, time_on_app)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    return execute_query(query, (user_id, session_id, app_name, alert_type, message, time_on_app))


def update_alert_response(alert_id, response):
    """Update user's response to alert"""
    query = "UPDATE distraction_alerts SET user_response = %s WHERE alert_id = %s"
    return execute_query(query, (response, alert_id))


# App Categories Model Functions
def get_app_category(user_id, app_name):
    """Get category for an app"""
    query = "SELECT category FROM app_categories WHERE user_id = %s AND app_name = %s"
    result = execute_query(query, (user_id, app_name), fetch_one=True)
    return result['category'] if result else 'neutral'


def set_app_category(user_id, app_name, category):
    """Set or update category for an app"""
    query = """
        INSERT INTO app_categories (user_id, app_name, category, is_custom)
        VALUES (%s, %s, %s, TRUE)
        ON DUPLICATE KEY UPDATE category = %s, is_custom = TRUE
    """
    return execute_query(query, (user_id, app_name, category, category))


def get_distraction_apps(user_id):
    """Get list of distraction apps"""
    query = "SELECT app_name FROM app_categories WHERE user_id = %s AND category = 'distraction'"
    result = execute_query(query, (user_id,), fetch=True)
    return [r['app_name'] for r in result] if result else []
