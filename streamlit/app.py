"""
Procrastify — Streamlit Web App
Main entry point: Login / Register
"""
import streamlit as st
import requests
from utils import api

# ── Page config ─────────────────────────────────────────
st.set_page_config(
    page_title="Procrastify",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero-header {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    padding: 2.5rem 2rem;
    border-radius: 1rem;
    text-align: center;
    margin-bottom: 2rem;
}
.hero-header h1 {
    color: white;
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
}
.hero-header .tagline {
    color: rgba(255,255,255,0.8);
    font-size: 1rem;
    margin-top: 0.5rem;
}
.feature-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 1.25rem;
}
.pill {
    background: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.9);
    padding: 0.4rem 0.9rem;
    border-radius: 2rem;
    font-size: 0.8rem;
    font-weight: 600;
}
.success-banner {
    background: #059669;
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 1rem;
}
.error-banner {
    background: #dc2626;
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 1rem;
}
[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Already logged in? Redirect ────────────────────────
if st.session_state.get("token"):
    st.switch_page("pages/1_📊_Dashboard.py")

# ── Hero Header ─────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🚀 Procrastify</h1>
    <p class="tagline">Beat procrastination. Own your productivity.</p>
    <div class="feature-pills">
        <span class="pill">📋 Smart Tasks</span>
        <span class="pill">⏱️ Pomodoro</span>
        <span class="pill">📊 Analytics</span>
        <span class="pill">🎯 Focus Score</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Auth Tabs ───────────────────────────────────────────
login_tab, register_tab = st.tabs(["🔑  Login", "✨  Create Account"])

# ── Login ───────────────────────────────────────────────
with login_tab:
    with st.form("login_form"):
        st.subheader("Welcome back!")
        email = st.text_input("Email", placeholder="you@example.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

    if submitted:
        if not email or not password:
            st.markdown('<div class="error-banner">Please fill in all fields</div>', unsafe_allow_html=True)
        else:
            try:
                data, status = api.login(email, password)
                if status == 200:
                    st.session_state["token"] = data["token"]
                    st.session_state["user"] = data["user"]
                    st.session_state["user_id"] = data["user"]["user_id"]
                    st.markdown('<div class="success-banner">✅ Login successful! Redirecting…</div>', unsafe_allow_html=True)
                    st.switch_page("pages/1_📊_Dashboard.py")
                else:
                    st.markdown(f'<div class="error-banner">{data.get("error", "Login failed")}</div>', unsafe_allow_html=True)
            except requests.exceptions.ConnectionError:
                st.markdown('<div class="error-banner">⚠️ Cannot connect to backend. Make sure Flask is running on port 5000.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-banner">Error: {e}</div>', unsafe_allow_html=True)

# ── Register ────────────────────────────────────────────
with register_tab:
    with st.form("register_form"):
        st.subheader("Get started free")
        name = st.text_input("Full Name", placeholder="John Doe", key="reg_name")
        email_r = st.text_input("Email", placeholder="you@example.com", key="reg_email")
        pass_r = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_pass")
        pass_c = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="reg_confirm")
        submitted_r = st.form_submit_button("Create Account", use_container_width=True, type="primary")

    if submitted_r:
        if not name or not email_r or not pass_r:
            st.markdown('<div class="error-banner">Please fill in all fields</div>', unsafe_allow_html=True)
        elif pass_r != pass_c:
            st.markdown('<div class="error-banner">Passwords do not match</div>', unsafe_allow_html=True)
        elif len(pass_r) < 6:
            st.markdown('<div class="error-banner">Password must be at least 6 characters</div>', unsafe_allow_html=True)
        else:
            try:
                data, status = api.register(name, email_r, pass_r)
                if status == 201:
                    st.session_state["token"] = data["token"]
                    st.session_state["user"] = data["user"]
                    st.session_state["user_id"] = data["user"]["user_id"]
                    st.markdown('<div class="success-banner">🎉 Account created! Redirecting…</div>', unsafe_allow_html=True)
                    st.switch_page("pages/1_📊_Dashboard.py")
                else:
                    st.markdown(f'<div class="error-banner">{data.get("error", "Registration failed")}</div>', unsafe_allow_html=True)
            except requests.exceptions.ConnectionError:
                st.markdown('<div class="error-banner">⚠️ Cannot connect to backend. Make sure Flask is running on port 5000.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-banner">Error: {e}</div>', unsafe_allow_html=True)

# ── Footer ──────────────────────────────────────────────
st.markdown("---")
st.caption("Procrastify — BCA Final Project")
