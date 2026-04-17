# focus timer page pomodoro countdown with session tracking
import streamlit as st
import streamlit.components.v1 as components
from utils import start_session, end_session, get_session_history, require_auth, setup_sidebar

st.set_page_config(page_title="Focus Timer | Procrastify", page_icon="⏱️", layout="centered")
require_auth()
setup_sidebar()

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
.session-card {
    background: #162231;
    border: 1px solid #1e3a4f;
    border-radius: 0.5rem;
    padding: 0.6rem 1rem;
    margin-bottom: 0.4rem;
    display: flex;
    justify-content: space-between;
}
.tip-box {
    background: rgba(45,212,191,0.08);
    border: 1px solid rgba(45,212,191,0.2);
    border-radius: 0.75rem;
    padding: 1rem;
    margin-top: 1rem;
    color: #94a3b8;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h2>⏱️ Focus Timer</h2>
    <p>Stay focused — no distractions allowed!</p>
</div>
""", unsafe_allow_html=True)

# Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "focus_active" not in st.session_state:
    st.session_state.focus_active = False
if "timer_duration" not in st.session_state:
    st.session_state.timer_duration = 25

# When focus is active hide sidebar nav
if st.session_state.focus_active:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    st.info("🔒 Focus mode is ON — sidebar is hidden. Complete or end your session to navigate away.")

#JS-based Timer
dur = st.session_state.timer_duration
timer_html = f"""
<div id="timer-wrap" style="text-align:center;padding:1.5rem;font-family:'Inter',sans-serif;caret-color:transparent;">
    <div id="timer-display" style="
        font-size:5rem;font-weight:700;color:#2dd4bf;margin-bottom:0.25rem;
    ">{dur:02d}:00</div>
    <div id="timer-label" style="font-size:1rem;color:#94a3b8;margin-bottom:1.5rem;">Ready to focus?</div>
    <div style="display:flex;gap:0.75rem;justify-content:center;margin-bottom:1rem;">
        <button onclick="startTimer()" style="
            background:#2dd4bf;color:#0f1923;border:none;padding:0.6rem 1.5rem;
            border-radius:0.5rem;font-size:0.95rem;font-weight:600;cursor:pointer;
        ">▶️ Start</button>
        <button onclick="pauseTimer()" style="
            background:#162231;color:#e2e8f0;border:1px solid #1e3a4f;
            padding:0.6rem 1.5rem;border-radius:0.5rem;font-size:0.95rem;cursor:pointer;
        ">⏸️ Pause</button>
        <button onclick="resetTimer()" style="
            background:#162231;color:#e2e8f0;border:1px solid #1e3a4f;
            padding:0.6rem 1.5rem;border-radius:0.5rem;font-size:0.95rem;cursor:pointer;
        ">🔄 Reset</button>
    </div>
    <div style="display:flex;gap:0.4rem;justify-content:center;">
        <button onclick="setDur(15)" style="background:rgba(45,212,191,0.1);color:#2dd4bf;border:1px solid rgba(45,212,191,0.2);padding:0.35rem 0.8rem;border-radius:2rem;font-size:0.8rem;cursor:pointer;">15m</button>
        <button onclick="setDur(25)" style="background:rgba(45,212,191,0.1);color:#2dd4bf;border:1px solid rgba(45,212,191,0.2);padding:0.35rem 0.8rem;border-radius:2rem;font-size:0.8rem;cursor:pointer;">25m</button>
        <button onclick="setDur(45)" style="background:rgba(45,212,191,0.1);color:#2dd4bf;border:1px solid rgba(45,212,191,0.2);padding:0.35rem 0.8rem;border-radius:2rem;font-size:0.8rem;cursor:pointer;">45m</button>
        <button onclick="setDur(60)" style="background:rgba(45,212,191,0.1);color:#2dd4bf;border:1px solid rgba(45,212,191,0.2);padding:0.35rem 0.8rem;border-radius:2rem;font-size:0.8rem;cursor:pointer;">60m</button>
    </div>
    <div style="margin-top:1rem;">
        <div style="background:#1e3a4f;border-radius:4px;height:6px;width:100%;">
            <div id="pbar" style="background:#2dd4bf;border-radius:4px;height:6px;width:0%;transition:width 1s linear;"></div>
        </div>
    </div>
</div>
<script>
    let total={dur}*60, rem=total, iv=null, on=false;
    function upd(){{
        let m=Math.floor(rem/60),s=rem%60;
        document.getElementById('timer-display').textContent=String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');
        document.getElementById('pbar').style.width=((total-rem)/total*100)+'%';
    }}
    function startTimer(){{
        if(on)return;on=true;
        document.getElementById('timer-label').textContent='🟢 Focus Mode Active';
        iv=setInterval(()=>{{
            if(rem<=0){{clearInterval(iv);on=false;
                document.getElementById('timer-label').textContent='🎉 Session Complete!';
                document.getElementById('timer-display').style.color='#22c55e';return;}}
            rem--;upd();
        }},1000);
    }}
    function pauseTimer(){{clearInterval(iv);on=false;document.getElementById('timer-label').textContent='⏸️ Paused';}}
    function resetTimer(){{clearInterval(iv);on=false;rem=total;upd();
        document.getElementById('timer-label').textContent='Ready to focus?';
        document.getElementById('timer-display').style.color='#2dd4bf';}}
    function setDur(m){{if(on)return;total=m*60;rem=total;upd();}}
</script>
"""
components.html(timer_html, height=320)

# Server session controls
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("🎯 Start Focus Session", use_container_width=True, type="primary",
                 disabled=st.session_state.focus_active):
        try:
            data, status = start_session()
            if status == 201:
                st.session_state.session_id = data.get("session_id")
                st.session_state.focus_active = True
                st.success(f"Session #{st.session_state.session_id} started! Press ▶️ Start above.")
                st.rerun()
            else:
                st.error("Failed to start session")
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    if st.button("✅ End & Save Session", use_container_width=True,
                 disabled=not st.session_state.focus_active):
        if st.session_state.session_id:
            try:
                data, _ = end_session(st.session_state.session_id, completed=True,
                                          interruptions=0, focus_score=100)
                streak = data.get("current_streak", 0)
                st.session_state.focus_active = False
                st.session_state.session_id = None
                st.success(f"🎉 Session saved! Streak: {streak} days")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.session_state.focus_active = False
            st.warning("No server session found. Focus lock released.")
            st.rerun()

# Tips
st.markdown("""
<div class="tip-box">
    <strong>💡 Tips</strong><br>
    • Put your phone face down<br>
    • Close other browser tabs<br>
    • Take a 5-min break between sessions
</div>
""", unsafe_allow_html=True)

# Session History 
st.markdown("---")
st.subheader("📜 Recent Sessions")
try:
    hd, _ = get_session_history(5)
    sessions = hd.get("sessions", [])
    if not sessions:
        st.info("No sessions yet — start your first one above!")
    else:
        for s in sessions:
            icon = "✅" if s.get("completed") else "⏸️"
            start = s.get("start_time", "?")[:16].replace("T", " ")
            score = s.get("focus_score", 0)
            st.markdown(f"""
            <div class="session-card">
                <div>{icon} {start}</div>
                <div style="opacity:0.6;font-size:0.85rem">Score: {score}%</div>
            </div>""", unsafe_allow_html=True)
except Exception:
    st.warning("Could not load history.")

st.markdown("---")
st.caption("Procrastify — BCA Final Project")
