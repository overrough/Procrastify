import mysql.connector
from mysql.connector import Error
import os

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'procrastify')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

def get_db():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=MYSQL_PORT
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def run_query(query, params=None, fetch=False, fetch_one=False):
    connection = get_db()
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

def create_user(email, password_hash, name):
    query = """
        INSERT INTO users (email, password_hash, name)
        VALUES (%s, %s, %s)
    """
    return run_query(query, (email, password_hash, name))

def get_user_by_email(email):
    query = "SELECT * FROM users WHERE email = %s"
    return run_query(query, (email,), fetch_one=True)

def get_user_by_id(user_id):
    query = "SELECT user_id, email, name, created_at, last_login FROM users WHERE user_id = %s"
    return run_query(query, (user_id,), fetch_one=True)

def update_last_login(user_id):
    query = "UPDATE users SET last_login = NOW() WHERE user_id = %s"
    return run_query(query, (user_id,))

def create_task(user_id, title, deadline, complexity, category, priority_score, description=None):
    query = """
        INSERT INTO tasks (user_id, title, description, deadline, complexity, category, priority_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    return run_query(query, (user_id, title, description, deadline, complexity, category, priority_score))

def get_tasks_by_user(user_id, status=None):
    if status:
        query = """
            SELECT * FROM tasks 
            WHERE user_id = %s AND status = %s 
            ORDER BY priority_score ASC, deadline ASC
        """
        return run_query(query, (user_id, status), fetch=True)
    else:
        query = """
            SELECT * FROM tasks 
            WHERE user_id = %s 
            ORDER BY priority_score ASC, deadline ASC
        """
        return run_query(query, (user_id,), fetch=True)

def get_task_by_id(task_id, user_id):
    query = "SELECT * FROM tasks WHERE task_id = %s AND user_id = %s"
    return run_query(query, (task_id, user_id), fetch_one=True)

def update_task(task_id, user_id, **kwargs):
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
    return run_query(query, tuple(values))

def complete_task(task_id, user_id):
    query = """
        UPDATE tasks 
        SET status = 'completed', completed_at = NOW() 
        WHERE task_id = %s AND user_id = %s
    """
    return run_query(query, (task_id, user_id))

def delete_task(task_id, user_id):
    query = "DELETE FROM tasks WHERE task_id = %s AND user_id = %s"
    return run_query(query, (task_id, user_id))

def create_focus_session(user_id, task_id=None):
    query = """
        INSERT INTO focus_sessions (user_id, task_id, start_time)
        VALUES (%s, %s, NOW())
    """
    return run_query(query, (user_id, task_id))

def end_focus_session(session_id, user_id, completed, interruptions, focus_score):
    query = """
        UPDATE focus_sessions 
        SET end_time = NOW(), 
            duration_minutes = TIMESTAMPDIFF(MINUTE, start_time, NOW()),
            completed = %s,
            interruptions = %s,
            focus_score = %s
        WHERE session_id = %s AND user_id = %s
    """
    return run_query(query, (completed, interruptions, focus_score, session_id, user_id))

def get_user_sessions(user_id, limit=10):
    query = """
        SELECT fs.*, t.title as task_title 
        FROM focus_sessions fs
        LEFT JOIN tasks t ON fs.task_id = t.task_id
        WHERE fs.user_id = %s
        ORDER BY fs.start_time DESC
        LIMIT %s
    """
    return run_query(query, (user_id, limit), fetch=True)

def get_session_streak(user_id):
    query = """
        SELECT COUNT(DISTINCT DATE(start_time)) as streak
        FROM focus_sessions
        WHERE user_id = %s AND completed = TRUE
        AND DATE(start_time) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    """
    return run_query(query, (user_id,), fetch_one=True)

def log_app_usage(user_id, app_name, app_category, duration_seconds, session_id=None):
    query = """
        INSERT INTO app_usage (user_id, session_id, app_name, app_category, duration_seconds)
        VALUES (%s, %s, %s, %s, %s)
    """
    return run_query(query, (user_id, session_id, app_name, app_category, duration_seconds))

def get_app_usage_today(user_id):
    query = """
        SELECT app_name, app_category, SUM(duration_seconds) as total_seconds
        FROM app_usage
        WHERE user_id = %s AND DATE(timestamp) = CURDATE()
        GROUP BY app_name, app_category
        ORDER BY total_seconds DESC
    """
    return run_query(query, (user_id,), fetch=True)

def update_daily_stats(user_id, productive_time=0, distraction_time=0, tasks_completed=0, sessions_completed=0):
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
    return run_query(query, (
        user_id, total_time, productive_time, distraction_time, focus_score, tasks_completed, sessions_completed,
        total_time, productive_time, distraction_time, tasks_completed, sessions_completed
    ))

def get_daily_stats(user_id, date=None):
    if date:
        query = "SELECT * FROM daily_stats WHERE user_id = %s AND date = %s"
        return run_query(query, (user_id, date), fetch_one=True)
    else:
        query = "SELECT * FROM daily_stats WHERE user_id = %s AND date = CURDATE()"
        return run_query(query, (user_id,), fetch_one=True)

def get_weekly_stats(user_id):
    query = """
        SELECT * FROM daily_stats 
        WHERE user_id = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        ORDER BY date DESC
    """
    return run_query(query, (user_id,), fetch=True)

def create_distraction_alert(user_id, session_id, app_name, alert_type, message, time_on_app):
    query = """
        INSERT INTO distraction_alerts (user_id, session_id, app_name, alert_type, message, time_on_app)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    return run_query(query, (user_id, session_id, app_name, alert_type, message, time_on_app))

def update_alert_response(alert_id, response):
    query = "UPDATE distraction_alerts SET user_response = %s WHERE alert_id = %s"
    return run_query(query, (response, alert_id))

def get_app_category(user_id, app_name):
    query = "SELECT category FROM app_categories WHERE user_id = %s AND app_name = %s"
    result = run_query(query, (user_id, app_name), fetch_one=True)
    return result['category'] if result else 'neutral'

def set_app_category(user_id, app_name, category):
    query = """
        INSERT INTO app_categories (user_id, app_name, category, is_custom)
        VALUES (%s, %s, %s, TRUE)
        ON DUPLICATE KEY UPDATE category = %s, is_custom = TRUE
    """
    return run_query(query, (user_id, app_name, category, category))

def get_distraction_apps(user_id):
    query = "SELECT app_name FROM app_categories WHERE user_id = %s AND category = 'distraction'"
    result = run_query(query, (user_id,), fetch=True)
    return [r['app_name'] for r in result] if result else []

def setup_default_categories(user_id):
    default_apps = [
        ('VS Code', 'productive'),
        ('PyCharm', 'productive'),
        ('Google Docs', 'productive'),
        ('Microsoft Word', 'productive'),
        ('Excel', 'productive'),
        ('Google Classroom', 'productive'),
        ('Instagram', 'distraction'),
        ('YouTube', 'distraction'),
        ('TikTok', 'distraction'),
        ('WhatsApp', 'distraction'),
        ('Facebook', 'distraction'),
        ('Twitter', 'distraction'),
        ('Netflix', 'distraction'),
        ('Snapchat', 'distraction'),
    ]
    for app_name, category in default_apps:
        query = """
            INSERT INTO app_categories (user_id, app_name, category, is_custom)
            VALUES (%s, %s, %s, FALSE)
        """
        run_query(query, (user_id, app_name, category))
