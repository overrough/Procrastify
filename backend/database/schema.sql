-- Procrastify v2.0 Database Schema
-- Run this in phpMyAdmin or MySQL Workbench

CREATE DATABASE IF NOT EXISTS procrastify;
USE procrastify;

-- Table 1: USERS - User authentication and profile
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL
);

-- Table 2: TASKS - Task information with priority
CREATE TABLE tasks (
    task_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline DATE NOT NULL,
    complexity INT CHECK (complexity BETWEEN 1 AND 5),
    category ENUM('Study', 'Personal', 'Work', 'Other') DEFAULT 'Study',
    priority_score INT,
    status ENUM('pending', 'completed') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Table 3: FOCUS_SESSIONS - Pomodoro session tracking
CREATE TABLE focus_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    task_id INT,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_minutes INT DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    interruptions INT DEFAULT 0,
    focus_score INT CHECK (focus_score BETWEEN 0 AND 100),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE SET NULL
);

-- Table 4: APP_USAGE - Granular app monitoring logs
CREATE TABLE app_usage (
    usage_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_id INT,
    app_name VARCHAR(100) NOT NULL,
    app_category ENUM('productive', 'distraction', 'neutral') DEFAULT 'neutral',
    duration_seconds INT DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES focus_sessions(session_id) ON DELETE SET NULL
);

-- Table 5: DAILY_STATS - Aggregated daily metrics
CREATE TABLE daily_stats (
    stat_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    total_screen_time INT DEFAULT 0,  -- in minutes
    productive_time INT DEFAULT 0,     -- in minutes
    distraction_time INT DEFAULT 0,    -- in minutes
    focus_score INT CHECK (focus_score BETWEEN 0 AND 100),
    tasks_completed INT DEFAULT 0,
    focus_sessions_completed INT DEFAULT 0,
    UNIQUE KEY unique_user_date (user_id, date),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Table 6: DISTRACTION_ALERTS - Alert history
CREATE TABLE distraction_alerts (
    alert_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_id INT,
    app_name VARCHAR(100) NOT NULL,
    alert_type ENUM('warning', 'critical', 'info') DEFAULT 'warning',
    message TEXT,
    time_on_app INT DEFAULT 0,  -- in seconds
    user_response ENUM('refocus', 'continue', 'break', 'ignored') DEFAULT 'ignored',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES focus_sessions(session_id) ON DELETE SET NULL
);

-- Table 7: APP_CATEGORIES - User-defined app classifications
CREATE TABLE app_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    app_name VARCHAR(100) NOT NULL,
    category ENUM('productive', 'distraction', 'neutral') DEFAULT 'neutral',
    is_custom BOOLEAN DEFAULT FALSE,
    UNIQUE KEY unique_user_app (user_id, app_name),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Insert default app categories (global defaults)
INSERT INTO app_categories (user_id, app_name, category, is_custom) VALUES
(1, 'VS Code', 'productive', FALSE),
(1, 'PyCharm', 'productive', FALSE),
(1, 'Google Docs', 'productive', FALSE),
(1, 'Microsoft Word', 'productive', FALSE),
(1, 'Excel', 'productive', FALSE),
(1, 'Google Classroom', 'productive', FALSE),
(1, 'Instagram', 'distraction', FALSE),
(1, 'YouTube', 'distraction', FALSE),
(1, 'TikTok', 'distraction', FALSE),
(1, 'WhatsApp', 'distraction', FALSE),
(1, 'Facebook', 'distraction', FALSE),
(1, 'Twitter', 'distraction', FALSE),
(1, 'Netflix', 'distraction', FALSE),
(1, 'Snapchat', 'distraction', FALSE);

-- Create indexes for performance
CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_sessions_user ON focus_sessions(user_id);
CREATE INDEX idx_app_usage_user ON app_usage(user_id);
CREATE INDEX idx_app_usage_timestamp ON app_usage(timestamp);
CREATE INDEX idx_daily_stats_date ON daily_stats(date);
