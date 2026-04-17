# analytics page daily and weekly stats with charts
import streamlit as st
import plotly.graph_objects as go
from utils import get_daily_analytics, get_weekly_analytics, get_session_stats, require_auth, setup_sidebar

st.set_page_config(page_title="Analytics | Procrastify", page_icon="📈", layout="wide")
require_auth()
setup_sidebar()

# Block navigation if focus session is active
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
    padding: 1rem;
    text-align: center;
}
.stat-card .value { font-size: 1.75rem; font-weight: 700; color: #2dd4bf; }
.stat-card .label { font-size: 0.8rem; color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h2>📈 Analytics</h2>
    <p>Track your productivity and focus patterns</p>
</div>
""", unsafe_allow_html=True)

# Today's Stats
st.subheader("📅 Today's Summary")

focus_score = 0
productive = 0
distraction = 0
tasks_done = 0
sessions_done = 0

try:
    d, _ = get_daily_analytics()
    if isinstance(d, dict):
        stats = d.get("stats", d)
        focus_score = stats.get("focus_score", 0) or 0
        productive = stats.get("productive_time", 0) or 0
        distraction = stats.get("distraction_time", 0) or 0
        tasks_done = stats.get("tasks_completed", 0) or 0
        sessions_done = stats.get("focus_sessions_completed", 0) or 0
except Exception:
    st.warning("Could not load daily stats.")

c1, c2, c3, c4 = st.columns(4)
with c1:
    color = "#22c55e" if focus_score >= 70 else "#f59e0b" if focus_score >= 40 else "#ef4444"
    st.markdown(f'<div class="stat-card"><div class="value" style="color:{color}">{focus_score}%</div><div class="label">Focus Score</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="value">{productive}m</div><div class="label">Productive</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="value">{distraction}m</div><div class="label">Distraction</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card"><div class="value">{sessions_done}</div><div class="label">Sessions</div></div>', unsafe_allow_html=True)

# Time Breakdown Chart
st.markdown("---")
st.subheader("⏰ Time Breakdown")

total_time = productive + distraction
if total_time > 0:
    fig = go.Figure(data=[go.Pie(
        labels=["Productive", "Distraction"],
        values=[productive, distraction],
        marker=dict(colors=["#2dd4bf", "#ef4444"]),
        hole=0.5,
        textinfo="label+percent"
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No time data yet — complete a focus session to see your breakdown!")

# Weekly Trend
st.markdown("---")
st.subheader("📊 Weekly Focus Trend")

try:
    w, _ = get_weekly_analytics()
    weekly = w.get("days", []) if isinstance(w, dict) else []
    
    if weekly:
        dates = [d.get("date", "?")[:10] for d in weekly]
        scores = [d.get("focus_score", 0) or 0 for d in weekly]
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=dates, y=scores,
            mode="lines+markers",
            name="Focus Score",
            line=dict(color="#2dd4bf", width=2),
            marker=dict(size=8)
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            yaxis=dict(title="Score %", range=[0, 100]),
            xaxis=dict(title="Date")
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Weekly summary
        total_prod = sum(d.get("productive_time", 0) or 0 for d in weekly)
        total_dist = sum(d.get("distraction_time", 0) or 0 for d in weekly)
        total_tasks = sum(d.get("tasks_completed", 0) or 0 for d in weekly)
        avg_score = sum(scores) / len(scores) if scores else 0
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Avg Focus Score", f"{avg_score:.0f}%")
        k2.metric("Total Productive", f"{total_prod}m")
        k3.metric("Total Distraction", f"{total_dist}m")
        k4.metric("Tasks Completed", total_tasks)
    else:
        st.info("No weekly data yet — use Procrastify for a few days to see trends!")
except Exception:
    st.info("No weekly data available yet.")

# Session Stats
st.markdown("---")
st.subheader("🏆 Focus Session Stats")

try:
    sd, _ = get_session_stats()
    if isinstance(sd, dict):
        stats = sd.get("stats", sd)
        s1, s2, s3 = st.columns(3)
        s1.metric("Total Sessions", stats.get("total_sessions", 0) or 0)
        s2.metric("Completed", stats.get("completed_sessions", 0) or 0)
        total_s = stats.get("total_sessions", 0) or 0
        comp_s = stats.get("completed_sessions", 0) or 0
        rate = int(comp_s / total_s * 100) if total_s > 0 else 0
        s3.metric("Completion Rate", f"{rate}%")
except Exception:
    st.info("No session stats available yet.")

st.markdown("---")
st.caption("Procrastify — BCA Final Project")
