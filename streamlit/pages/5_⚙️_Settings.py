# settings page profile, preferences and logout
import streamlit as st
from utils import api, require_auth, logout, setup_sidebar

st.set_page_config(page_title="Settings | Procrastify", page_icon="⚙️", layout="centered")
require_auth()
setup_sidebar()

# Block navigation if focus session is active
if st.session_state.get("focus_active"):
    st.warning("⚠️ You have an active focus session! Go back to the timer to finish it.")
    if st.button("⏱️ Go to Focus Timer"):
        st.switch_page("pages/3_⏱️_Focus_Timer.py")
    st.stop()

# ── CSS ─────────────────────────────────────────────────
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
.info-card {
    background: #162231;
    border: 1px solid #1e3a4f;
    border-radius: 0.75rem;
    padding: 1.25rem;
    margin-bottom: 1rem;
    color: #94a3b8;
}
.info-card strong { color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h2>⚙️ Settings</h2>
    <p>Manage your profile and preferences</p>
</div>
""", unsafe_allow_html=True)

# ── Profile ─────────────────────────────────────────────
st.subheader("👤 Profile")
user = st.session_state.get("user", {})

st.markdown(f"""
<div class="info-card">
    <strong>Name:</strong> {user.get("name", "N/A")}<br>
    <strong>Email:</strong> {user.get("email", "N/A")}<br>
    <strong>Member since:</strong> {str(user.get("created_at", "N/A"))[:10]}
</div>
""", unsafe_allow_html=True)

# ── Preferences ─────────────────────────────────────────
st.markdown("---")
st.subheader("🎨 Preferences")

col1, col2 = st.columns(2)

with col1:
    theme = st.selectbox("Theme", ["Dark", "Light"], index=0,
                        help="Use Streamlit Settings (top-right menu) to change theme")

with col2:
    default_dur = st.selectbox("Default Pomodoro Duration",
                               [15, 25, 45, 60],
                               index=1,
                               format_func=lambda x: f"{x} minutes")
    if default_dur != st.session_state.get("timer_duration", 25):
        st.session_state.timer_duration = default_dur
        st.success(f"Default duration set to {default_dur} minutes")

# ── Logout ──────────────────────────────────────────────
st.markdown("---")
st.subheader("🚪 Account")

if st.button("Logout", type="primary", use_container_width=True):
    logout()

# ── About ───────────────────────────────────────────────
st.markdown("---")
st.subheader("ℹ️ About")

st.markdown("""
<div class="info-card">
    <strong>Procrastify</strong><br>
    A productivity app for students to manage tasks, track focus sessions, 
    and beat procrastination.<br><br>
    <strong>Built with:</strong> Python, Streamlit, Flask, MySQL<br>
    <strong>Project:</strong> BCA Final Year Project
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Procrastify — BCA Final Project")
