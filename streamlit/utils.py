"""
Procrastify - Streamlit Utilities
API client, auth helpers
"""
import streamlit as st
import requests

import os
API_BASE = os.environ.get("API_BASE_URL", "http://localhost:5000/api")


class ProcrastifyAPI:
    """HTTP client wrapping the Flask backend API"""

    def __init__(self):
        self.base = API_BASE

    @property
    def _headers(self):
        token = st.session_state.get("token")
        if token:
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    # Auth
    def register(self, name, email, password):
        r = requests.post(f"{self.base}/auth/register",
                          json={"name": name, "email": email, "password": password})
        return r.json(), r.status_code

    def login(self, email, password):
        r = requests.post(f"{self.base}/auth/login",
                          json={"email": email, "password": password})
        return r.json(), r.status_code

    def get_profile(self):
        r = requests.get(f"{self.base}/auth/profile", headers=self._headers)
        return r.json(), r.status_code

    # Tasks
    def get_tasks(self, status="pending"):
        r = requests.get(f"{self.base}/tasks", headers=self._headers,
                         params={"status": status})
        return r.json(), r.status_code

    def create_task(self, title, deadline, complexity, category="Study", description=""):
        r = requests.post(f"{self.base}/tasks", headers=self._headers,
                          json={"title": title, "deadline": deadline,
                                "complexity": complexity, "category": category,
                                "description": description})
        return r.json(), r.status_code

    def complete_task(self, task_id):
        r = requests.patch(f"{self.base}/tasks/{task_id}/complete", headers=self._headers)
        return r.json(), r.status_code

    def delete_task(self, task_id):
        r = requests.delete(f"{self.base}/tasks/{task_id}", headers=self._headers)
        return r.json(), r.status_code

    # Analytics
    def get_daily_analytics(self):
        r = requests.get(f"{self.base}/analytics/daily", headers=self._headers)
        return r.json(), r.status_code

    def get_weekly_analytics(self):
        r = requests.get(f"{self.base}/analytics/weekly", headers=self._headers)
        return r.json(), r.status_code

    def get_focus_score(self):
        r = requests.get(f"{self.base}/analytics/focus-score", headers=self._headers)
        return r.json(), r.status_code

    # Sessions
    def start_session(self, task_id=None, duration=25):
        payload = {"duration": duration}
        if task_id:
            payload["task_id"] = task_id
        r = requests.post(f"{self.base}/sessions/start", headers=self._headers,
                          json=payload)
        return r.json(), r.status_code

    def end_session(self, session_id, completed=True, interruptions=0, focus_score=100):
        r = requests.post(f"{self.base}/sessions/end", headers=self._headers,
                          json={"session_id": session_id, "completed": completed,
                                "interruptions": interruptions, "focus_score": focus_score})
        return r.json(), r.status_code

    def get_session_history(self, limit=10):
        r = requests.get(f"{self.base}/sessions/history", headers=self._headers,
                         params={"limit": limit})
        return r.json(), r.status_code

    def get_streak(self):
        r = requests.get(f"{self.base}/sessions/streak", headers=self._headers)
        return r.json(), r.status_code

    def get_session_stats(self):
        r = requests.get(f"{self.base}/sessions/stats", headers=self._headers)
        return r.json(), r.status_code


# Singleton
api = ProcrastifyAPI()


# Auth Helpers
def require_auth():
    """Redirect to login if not authenticated."""
    if not st.session_state.get("token"):
        st.warning("⚠️ Please login first!")
        st.switch_page("app.py")
        st.stop()


def logout():
    """Clear session and redirect to login."""
    for key in ["token", "user", "user_id"]:
        st.session_state.pop(key, None)
    st.switch_page("app.py")


# Sidebar Branding
def setup_sidebar():
    
    st.markdown("""
    <style>
    /* Hide all elements with the specific data-testid */
    [data-testid="stSidebarNav"] span:first-child {
        display: none !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Add branded header in sidebar
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


# Formatters
def fmt_minutes(minutes):
    
    if not minutes or minutes <= 0:
        return "0m"
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m}m" if h else f"{m}m"


URGENCY_COLORS = {
    "overdue":    "#FF0000",
    "high":       "#FF4444",
    "medium":     "#FFB347",
    "low":        "#77DD77",
    "relaxed":    "#90EE90",
    "completed":  "#4CAF50",
}
