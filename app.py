import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date, time, timedelta
import uuid
import random
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="CLC Behaviour Support", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# MINIMALIST PROFESSIONAL STYLING
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: #f8fafc; }
    .stButton>button {
        background: #334155 !important; color: white !important;
        border: none !important; border-radius: 6px !important;
        padding: 0.5rem 1.2rem !important; font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s !important;
    }
    .stButton>button:hover { background: #1e293b !important; transform: translateY(-1px) !important; }
    button[kind="primary"] { background: #0ea5e9 !important; color: white !important; }
    button[kind="primary"]:hover { background: #0284c7 !important; }
    [data-testid="stVerticalBlock"] > div[style*="border"] {
        background: white !important; border-radius: 8px !important;
        padding: 1.5rem !important; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e2e8f0 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.875rem !important; font-weight: 700 !important; color: #0f172a !important;
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important; font-weight: 600 !important; font-size: 0.875rem !important;
        text-transform: uppercase !important; letter-spacing: 0.05em !important;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select, 
    .stTextArea>div>div>textarea, .stNumberInput>div>div>input,
    .stDateInput>div>div>input, .stTimeInput>div>div>input {
        border: 1px solid #cbd5e1 !important; background: white !important;
        color: #0f172a !important; font-weight: 500 !important; border-radius: 6px !important;
    }
    h1 { color: #0f172a !important; font-weight: 700 !important; }
    h2 { color: #0f172a !important; font-weight: 700 !important; }
    h3 { color: #0f172a !important; font-weight: 600 !important; }
    label { color: #334155 !important; font-weight: 600 !important; font-size: 0.875rem !important; }
    .stSuccess { background: #ecfdf5 !important; color: #065f46 !important; 
                 border-left: 4px solid #10b981 !important; }
    .stInfo { background: #f0f9ff !important; color: #075985 !important; 
              border-left: 4px solid #0ea5e9 !important; }
    .stWarning { background: #fffbeb !important; color: #92400e !important; 
                 border-left: 4px solid #f59e0b !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background: white; padding: 1.25rem; border-radius: 8px; margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); border-left: 4px solid #0ea5e9;'>
    <div style='color: #0f172a; font-weight: 700; font-size: 1.125rem; margin-bottom: 0.25rem;'>
        🎭 SANDBOX MODE
    </div>
    <div style='color: #64748b; font-size: 0.875rem; font-weight: 500;'>
        This demonstration uses synthetic data only. No real student information is included.
    </div>
</div>
""", unsafe_allow_html=True)

# MOCK DATA
MOCK_STAFF = [
    {"id": "s1", "name": "Emily Jones", "role": "JP", "email": "emily.jones@example.com", "password": "demo123"},
    {"id": "s2", "name": "Daniel Lee", "role": "PY", "email": "daniel.lee@example.com", "password": "demo123"},
    {"id": "s3", "name": "Sarah Chen", "role": "SY", "email": "sarah.chen@example.com", "password": "demo123"},
    {"id": "s4", "name": "Admin User", "role": "ADM", "email": "admin@example.com", "password": "admin123"},
]

MOCK_STUDENTS = [
    {"id": "stu_jp1", "name": "Emma T.", "grade": "R", "dob": "2018-05-30", "program": "JP"},
    {"id": "stu_jp2", "name": "Oliver S.", "grade": "Y1", "dob": "2017-09-12", "program": "JP"},
    {"id": "stu_jp3", "name": "Sophie M.", "grade": "Y2", "dob": "2016-03-20", "program": "JP"},
    {"id": "stu_py1", "name": "Liam C.", "grade": "Y3", "dob": "2015-06-15", "program": "PY"},
    {"id": "stu_py2", "name": "Ava R.", "grade": "Y4", "dob": "2014-11-08", "program": "PY"},
    {"id": "stu_py3", "name": "Noah B.", "grade": "Y6", "dob": "2012-02-28", "program": "PY"},
    {"id": "stu_sy1", "name": "Isabella G.", "grade": "Y7", "dob": "2011-04-17", "program": "SY"},
    {"id": "stu_sy2", "name": "Ethan D.", "grade": "Y9", "dob": "2009-12-03", "program": "SY"},
    {"id": "stu_sy3", "name": "Mia A.", "grade": "Y11", "dob": "2007-08-20", "program": "SY"},
]

PROGRAM_NAMES = {"JP": "Junior Primary", "PY": "Primary Years", "SY": "Senior Years"}
BEHAVIOUR_TYPES = ["Verbal Refusal", "Elopement", "Property Destruction", "Aggression (Peer)", 
                   "Aggression (Adult)", "Self-Harm", "Verbal Aggression", "Other"]
ANTECEDENTS = ["Requested to transition", "Given instruction/demand", "Peer conflict", 
               "Staff attention shifted", "Unstructured time", "Sensory overload", 
               "Access denied", "Change in routine", "Difficult task"]
INTERVENTIONS = ["CPI Supportive stance", "Offered break", "Reduced demand", "Provided choices", 
                "Removed audience", "Visual supports", "Co-regulation", "Prompted coping skill", "Redirection"]
LOCATIONS = ["JP Classroom", "PY Classroom", "SY Classroom", "Playground", "Library", "Admin", "Gate", "Toilets"]
VALID_PAGES = ["login", "landing", "program_students", "incident_log", "critical_incident", "student_analysis"]

# HYPOTHESIS GENERATOR
def generate_hypothesis(antecedent, behaviour, consequence):
    """Auto-generate hypothesis based on ABC data"""
    hypotheses = []
    
    # Escape/avoidance patterns
    if any(word in antecedent.lower() for word in ["instruction", "demand", "task", "transition", "work"]):
        hypotheses.append("To avoid or escape the demand/task")
    
    # Attention-seeking patterns
    if any(word in antecedent.lower() for word in ["attention", "shifted", "ignored", "alone"]):
        hypotheses.append("To gain staff/peer attention")
    
    # Sensory patterns
    if any(word in antecedent.lower() for word in ["sensory", "loud", "noise", "bright", "touch"]):
        hypotheses.append("To escape sensory discomfort or seek sensory input")
    
    # Access patterns
    if any(word in antecedent.lower() for word in ["denied", "can't have", "no", "wait"]):
        hypotheses.append("To gain access to preferred item/activity")
    
    # Control/power patterns
    if any(word in behaviour.lower() for word in ["refusal", "defiance", "left", "ran"]):
        hypotheses.append("To assert control or autonomy")
    
    # Default
    if not hypotheses:
        hypotheses.append("Function requires further analysis")
    
    return " / ".join(hypotheses[:2])  # Return top 2

def show_severity_guide():
    st.markdown("""
    <div style='background: white; padding: 1.25rem; border-radius: 8px; margin: 1rem 0; 
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0;'>
        <div style='color: #0f172a; font-weight: 700; margin-bottom: 1rem; font-size: 1rem;'>
            📊 Severity Level Guide
        </div>
        <div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem;'>
            <div style='background: #f8fafc; padding: 1rem; border-radius: 6px; border: 2px solid #cbd5e1;'>
                <div style='color: #0f172a; font-weight: 700; margin-bottom: 0.5rem;'>1 - Low</div>
                <div style='color: #64748b; font-size: 0.8rem; line-height: 1.3;'>Persistent minor behaviours</div>
            </div>
            <div style='background: #f1f5f9; padding: 1rem; border-radius: 6px; border: 2px solid #94a3b8;'>
                <div style='color: #0f172a; font-weight: 700; margin-bottom: 0.5rem;'>2 - Disruptive</div>
                <div style='color: #64748b; font-size: 0.8rem; line-height: 1.3;'>Impacts others</div>
            </div>
            <div style='background: #e2e8f0; padding: 1rem; border-radius: 6px; border: 2px solid #64748b;'>
                <div style='color: #0f172a; font-weight: 700; margin-bottom: 0.5rem;'>3 - Concerning</div>
                <div style='color: #475569; font-size: 0.8rem; line-height: 1.3;'>Verbal aggression</div>
            </div>
            <div style='background: #cbd5e1; padding: 1rem; border-radius: 6px; border: 2px solid #475569;'>
                <div style='color: #0f172a; font-weight: 700; margin-bottom: 0.5rem;'>4 - Serious</div>
                <div style='color: #334155; font-size: 0.8rem; line-height: 1.3;'>Physical aggression</div>
            </div>
            <div style='background: #94a3b8; padding: 1rem; border-radius: 6px; border: 2px solid #1e293b;'>
                <div style='color: #fff; font-weight: 700; margin-bottom: 0.5rem;'>5 - Critical</div>
                <div style='color: #f1f5f9; font-size: 0.8rem; line-height: 1.3;'>Severe violence</div>
            </div>
        </div>
        <div style='margin-top: 1rem; padding: 0.75rem; background: #fffbeb; border-radius: 6px; border-left: 4px solid #f59e0b;'>
            <div style='color: #92400e; font-weight: 600; font-size: 0.85rem;'>
                ⚠️ Severity 3 or above requires a Critical Incident ABCH Form
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def send_critical_incident_email(incident_data, student, staff_email, leader_email):
    """Send email notification"""
    st.info(f"""📧 **Email Notification Sent**
    
**To:** {leader_email}, {staff_email}  
**Subject:** CRITICAL INCIDENT - {student['name']}

**Student:** {student['name']} | **Programme:** {student['program']} | **Grade:** {student['grade']}  

Critical Incident Form completed and saved.

*(In production, this sends via SMTP)*
    """)


def generate_behaviour_analysis_plan_docx(student, full_df, top_ant, top_beh, top_loc, top_session, risk_score, risk_level):
    """Generate Word doc WITH graphs"""
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = Document()
        title = doc.add_heading('Behaviour Analysis Plan', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('Student Information', 1)
        info_table = doc.add_table(rows=4, cols=2)
        info_table.style = 'Light Grid Accent 1'
        info_table.rows[0].cells[0].text = 'Student:'
        info_table.rows[0].cells[1].text = student['name']
        info_table.rows[1].cells[0].text = 'Program:'
        info_table.rows[1].cells[1].text = student['program']
        info_table.rows[2].cells[0].text = 'Grade:'
        info_table.rows[2].cells[1].text = student['grade']
        info_table.rows[3].cells[0].text = 'Date:'
        info_table.rows[3].cells[1].text = datetime.now().strftime('%d/%m/%Y')
        
        doc.add_paragraph()
        doc.add_heading('Executive Summary', 1)
        summary = doc.add_paragraph()
        summary.add_run('Total Incidents: ').bold = True
        summary.add_run(f"{len(full_df)}\n")
        summary.add_run('Critical Incidents: ').bold = True
        summary.add_run(f"{len(full_df[full_df['incident_type'] == 'Critical'])}\n")
        summary.add_run('Average Severity: ').bold = True
        summary.add_run(f"{full_df['severity'].mean():.2f}\n")
        summary.add_run('Risk Level: ').bold = True
        summary.add_run(f"{risk_level} ({risk_score}/100)")
        
        doc.add_paragraph()
        doc.add_heading('Key Findings', 1)
        findings = doc.add_paragraph()
        findings.add_run('Primary Behaviour: ').bold = True
        findings.add_run(f"{top_beh}\n\n")
        findings.add_run('Most Common Trigger: ').bold = True
        findings.add_run(f"{top_ant}\n\n")
        findings.add_run('Hotspot Location: ').bold = True
        findings.add_run(f"{top_loc} during {top_session}")
        
        doc.add_paragraph()
        doc.add_heading('Visual Analytics', 1)
        
        try:
            # Graph embeddings here (same as before)
            daily = full_df.groupby(full_df["date_parsed"].dt.date).size().reset_index(name="count")
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=daily["date_parsed"], y=daily["count"], mode='lines+markers', 
                                     line=dict(color='#334155', width=2), fill='tozeroy'))
            fig1.update_layout(height=300, width=600, showlegend=False, plot_bgcolor='white', paper_bgcolor='white')
            img_path1 = "/tmp/daily_freq.png"
            fig1.write_image(img_path1)
            doc.add_picture(img_path1, width=Inches(5.5))
        except:
            doc.add_paragraph("Graph generation requires kaleido")
        
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def init_state():
    ss = st.session_state
    if "logged_in" not in ss: ss.logged_in = False
    if "current_user" not in ss: ss.current_user = None
    if "current_page" not in ss: ss.current_page = "login"
    if "students" not in ss: ss.students = MOCK_STUDENTS
    if "staff" not in ss: ss.staff = MOCK_STAFF
    if "incidents" not in ss: ss.incidents = generate_mock_incidents(70)
    if "critical_incidents" not in ss: ss.critical_incidents = []
    if "selected_program" not in ss: ss.selected_program = "JP"
    if "selected_student_id" not in ss: ss.selected_student_id = None
    if "current_incident_id" not in ss: ss.current_incident_id = None
    if "abch_rows" not in ss: ss.abch_rows = []
    if "show_critical_prompt" not in ss: ss.show_critical_prompt = False

def login_user(email: str, password: str) -> bool:
    email = (email or "").strip().lower()
    password = (password or "").strip()
    if not email or not password: return False
    for staff in st.session_state.staff:
        if staff.get("email", "").lower() == email and staff.get("password", "") == password:
            st.session_state.logged_in = True
            st.session_state.current_user = staff
            st.session_state.current_page = "landing"
            return True
    return False

def go_to(page: str, **kwargs):
    if page not in VALID_PAGES: return
    st.session_state.current_page = page
    for k, v in kwargs.items():
        setattr(st.session_state, k, v)
    st.rerun()

def get_student(sid): return next((s for s in st.session_state.students if s["id"] == sid), None)
def get_session_from_time(t): return "Morning" if t.hour < 11 else "Middle" if t.hour < 13 else "Afternoon"

def generate_mock_incidents(n=70):
    incidents = []
    weights = {"stu_sy1": 12, "stu_py1": 10, "stu_sy2": 9, "stu_jp1": 8, "stu_py2": 7}
    pool = []
    for stu in MOCK_STUDENTS:
        pool.extend([stu] * weights.get(stu["id"], 5))
    for _ in range(n):
        stu = random.choice(pool)
        sev = random.choices([1, 2, 3, 4, 5], weights=[20, 35, 25, 15, 5])[0]
        dt = datetime.now() - timedelta(days=random.randint(0, 90))
        dt = dt.replace(hour=random.choices([9,10,11,12,13,14,15], weights=[10,15,12,8,12,18,10])[0], 
                       minute=random.randint(0,59), second=0)
        incidents.append({
            "id": str(uuid.uuid4()), "student_id": stu["id"], "student_name": stu["name"],
            "date": dt.date().isoformat(), "time": dt.time().strftime("%H:%M:%S"),
            "day": dt.strftime("%A"), "session": get_session_from_time(dt.time()),
            "location": random.choice(LOCATIONS), "behaviour_type": random.choice(BEHAVIOUR_TYPES),
            "antecedent": random.choice(ANTECEDENTS), "intervention": random.choice(INTERVENTIONS),
            "severity": sev, "reported_by": random.choice(MOCK_STAFF)["name"],
            "description": "Mock incident", "is_critical": sev >= 3, "duration_minutes": random.randint(2, 25)
        })
    return incidents

# PAGES
def render_login_page():
    st.markdown("## 🔐 Staff Login")
    with st.container(border=True):
        st.markdown("**Demo Credentials:**")
        st.code("Email: emily.jones@example.com\nPassword: demo123")
    email = st.text_input("Email Address", placeholder="your.email@example.com", key="login_email")
    password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")
    if st.button("Login", type="primary", use_container_width=True):
        if login_user(email, password):
            st.success(f"Welcome {st.session_state.current_user['name']}!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def render_landing_page():
    user = st.session_state.current_user or {}
    st.markdown(f"### 👋 Welcome, {user.get('name', 'User')}")
    if st.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.current_page = "login"
        st.rerun()
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Students", len(st.session_state.students))
    with col2: st.metric("Total Incidents", len(st.session_state.incidents))
    with col3: st.metric("Critical", len([i for i in st.session_state.incidents if i.get("is_critical")]))
    st.markdown("---")
    st.markdown("### Select Program")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Junior Primary**")
        if st.button("Enter JP", use_container_width=True, type="primary", key="btn_jp"):
            go_to("program_students", selected_program="JP")
    with col2:
        st.markdown("**Primary Years**")
        if st.button("Enter PY", use_container_width=True, type="primary", key="btn_py"):
            go_to("program_students", selected_program="PY")
    with col3:
        st.markdown("**Senior Years**")
        if st.button("Enter SY", use_container_width=True, type="primary", key="btn_sy"):
            go_to("program_students", selected_program="SY")

def render_program_students_page():
    program = st.session_state.get("selected_program", "JP")
    st.markdown(f"## {PROGRAM_NAMES.get(program)} — Students")
    if st.button("⬅ Back", key="back_students"):
        go_to("landing")
    students = [s for s in st.session_state.students if s["program"] == program]
    for stu in students:
        stu_incidents = [i for i in st.session_state.incidents if i["student_id"] == stu["id"]]
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"**{stu['name']}**")
                st.caption(f"Grade {stu['grade']}")
            with col2:
                st.metric("Incidents", len(stu_incidents))
            with col3:
                if st.button("📝 Log", key=f"log_{stu['id']}", use_container_width=True):
                    go_to("incident_log", selected_student_id=stu["id"])
                if st.button("📊 Analysis", key=f"ana_{stu['id']}", use_container_width=True):
                    go_to("student_analysis", selected_student_id=stu["id"])


def render_incident_log_page():
    student_id = st.session_state.get("selected_student_id")
    student = get_student(student_id)
    if not student:
        st.error("No student selected")
        return
    
    st.markdown(f"## 📝 Incident Log — {student['name']}")
    show_severity_guide()
    
    # Check if we should show critical prompt
    if st.session_state.show_critical_prompt:
        inc_info = st.session_state.get("last_incident_info", {})
        if inc_info.get("severity", 0) >= 3:
            st.warning(f"⚠️ **Severity {inc_info['severity']} Detected** - Critical Incident Form Required")
        else:
            st.warning("⚠️ **Critical Incident Flagged** - Critical Incident Form Required")
        st.info("Please complete the Critical Incident ABCH form to document this event fully.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Complete Critical Form Now", type="primary", key="crit_now", use_container_width=True):
                st.session_state.show_critical_prompt = False
                go_to("critical_incident", current_incident_id=st.session_state.current_incident_id)
        with col2:
            if st.button("Skip for Now", key="crit_later", use_container_width=True):
                st.session_state.show_critical_prompt = False
                go_to("program_students", selected_program=student["program"])
        st.markdown("---")
        st.stop()
    
    # EMPTY FORM
    with st.form("incident_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            inc_date = st.date_input("Date *", date.today(), key="inc_date")
            inc_time = st.time_input("Time *", datetime.now().time(), key="inc_time")
            location = st.selectbox("Location *", [""] + LOCATIONS, key="inc_loc")
        with col2:
            behaviour = st.selectbox("Behaviour Type *", [""] + BEHAVIOUR_TYPES, key="inc_beh")
            antecedent = st.selectbox("Antecedent/Trigger *", [""] + ANTECEDENTS, key="inc_ant")
            intervention = st.selectbox("Intervention Used *", [""] + INTERVENTIONS, key="inc_int")
        duration = st.number_input("Duration (minutes) *", min_value=1, value=1, key="inc_dur")
        severity = st.slider("Severity Level *", 1, 5, 1, key="inc_sev")
        description = st.text_area("Brief Description (Optional)", placeholder="Factual, objective description...", key="inc_desc")
        manual_critical = st.checkbox("This incident requires a Critical Incident ABCH Form (regardless of severity)", key="manual_crit")
        submitted = st.form_submit_button("Submit Incident", type="primary")
    
    if submitted:
        if not location or not behaviour or not antecedent or not intervention:
            st.error("Please complete all required fields marked with *")
        else:
            new_id = str(uuid.uuid4())
            is_critical = (severity >= 3) or manual_critical
            rec = {
                "id": new_id, "student_id": student_id, "student_name": student["name"],
                "date": inc_date.isoformat(), "time": inc_time.strftime("%H:%M:%S"),
                "day": inc_date.strftime("%A"), "session": get_session_from_time(inc_time),
                "location": location, "behaviour_type": behaviour, "antecedent": antecedent,
                "intervention": intervention, "severity": severity,
                "reported_by": st.session_state.current_user["name"],
                "duration_minutes": duration, "description": description or "", 
                "is_critical": is_critical
            }
            st.session_state.incidents.append(rec)
            st.success("✅ Incident logged successfully")
            if is_critical:
                st.session_state.current_incident_id = new_id
                st.session_state.show_critical_prompt = True
                st.session_state.last_incident_info = {"severity": severity, "manual": manual_critical}
                st.rerun()
            else:
                st.markdown("---")
                if st.button("↩️ Back to Students", key="back_after_log"):
                    go_to("program_students", selected_program=student["program"])


def render_critical_incident_page():
    """NEW CRITICAL INCIDENT FORM - Matches your Word document structure"""
    inc_id = st.session_state.get("current_incident_id")
    quick_inc = next((i for i in st.session_state.incidents if i["id"] == inc_id), None)
    
    if not quick_inc:
        st.error("No incident found")
        return
    
    student = get_student(quick_inc["student_id"])
    st.markdown(f"## 🚨 Critical Incident ABCH Form")
    
    # SHOW QUICK INCIDENT DETAILS AT TOP
    st.markdown("### Incident Details (from Quick Log)")
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**Student:** {student['name']}")
            st.markdown(f"**Grade:** {student['grade']}")
        with col2:
            st.markdown(f"**Date:** {quick_inc['date']}")
            st.markdown(f"**Time:** {quick_inc['time']}")
        with col3:
            st.markdown(f"**Location:** {quick_inc['location']}")
            st.markdown(f"**Session:** {quick_inc['session']}")
        with col4:
            st.markdown(f"**Severity:** {quick_inc['severity']}")
            st.markdown(f"**Behaviour:** {quick_inc['behaviour_type']}")
    
    st.markdown("---")
    st.markdown("### ABCH Chronology")
    st.caption("Document the sequence of events. Add more rows if the incident involved multiple events.")
    
    # Initialize ABCH rows if needed
    if "abch_rows" not in st.session_state:
        st.session_state.abch_rows = []
    
    # PRIMARY ROW (always shown)
    st.markdown("#### Primary Incident")
    
    # Create the 5-column structure: Antecedent (2 cols) | Behaviour (2 cols) | Consequence | Hypothesis
    col_header = st.columns([2, 2, 2, 2, 2])
    with col_header[0]:
        st.markdown("**ANTECEDENT (Triggers)**")
    with col_header[1]:
        st.markdown("")  # Spans with Location
    with col_header[2]:
        st.markdown("**BEHAVIOUR**")
    with col_header[3]:
        st.markdown("")  # Spans with Time
    with col_header[4]:
        st.markdown("**CONSEQUENCES**")
    
    # Sub-headers for split columns
    col_subheader = st.columns([1, 1, 1, 1, 2, 2])
    with col_subheader[0]:
        st.caption("Location")
    with col_subheader[1]:
        st.caption("Context (what was happening?)")
    with col_subheader[2]:
        st.caption("Time")
    with col_subheader[3]:
        st.caption("Observed Behaviour (what did student do?)")
    with col_subheader[4]:
        st.caption("What happened after?")
    with col_subheader[5]:
        st.caption("HYPOTHESIS (Function)")
    
    # PRIMARY ROW INPUTS - Pre-fill time and location from quick incident
    col_inputs1 = st.columns([1, 1, 1, 1, 2, 2])
    
    with col_inputs1[0]:
        location_1 = st.text_input("", value=quick_inc['location'], key="loc_1", label_visibility="collapsed")
    
    with col_inputs1[1]:
        context_1 = st.text_area("", placeholder="What was going on before the behaviour? What was being said and done?", 
                                key="context_1", height=100, label_visibility="collapsed")
    
    with col_inputs1[2]:
        time_1 = st.text_input("", value=quick_inc['time'], key="time_1", label_visibility="collapsed")
    
    with col_inputs1[3]:
        behaviour_1 = st.text_area("", placeholder="What did the student do? Be specific and observable.", 
                                  key="behaviour_1", height=100, label_visibility="collapsed")
    
    with col_inputs1[4]:
        consequence_1 = st.text_area("", placeholder="What happened as a result? Staff response? Student reaction?", 
                                    key="consequence_1", height=100, label_visibility="collapsed")
    
    with col_inputs1[5]:
        # AUTO-GENERATE hypothesis, but allow editing
        if "hyp_1_generated" not in st.session_state:
            st.session_state.hyp_1_generated = False
        
        if not st.session_state.hyp_1_generated and context_1 and behaviour_1:
            auto_hyp = generate_hypothesis(context_1, behaviour_1, consequence_1)
            st.session_state.hyp_1_auto = auto_hyp
            st.session_state.hyp_1_generated = True
        
        hypothesis_1 = st.text_area("", 
                                    value=st.session_state.get("hyp_1_auto", ""),
                                    placeholder="Why did this occur? What was the student trying to achieve? (Auto-generated, you can edit)", 
                                    key="hypothesis_1", height=100, label_visibility="collapsed")
    
    st.markdown("---")
    
    # ADD MORE ROWS BUTTON
    if st.button("➕ Add Another Incident Row", key="add_abch_row"):
        st.session_state.abch_rows.append({})
        st.rerun()
    
    # ADDITIONAL ROWS
    for idx, row in enumerate(st.session_state.abch_rows):
        st.markdown(f"#### Incident {idx + 2}")
        
        col_add = st.columns([1, 1, 1, 1, 2, 2])
        
        with col_add[0]:
            row["location"] = st.text_input("", key=f"loc_{idx+2}", label_visibility="collapsed")
        with col_add[1]:
            row["context"] = st.text_area("", key=f"context_{idx+2}", height=100, label_visibility="collapsed")
        with col_add[2]:
            row["time"] = st.text_input("", key=f"time_{idx+2}", label_visibility="collapsed")
        with col_add[3]:
            row["behaviour"] = st.text_area("", key=f"behaviour_{idx+2}", height=100, label_visibility="collapsed")
        with col_add[4]:
            row["consequence"] = st.text_area("", key=f"consequence_{idx+2}", height=100, label_visibility="collapsed")
        with col_add[5]:
            # Auto-generate for additional rows too
            if row.get("context") and row.get("behaviour"):
                auto_hyp_add = generate_hypothesis(row["context"], row["behaviour"], row.get("consequence", ""))
                row["hypothesis"] = st.text_area("", value=auto_hyp_add, key=f"hypothesis_{idx+2}", height=100, label_visibility="collapsed")
            else:
                row["hypothesis"] = st.text_area("", key=f"hypothesis_{idx+2}", height=100, label_visibility="collapsed")
        
        st.markdown("---")
    
    # INTENDED OUTCOMES SECTION
    st.markdown("### Intended Outcomes")
    st.caption("What are we aiming to achieve through this intervention?")
    
    outcomes_options = [
        "Send Home", "Parent/Caregiver notified via Phone Call",
        "Student Leaving supervised areas/leaving school grounds",
        "Sexualised behaviour", "Incident – student to student",
        "Complaint by co-located school/member of public",
        "Property damage", "Stealing", "Toileting issue",
        "ED155: Staff Injury", "ED155: Student injury",
        "Emergency services - SAPOL", "Emergency services - SA Ambulance",
        "Incident Internally Managed - Restorative Session",
        "Incident Internally Managed - Community Service",
        "Incident Internally Managed - Re-Entry",
        "Incident Internally Managed - Case Review",
        "Incident Internally Managed - Make-up Time"
    ]
    
    selected_outcomes = st.multiselect("Select all intended outcomes:", outcomes_options, key="intended_outcomes")
    
    # TAC Meeting notes
    tac_notes = st.text_area("Additional Outcome Notes (e.g., TAC meeting, other actions):", 
                            placeholder="A TAC meeting will be held to discuss solutions to support the student...",
                            key="tac_notes", height=100)
    
    st.markdown("---")
    
    # NOTIFICATIONS
    st.markdown("### Notifications & Administration")
    
    col_notif1, col_notif2 = st.columns(2)
    with col_notif1:
        notified_line_manager = st.checkbox("Notified Line Manager of Critical Incident", key="notif_manager", value=True)
        notified_parent = st.checkbox("Notified Parent/Caregiver of Critical Incident", key="notif_parent")
    with col_notif2:
        copy_in_file = st.checkbox("Copy of Critical Incident in student file", key="copy_file", value=True)
        safety_plan_review = st.checkbox("Safety and Risk Plan to be developed/reviewed", key="safety_review")
    
    st.markdown("---")
    
    # STAFF AGREEMENT & SIGNATURE
    st.markdown("### Staff Agreement")
    
    staff_name = st.session_state.current_user.get("name", "Staff Member")
    st.markdown(f"**Completing Staff Member:** {staff_name}")
    
    staff_agrees = st.checkbox(f"✓ I, {staff_name}, confirm that the information entered in this Critical Incident Form is accurate and complete.", 
                               key="staff_agrees")
    
    st.markdown("---")
    
    # LEADER EMAIL
    st.markdown("### Send to Line Manager")
    leader_email = st.text_input("Line Manager Email *", 
                                 placeholder="manager@clc.sa.edu.au",
                                 value="manager@clc.sa.edu.au",
                                 key="leader_email")
    
    st.markdown("---")
    
    # SAVE BUTTON
    if st.button("📧 Submit Critical Incident Form (sends email)", type="primary", use_container_width=True, key="save_crit"):
        # Validation
        if not context_1 or not behaviour_1 or not consequence_1 or not hypothesis_1:
            st.error("❌ Please complete all ABCH fields for the primary incident")
        elif not staff_agrees:
            st.error("❌ Please confirm your agreement by checking the box above")
        elif not leader_email or "@" not in leader_email:
            st.error("❌ Please enter a valid Line Manager email address")
        else:
            # SAVE TO DATABASE
            record = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
                "quick_incident_id": inc_id,
                "student_id": quick_inc["student_id"],
                "student_name": student["name"],
                "incident_type": "Critical",  # Mark as critical
                "ABCH_primary": {
                    "location": location_1,
                    "context": context_1,
                    "time": time_1,
                    "behaviour": behaviour_1,
                    "consequence": consequence_1,
                    "hypothesis": hypothesis_1
                },
                "ABCH_additional": st.session_state.abch_rows.copy(),
                "intended_outcomes": selected_outcomes,
                "tac_notes": tac_notes,
                "notifications": {
                    "line_manager": notified_line_manager,
                    "parent": notified_parent,
                    "copy_in_file": copy_in_file,
                    "safety_plan_review": safety_plan_review
                },
                "staff_agreement": {
                    "staff_name": staff_name,
                    "agreed": staff_agrees,
                    "timestamp": datetime.now().isoformat()
                },
                "leader_email": leader_email
            }
            
            st.session_state.critical_incidents.append(record)
            st.session_state.abch_rows = []  # Clear rows
            st.session_state.hyp_1_generated = False  # Reset
            
            st.success("✅ Critical incident form saved successfully to database")
            
            # SEND EMAIL
            staff_email = st.session_state.current_user.get("email", "staff@example.com")
            send_critical_incident_email(record, student, staff_email, leader_email)
            
            st.markdown("---")
            st.info("✉️ Emails sent to Line Manager and completing staff member")
            st.info("💾 Critical incident data saved in student's file")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 View Student Analysis", type="primary", use_container_width=True, key="view_analysis"):
                    go_to("student_analysis", selected_student_id=quick_inc["student_id"])
            with col2:
                if st.button("↩️ Back to Students", use_container_width=True, key="back_crit"):
                    go_to("program_students", selected_program=student["program"])


def render_student_analysis_page():
    """Simplified analysis page"""
    student_id = st.session_state.get("selected_student_id")
    student = get_student(student_id)
    if not student:
        st.error("No student selected")
        return
    
    st.markdown(f"## 📊 Data Analysis — {student['name']}")
    
    quick = [i for i in st.session_state.incidents if i["student_id"] == student_id]
    crit = [c for c in st.session_state.critical_incidents if c["student_id"] == student_id]
    
    if not quick and not crit:
        st.info("No incident data available yet.")
        if st.button("↩️ Back", key="back_no_data"):
            go_to("program_students", selected_program=student["program"])
        return
    
    # Build dataframe
    quick_df = pd.DataFrame(quick) if quick else pd.DataFrame()
    crit_df = pd.DataFrame(crit) if crit else pd.DataFrame()
    
    if not quick_df.empty:
        quick_df["incident_type"] = "Quick"
        quick_df["date_parsed"] = pd.to_datetime(quick_df["date"])
    
    if not crit_df.empty:
        crit_df["incident_type"] = "Critical"
        crit_df["date_parsed"] = pd.to_datetime(crit_df.get("created_at", datetime.now().isoformat()))
        crit_df["severity"] = 5
    
    full_df = pd.concat([quick_df, crit_df], ignore_index=True).sort_values("date_parsed")
    
    # OVERVIEW
    st.markdown("### 📈 Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total", len(full_df))
    with col2: st.metric("Critical", len(full_df[full_df["incident_type"] == "Critical"]))
    with col3: st.metric("Avg Severity", f"{full_df['severity'].mean():.1f}")
    with col4:
        days = max((full_df["date_parsed"].max() - full_df["date_parsed"].min()).days, 1)
        st.metric("Days Span", days)
    
    st.markdown("---")
    
    # Simple daily frequency graph
    st.markdown("### 📅 Daily Incident Frequency")
    daily = full_df.groupby(full_df["date_parsed"].dt.date).size().reset_index(name="count")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=daily["date_parsed"], y=daily["count"],
        mode='lines+markers', line=dict(color='#334155', width=2),
        marker=dict(size=7, color='#334155'),
        fill='tozeroy', fillcolor='rgba(51, 65, 85, 0.1)'
    ))
    fig1.update_layout(
        height=280, showlegend=False, xaxis_title="Date", yaxis_title="Incidents",
        plot_bgcolor='white', paper_bgcolor='white'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    
    # Top behaviours
    if "behaviour_type" in full_df.columns:
        st.markdown("### 🎯 Most Common Behaviours")
        beh_counts = full_df["behaviour_type"].value_counts().head(5)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            y=beh_counts.index, x=beh_counts.values,
            orientation='h', marker=dict(color='#475569'),
            text=beh_counts.values, textposition='outside'
        ))
        fig2.update_layout(
            height=280, showlegend=False, xaxis_title="Frequency",
            plot_bgcolor='white', paper_bgcolor='white'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # Export buttons
    st.markdown("### 📄 Export Data")
    col1, col2 = st.columns(2)
    with col1:
        csv = full_df.to_csv(index=False)
        st.download_button(
            "📥 Download Raw Data (CSV)",
            csv,
            file_name=f"{student['name']}_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    
    if st.button("⬅ Back to Students", type="primary", key="back_analysis"):
        go_to("program_students", selected_program=student["program"])

def main():
    init_state()
    
    if not st.session_state.logged_in:
        render_login_page()
        return
    
    page = st.session_state.current_page
    
    if page == "landing": render_landing_page()
    elif page == "program_students": render_program_students_page()
    elif page == "incident_log": render_incident_log_page()
    elif page == "critical_incident": render_critical_incident_page()
    elif page == "student_analysis": render_student_analysis_page()
    else: render_landing_page()

if __name__ == "__main__":
    main()
