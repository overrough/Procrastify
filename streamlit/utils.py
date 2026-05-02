import streamlit as st
import requests
import os

API_BASE = os.environ.get("BACKEND_URL", "http://localhost:5000") + "/api"

def get_headers():
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return {"Content-Type": "application/json"}

def login(email, password):
    r = requests.post(f"{API_BASE}/auth/login", json={"email": email, "password": password})
    return r.json(), r.status_code

def register(name, email, password):
    r = requests.post(f"{API_BASE}/auth/register", json={"name": name, "email": email, "password": password})
    return r.json(), r.status_code

def get_profile():
    r = requests.get(f"{API_BASE}/auth/profile", headers=get_headers())
    return r.json(), r.status_code

def get_tasks(status="pending"):
    r = requests.get(f"{API_BASE}/tasks", headers=get_headers(), params={"status": status})
    return r.json(), r.status_code

def create_task(title, deadline, complexity, category="Study", description=""):
    r = requests.post(f"{API_BASE}/tasks", headers=get_headers(),
                      json={"title": title, "deadline": deadline, "complexity": complexity,
                            "category": category, "description": description})
    return r.json(), r.status_code

def complete_task(task_id):
    r = requests.patch(f"{API_BASE}/tasks/{task_id}/complete", headers=get_headers())
    return r.json(), r.status_code

def delete_task(task_id):
    r = requests.delete(f"{API_BASE}/tasks/{task_id}", headers=get_headers())
    return r.json(), r.status_code

def get_daily_analytics():
    r = requests.get(f"{API_BASE}/analytics/daily", headers=get_headers())
    return r.json(), r.status_code

def get_weekly_analytics():
    r = requests.get(f"{API_BASE}/analytics/weekly", headers=get_headers())
    return r.json(), r.status_code

def get_focus_score():
    r = requests.get(f"{API_BASE}/analytics/focus-score", headers=get_headers())
    return r.json(), r.status_code

def start_session(task_id=None, duration=25):
    payload = {"duration": duration}
    if task_id:
        payload["task_id"] = task_id
    r = requests.post(f"{API_BASE}/sessions/start", headers=get_headers(), json=payload)
    return r.json(), r.status_code

def end_session(session_id, completed=True, interruptions=0, focus_score=100):
    r = requests.post(f"{API_BASE}/sessions/end", headers=get_headers(),
                      json={"session_id": session_id, "completed": completed,
                            "interruptions": interruptions, "focus_score": focus_score})
    return r.json(), r.status_code

def get_session_history(limit=10):
    r = requests.get(f"{API_BASE}/sessions/history", headers=get_headers(), params={"limit": limit})
    return r.json(), r.status_code

def get_streak():
    r = requests.get(f"{API_BASE}/sessions/streak", headers=get_headers())
    return r.json(), r.status_code

def get_session_stats():
    r = requests.get(f"{API_BASE}/sessions/stats", headers=get_headers())
    return r.json(), r.status_code

def require_auth():
    if not st.session_state.get("token"):
        st.warning("Please login first!")
        st.switch_page("app.py")
        st.stop()

def logout():
    for key in ["token", "user", "user_id"]:
        st.session_state.pop(key, None)
    st.switch_page("app.py")

def setup_sidebar():
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] span:first-child {
        display: none !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0.5rem 0.75rem; margin-bottom: 0.25rem; border-bottom: 1px solid #1e3a4f;">
        <div style="font-size: 1.5rem; font-weight: 700; color: #2dd4bf;">
            🚀 Procrastify
        </div>
        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem;">
            Beat Procrastination
        </div>
    </div>
    """, unsafe_allow_html=True)

def fmt_minutes(minutes):
    if not minutes or minutes <= 0:
        return "0m"
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m}m" if h else f"{m}m"

URGENCY_COLORS = {
    "overdue":    "#FF0000",
    "high":       "#FF4D4D",
    "medium":     "#FFA500",
    "low":        "#FFFF00",
    "relaxed":    "#00FF00",
    "completed":  "#4CAF50",
}
