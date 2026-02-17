# Procrastify

**A Productivity & Task Management App for Students**

This is our BCA final year project. It helps students manage their tasks, track focus sessions, and stay productive.

## Features

- **User Login & Registration** — Secure login with JWT tokens
- **Task Management** — Add, edit, complete, delete tasks with categories
- **Priority System** — Tasks are auto-ranked using `Priority = Days × Complexity`
- **Focus Timer (Pomodoro)** — 25-minute focus sessions with break tracking
- **Analytics Dashboard** — See your focus score, daily stats, and progress
- **Screen Time Tracking** — Monitor productive vs distraction time
- **Distraction Alerts** — Get alerts when spending too much time on distracting apps

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend (Web) | Streamlit |
| Backend API | Flask (Python) |
| Database | MySQL (via XAMPP) |
| Authentication | JWT + bcrypt |

## Project Structure

```
procrastify/
├── backend/                 # Flask API Server
│   ├── app.py               # Main app
│   ├── config.py            # Config settings
│   ├── database/
│   │   └── schema.sql       # MySQL tables
│   ├── routes/              # API routes
│   ├── models/              # Database models
│   └── utils/               # Helper functions
│
├── streamlit/               # Streamlit Web App
│   ├── app.py               # Login/Register page
│   ├── utils.py             # API client & helpers
│   └── pages/               # Dashboard, Tasks, Timer, Analytics, Settings
│
└── mobile/                  # Kivy Mobile App (experimental)
    ├── main.py              # Entry point
    ├── screens/             # All app screens
    └── services/            # API communication
```

## How to Run

### 1. Database Setup

1. Open XAMPP and start **Apache** + **MySQL**
2. Go to `http://localhost/phpmyadmin`
3. Create a new database called `procrastify`
4. Import `backend/database/schema.sql` into it

### 2. Start Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server starts at `http://localhost:5000`

### 3. Start Streamlit App

```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

App opens at `http://localhost:8501`

## API Endpoints

### Auth
- `POST /api/auth/register` — Register
- `POST /api/auth/login` — Login
- `GET /api/auth/profile` — Get profile

### Tasks
- `GET /api/tasks` — Get tasks
- `POST /api/tasks` — Create task
- `DELETE /api/tasks/<id>` — Delete task
- `PATCH /api/tasks/<id>/complete` — Mark complete

### Analytics
- `GET /api/analytics/daily` — Today's stats
- `GET /api/analytics/weekly` — Weekly summary

### Focus Sessions
- `POST /api/sessions/start` — Start timer
- `POST /api/sessions/end` — End session
- `GET /api/sessions/streak` — Get streak

## How Priority Works

```
Priority Score = Days Until Deadline × Complexity (1-5)
```
Lower score = more urgent. Overdue tasks get a score of 0 (highest priority).

## Team

**BCA 6th Semester — Group G39**

- Saksham
- Vivek

---

Made for students who want to stop procrastinating 💪
