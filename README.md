# Procrastify

**A Productivity & Task Management App for Students**

This is our BCA final year project. It helps students manage their tasks, track focus sessions, and stay productive.

🌐 **Live Demo: [https://procrastify-web.onrender.com/](https://procrastify-web.onrender.com/)**

## Features

- **User Login & Registration** — Secure login with JWT tokens
- **Task Management** — Add, edit, complete, delete tasks with categories
- **Priority System** — Tasks are auto-ranked using `Priority = Days / Complexity`
- **Focus Timer (Pomodoro)** — 15-minute focus sessions with break tracking
- **Analytics Dashboard** — See your focus score, daily stats, and progress
- **Screen Time Tracking** — Monitor productive vs distraction time
- **Distraction Alerts** — Get alerts when spending too much time on distracting apps

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend (Web) | Streamlit |
| Backend API | Flask (Python) |
| Database | MySQL |
| Authentication | JWT + bcrypt |
| Deployment | Render.com |

## Project Structure

```
procrastify/
├── backend/
│   ├── app.py
│   ├── database/
│   │   └── schema.sql
│   ├── routes.py
│   ├── database.py
│   └── priority.py
│
├── streamlit/
│   ├── app.py
│   ├── utils.py
│   └── pages/
```

## How to Use

The app is live at **[https://procrastify-web.onrender.com/](https://procrastify-web.onrender.com/)** — just open it in your browser, register an account, and start managing your tasks.

## Local Development (Optional)

To run locally:

1. Start **MySQL** and create a database called `procrastify`
2. Import `backend/database/schema.sql`
3. Run the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```
4. Run the frontend:
   ```bash
   cd streamlit
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Deployment

The app is deployed on Render.com at **https://procrastify-web.onrender.com/**

Set the following environment variable in your **Streamlit** app:

- `BACKEND_URL`: The URL of your deployed Flask backend. **Do not** add `/api` or a trailing slash.

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
Priority Score = Days Until Deadline / Complexity (1-5)
```
Lower score = more urgent. Higher complexity reduces the score, making the task more urgent. Overdue tasks get a score of 0 (highest priority).

## Team

**BCA 6th Semester — Group G39**

- Saksham
- Vivek

---

Made for students who want to stop procrastinating 💪
