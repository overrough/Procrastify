# 🎯 Procrastify v2.0

**Mobile Productivity & Distraction Management System**

A comprehensive mobile app combining intelligent task prioritization with real-time phone usage monitoring for students.

## 🚀 Features

### Core Features
1. **User Authentication** - Secure registration & login with JWT tokens
2. **Task Management** - Create, edit, complete, delete tasks with categories
3. **Intelligent Priority Algorithm** - Auto-ranking: `Priority = Days × Complexity`

### Intelligence Features
4. **Screen Time Tracking** - Monitor app usage across your device
5. **Smart Distraction Alerts** - Get notified when spending too much time on distracting apps
6. **Real-Time Analytics Dashboard** - Focus score, time breakdown, top apps
7. **Task Progress Tracker** - Completion percentages and trends

### Advanced Features
8. **Focus Sessions (Pomodoro)** - 25-min focus timer with breaks
9. **Advanced Analytics** - Weekly/monthly trends and charts
10. **Notifications & Settings** - Customizable themes and preferences

## 📁 Project Structure

```
procrastify/
├── backend/                 # Flask API Server
│   ├── app.py               # Main Flask application
│   ├── config.py            # Configuration
│   ├── requirements.txt     # Dependencies
│   ├── database/
│   │   └── schema.sql       # MySQL tables
│   ├── routes/
│   │   ├── auth.py          # Auth endpoints
│   │   ├── tasks.py         # Task endpoints
│   │   ├── analytics.py     # Analytics endpoints
│   │   └── sessions.py      # Focus session endpoints
│   ├── models/
│   │   └── models.py        # Database models
│   └── utils/
│       ├── auth_utils.py    # JWT & password utilities
│       └── priority.py      # Priority algorithm
│
└── mobile/                  # Kivy Mobile App
    ├── main.py              # App entry point
    ├── requirements.txt     # Dependencies
    ├── screens/
    │   ├── login.py         # Login screen
    │   ├── register.py      # Registration screen
    │   ├── home.py          # Dashboard
    │   ├── tasks.py         # Task management
    │   ├── analytics.py     # Analytics dashboard
    │   ├── focus.py         # Pomodoro timer
    │   └── settings.py      # Settings
    ├── components/
    │   └── alert_popup.py   # Distraction alert
    └── services/
        └── api_client.py    # API communication
```

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| Mobile UI | Kivy 2.3+ / KivyMD (Material Design) |
| Backend API | Flask 3.0+ |
| Database | MySQL 8.0+ (via XAMPP) |
| Auth | JWT + bcrypt |

## 📦 Setup Instructions

### 1. Database Setup (XAMPP)

1. Start XAMPP Control Panel
2. Start **Apache** and **MySQL** services
3. Open **phpMyAdmin**: `http://localhost/phpmyadmin`
4. Create database: Click "New" → Enter `procrastify` → Click "Create"
5. Import schema: Select `procrastify` database → Click "Import" → Choose `backend/database/schema.sql` → Click "Go"

### 2. Backend Setup

```bash
# Navigate to backend
cd procrastify/backend

# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

Server runs at: `http://localhost:5000`

### 3. Mobile App Setup

```bash
# Navigate to mobile app
cd procrastify/mobile

# Install dependencies
pip install -r requirements.txt

# Run app (desktop testing)
python main.py
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get profile (protected)

### Tasks
- `GET /api/tasks` - Get all tasks (sorted by priority)
- `POST /api/tasks` - Create task
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task
- `PATCH /api/tasks/<id>/complete` - Mark complete

### Analytics
- `GET /api/analytics/daily` - Today's stats
- `GET /api/analytics/weekly` - Week summary
- `POST /api/analytics/app-usage` - Log app usage
- `GET /api/analytics/focus-score` - Get focus score

### Focus Sessions
- `POST /api/sessions/start` - Start Pomodoro
- `POST /api/sessions/end` - End session
- `GET /api/sessions/streak` - Get streak

## 🧮 Key Algorithms

### Priority Calculation
```python
Priority = Days_Until_Deadline × Complexity
# Lower score = Higher urgency
```

### Focus Score
```python
Focus_Score = (Productive_Time / Total_Time) × 100
# 80-100% = Excellent, 60-79% = Good, 40-59% = Fair, 0-39% = Poor
```

## 📱 Building for Android

```bash
# Install buildozer
pip install buildozer

# Initialize (first time only)
buildozer init

# Build APK
buildozer android debug
```

## 👥 Team

**BCA 6th Semester Major Project - Group G39**

---

Made with ❤️ for students who want to beat procrastination!
