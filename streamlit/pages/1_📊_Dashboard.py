# dashboard page overview withfocus score, tasks and stats
import streamlit as st
from utils import get_daily_analytics, get_tasks, get_streak, require_auth, setup_sidebar

st.set_page_config(page_title="Dashboard | Procrastify", page_icon="📊", layout="wide")
require_auth()
setup_sidebar()

# Check if focus session is active redirect back 
if st.session_state.get("focus_active"):
    st.warning("⚠️ You have an active focus session! Go back to the timer to finish it.")
    if st.button("⏱️ Go to Focus Timer"):
        st.switch_page("pages/3_⏱️_Focus_Timer.py")
    st.stop()

# CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stMarkdownContainer"] { caret-color: transparent; }
.page-header {
    background: #162231;
    border: 1px solid #1e3a4f;
    padding: 1.25rem 1.5rem;
    border-radius: 0.75rem;
    margin-bottom: 1.5rem;
}
.page-header h2 { margin: 0; color: #e2e8f0; font-weight: 700; }
.page-header p { margin: 0; color: #94a3b8; font-size: 0.9rem; }
.stat-card {
    background: #162231;
    border: 1px solid #1e3a4f;
    border-radius: 0.75rem;
    padding: 1.25rem;
    text-align: center;
}
.stat-card .value { font-size: 2rem; font-weight: 700; color: #2dd4bf; }
.stat-card .label { font-size: 0.85rem; color: #94a3b8; margin-top: 0.25rem; }
.task-item {
    background: #162231;
    border: 1px solid #1e3a4f;
    border-radius: 0.5rem;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)

#  Header 
user = st.session_state.get("user", {})
name = user.get("name", "Student")

st.markdown(f"""
<div class="page-header">
    <h2>👋 Welcome back, {name}!</h2>
    <p>Here's your productivity snapshot</p>
</div>
""", unsafe_allow_html=True)

#Fetch data 
focus_score = 0
pending = 0
completed_today = 0
streak = 0
productive_min = 0
distraction_min = 0
focus_sessions = 0
top_tasks = []

try:
    # Analytics daily
    d, _ = get_daily_analytics()
    if isinstance(d, dict):
        stats = d.get("stats", d)
        focus_score = stats.get("focus_score", 0) or 0
        productive_min = stats.get("productive_time", 0) or 0
        distraction_min = stats.get("distraction_time", 0) or 0
        completed_today = stats.get("tasks_completed", 0) or 0
        focus_sessions = stats.get("focus_sessions_completed", 0) or 0
except Exception:
    pass

try:
    # Pending tasks
    td, _ = get_tasks("pending")
    tasks_list = td.get("tasks", []) if isinstance(td, dict) else []
    pending = len(tasks_list)
    # Sort by days_remaining (closest deadline first) so urgent tasks show on top
    tasks_list.sort(key=lambda t: t.get("days_remaining", 999))
    top_tasks = tasks_list[:3]
except Exception:
    pass

try:
    # Streak
    sd, _ = get_streak()
    if isinstance(sd, dict):
        streak = sd.get("streak", 0) or 0
except Exception:
    pass

# Stat Cards
c1, c2, c3, c4 = st.columns(4)

with c1:
    color = "#22c55e" if focus_score >= 70 else "#f59e0b" if focus_score >= 40 else "#ef4444"
    st.markdown(f"""
    <div class="stat-card">
        <div class="value" style="color:{color}">{focus_score}%</div>
        <div class="label">Focus Score</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="value">📋 {pending}</div>
        <div class="label">Pending Tasks</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="value">✅ {completed_today}</div>
        <div class="label">Completed Today</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="value">🔥 {streak}</div>
        <div class="label">Day Streak</div>
    </div>""", unsafe_allow_html=True)

# Priority Tasks +Todays Stats
st.markdown("---")
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("🎯 Priority Tasks")
    if top_tasks:
        for t in top_tasks:
            days = t.get("days_remaining", "?")
            days_txt = f"{days}d left" if isinstance(days, int) and days >= 0 else "⚠️ overdue"
            level = t.get("urgency_level", "LOW").upper()
            dot = "🔴" if level in ("OVERDUE", "HIGH") else "🟠" if level == "MEDIUM" else "🟢"
            st.markdown(f"""
            <div class="task-item">
                <div>{dot} <strong>{t.get('title','Untitled')}</strong></div>
                <div style="opacity:0.6;font-size:0.85rem">{t.get('category','—')} · {days_txt}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No pending tasks! 🎉")

with col_right:
    st.subheader("📈 Today's Stats")
    st.markdown(f"🎯 **Productive Time:** {productive_min}m")
    st.markdown(f"📱 **Distraction Time:** {distraction_min}m")
    st.markdown(f"🔥 **Focus Sessions:** {focus_sessions}")

st.markdown("---")
st.caption("Procrastify — BCA Final Project")
