CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL DEFAULT NULL
);

CREATE TABLE tasks (
    task_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline DATE NOT NULL,
    complexity INT DEFAULT 3,
    category ENUM('Study', 'Personal', 'Work', 'Other') DEFAULT 'Study',
    priority_score FLOAT,
    status ENUM('pending', 'completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE focus_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    task_id INT,
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL DEFAULT NULL,
    duration_minutes INT DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    interruptions INT DEFAULT 0,
    focus_score INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE SET NULL
);

CREATE TABLE app_usage (
    usage_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_id INT,
    app_name VARCHAR(100) NOT NULL,
    app_category ENUM('productive', 'distraction', 'neutral') DEFAULT 'neutral',
    duration_seconds INT DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES focus_sessions(session_id) ON DELETE SET NULL
);

CREATE TABLE daily_stats (
    stat_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    total_screen_time INT DEFAULT 0,
    productive_time INT DEFAULT 0,
    distraction_time INT DEFAULT 0,
    focus_score INT DEFAULT 0,
    tasks_completed INT DEFAULT 0,
    focus_sessions_completed INT DEFAULT 0,
    UNIQUE KEY unique_user_date (user_id, date),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE distraction_alerts (
    alert_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_id INT,
    app_name VARCHAR(100) NOT NULL,
    alert_type ENUM('warning', 'critical', 'info') DEFAULT 'warning',
    message TEXT,
    time_on_app INT DEFAULT 0,
    user_response ENUM('refocus', 'continue', 'break', 'ignored') DEFAULT 'ignored',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES focus_sessions(session_id) ON DELETE SET NULL
);

CREATE TABLE app_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    app_name VARCHAR(100) NOT NULL,
    category ENUM('productive', 'distraction', 'neutral') DEFAULT 'neutral',
    is_custom BOOLEAN DEFAULT FALSE,
    UNIQUE KEY unique_user_app (user_id, app_name),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE streaks (
    streak_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    level VARCHAR(20) DEFAULT 'Starting',
    last_active DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_sessions_user ON focus_sessions(user_id);
CREATE INDEX idx_app_usage_user ON app_usage(user_id);
CREATE INDEX idx_app_usage_timestamp ON app_usage(timestamp);
CREATE INDEX idx_daily_stats_date ON daily_stats(date);
