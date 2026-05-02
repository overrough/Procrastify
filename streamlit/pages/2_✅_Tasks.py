import streamlit as st
from datetime import date, timedelta
from utils import create_task, get_tasks, complete_task, delete_task, require_auth, URGENCY_COLORS, setup_sidebar

st.set_page_config(page_title="Tasks | Procrastify", page_icon="✅", layout="wide")
require_auth()
setup_sidebar()

if st.session_state.get("focus_active"):
    st.warning("⚠️ You have an active focus session! Go back to the timer to finish it.")
    if st.button("⏱️ Go to Focus Timer"):
        st.switch_page("pages/3_⏱️_Focus_Timer.py")
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
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

.task-card {
    border-left: 4px solid;
    background: #162231;
    border-radius: 0 0.75rem 0.75rem 0;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    border-top: 1px solid #1e3a4f;
    border-right: 1px solid #1e3a4f;
    border-bottom: 1px solid #1e3a4f;
}
.task-card h4 { margin: 0 0 0.25rem; font-weight: 700; color: #e2e8f0; }
.task-card .meta { color: #94a3b8; font-size: 0.85rem; }
.priority-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 700;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h2>✅ Task Manager</h2>
    <p>Add, prioritize, and conquer your tasks</p>
</div>
""", unsafe_allow_html=True)

with st.expander("➕ Add New Task", expanded=False):
    with st.form("add_task_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Task Title", placeholder="e.g. BCA Unit 3 Notes")
            category = st.selectbox("Category", ["Study", "Personal", "Work", "Other"])
        with col2:
            deadline = st.date_input("Deadline", value=date.today() + timedelta(days=3), min_value=date.today())
            complexity = st.slider("Complexity", 1, 5, 3, help="1 = Easy, 5 = Very Hard")
        description = st.text_area("Description (optional)", placeholder="Any extra details…", height=80)
        submitted = st.form_submit_button("Add Task", use_container_width=True, type="primary")

    if submitted:
        if not title:
            st.error("Please enter a task title.")
        else:
            try:
                data, status = create_task(title, str(deadline), complexity, category, description)
                if status == 201:
                    st.success(f"✅ Task '{title}' created!")
                    st.rerun()
                else:
                    st.error(data.get("error", "Failed to create task"))
            except Exception as e:
                st.error(f"Error: {e}")

tab_pending, tab_completed, tab_all = st.tabs(["📋 Pending", "✅ Completed", "📁 All"])

def render_tasks(status_filter):
    try:
        data, code = get_tasks(status_filter)
        if code != 200:
            st.error("Failed to load tasks")
            return
    except Exception:
        st.warning("⚠️ Cannot connect to backend.")
        return
    tasks = data.get("tasks", [])
    summary = data.get("summary", {})
    if not tasks:
        st.info("No tasks here yet!")
        return
    if summary:
        if status_filter == "pending":
            s1, s2 = st.columns(2)
            s1.metric("Total", summary.get("total", len(tasks)))
            s2.metric("Urgent", summary.get("high", 0) + summary.get("overdue", 0))
        elif status_filter == "completed":
            s1, s2 = st.columns(2)
            s1.metric("Total", summary.get("total", len(tasks)))
            s2.metric("Completed", summary.get("completed", 0))
        else:
            s1, s2, s3 = st.columns(3)
            s1.metric("Total", summary.get("total", len(tasks)))
            s2.metric("Urgent", summary.get("high", 0) + summary.get("overdue", 0))
            s3.metric("Overdue", summary.get("overdue", 0))
    st.markdown("---")
    for task in tasks:
        color = URGENCY_COLORS.get(task.get("urgency_level", "low").lower(), "#4CAF50")
        level = task.get("urgency_level", "low").upper()
        days = task.get("days_remaining", "?")
        days_text = f"{days} day(s) left" if isinstance(days, int) and days >= 0 else "⚠️ OVERDUE"
        st.markdown(f"""
        <div class="task-card" style="border-left-color: {color}">
            <h4>{task.get("title", "Untitled")}
                <span class="priority-badge" style="background:{color}">{level}</span>
            </h4>
            <div class="meta">
                📂 {task.get("category", "—")} &nbsp;·&nbsp;
                📅 {task.get("deadline", "—")} ({days_text}) &nbsp;·&nbsp;
                ⚡ Complexity {task.get("complexity", "?")} &nbsp;·&nbsp;
                🏆 Priority Score: {task.get("priority_score", "—")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if task.get("status") != "completed":
            bc1, bc2, _ = st.columns([1, 1, 4])
            task_id = task.get("task_id")
            with bc1:
                if st.button("✅ Complete", key=f"done_{status_filter}_{task_id}"):
                    try:
                        complete_task(task_id)
                        st.rerun()
                    except Exception:
                        st.error("Failed to complete")
            with bc2:
                if st.button("🗑️ Delete", key=f"del_{status_filter}_{task_id}"):
                    try:
                        delete_task(task_id)
                        st.rerun()
                    except Exception:
                        st.error("Failed to delete")

with tab_pending:
    render_tasks("pending")

with tab_completed:
    render_tasks("completed")

with tab_all:
    render_tasks("all")

st.markdown("---")
st.caption("Procrastify — BCA Final Project")
