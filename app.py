import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date, time, timedelta
import uuid
import random
from io import BytesIO
import base64
import bcrypt

# SUPABASE CONNECTION
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    st.warning("⚠️ Supabase not installed. Run: pip install supabase")

# Initialize Supabase client
@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client with credentials from secrets"""
    if not SUPABASE_AVAILABLE:
        return None
    
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Supabase connection failed: {e}")
        st.info("💡 Add Supabase credentials to .streamlit/secrets.toml")
        return None

# Global Supabase client
supabase: Client = init_supabase()

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

# Production mode - sandbox banner removed

# MOCK DATA
MOCK_STAFF = [
    {"id": "s1", "name": "Emily Jones", "role": "JP", "email": "emily.jones@example.com", "password": "demo123"},
    {"id": "s2", "name": "Daniel Lee", "role": "PY", "email": "daniel.lee@example.com", "password": "demo123"},
    {"id": "s3", "name": "Sarah Chen", "role": "SY", "email": "sarah.chen@example.com", "password": "demo123"},
    {"id": "s4", "name": "Admin User", "role": "ADM", "email": "admin@example.com", "password": "admin123"},
]

MOCK_STUDENTS = [
    {"id": "stu_jp1", "name": "Emma T.", "grade": "R", "dob": "2018-05-30", "program": "JP", 
     "edid": "ED123456", "placement_start": "2024-02-01", "placement_end": None},
    {"id": "stu_jp2", "name": "Oliver S.", "grade": "Y1", "dob": "2017-09-12", "program": "JP",
     "edid": "ED234567", "placement_start": "2024-03-15", "placement_end": None},
    {"id": "stu_jp3", "name": "Sophie M.", "grade": "Y2", "dob": "2016-03-20", "program": "JP",
     "edid": "ED345678", "placement_start": "2024-01-29", "placement_end": None},
    {"id": "stu_py1", "name": "Liam C.", "grade": "Y3", "dob": "2015-06-15", "program": "PY",
     "edid": "ED456789", "placement_start": "2024-02-12", "placement_end": None},
    {"id": "stu_py2", "name": "Ava R.", "grade": "Y4", "dob": "2014-11-08", "program": "PY",
     "edid": "ED567890", "placement_start": "2024-01-08", "placement_end": None},
    {"id": "stu_py3", "name": "Noah B.", "grade": "Y6", "dob": "2012-02-28", "program": "PY",
     "edid": "ED678901", "placement_start": "2024-04-03", "placement_end": None},
    {"id": "stu_sy1", "name": "Isabella G.", "grade": "Y7", "dob": "2011-04-17", "program": "SY",
     "edid": "ED789012", "placement_start": "2024-01-29", "placement_end": None},
    {"id": "stu_sy2", "name": "Ethan D.", "grade": "Y9", "dob": "2009-12-03", "program": "SY",
     "edid": "ED890123", "placement_start": "2024-02-26", "placement_end": None},
    {"id": "stu_sy3", "name": "Mia A.", "grade": "Y11", "dob": "2007-08-20", "program": "SY",
     "edid": "ED901234", "placement_start": "2024-03-11", "placement_end": None},
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
VALID_PAGES = ["login", "landing", "program_students", "incident_log", "critical_incident", "student_analysis", "admin_portal"]

# AI HYPOTHESIS SYSTEM
HYPOTHESIS_FUNCTIONS = ["To get", "To avoid"]
HYPOTHESIS_ITEMS = ["Tangible", "Activity", "Sensory", "Attention"]

def format_time_12hr(time_str):
    """Convert 24hr time string to 12hr format"""
    try:
        if isinstance(time_str, str):
            dt = datetime.strptime(time_str, "%H:%M:%S")
        else:
            dt = datetime.combine(date.today(), time_str)
        return dt.strftime("%I:%M %p")
    except:
        return time_str

def generate_hypothesis(antecedent, behaviour, consequence):
    """Auto-generate hypothesis based on ABC data"""
    hypotheses = []
    antecedent_lower = antecedent.lower()
    behaviour_lower = behaviour.lower()
    
    if any(word in antecedent_lower for word in ["instruction", "demand", "task", "transition", "work"]):
        hypotheses.append("To avoid or escape the demand/task")
    if any(word in antecedent_lower for word in ["attention", "shifted", "ignored", "alone"]):
        hypotheses.append("To gain staff/peer attention")
    if any(word in antecedent_lower for word in ["sensory", "loud", "noise", "bright", "touch"]):
        hypotheses.append("To escape sensory discomfort or seek sensory input")
    if any(word in antecedent_lower for word in ["denied", "can't have", "no", "wait"]):
        hypotheses.append("To gain access to preferred item/activity")
    if any(word in behaviour_lower for word in ["refusal", "defiance", "left", "ran"]):
        hypotheses.append("To assert control or autonomy")
    
    if not hypotheses:
        hypotheses.append("Function requires further analysis")
    
    return " / ".join(hypotheses[:2])

def generate_admin_summary(incident_data, student, staff_name):
    """Generate brief summary for external incident log - FOR ADMIN USE ONLY"""
    abch_primary = incident_data.get("ABCH_primary", {})
    intended = incident_data.get("intended_outcomes", [])
    
    date_time = incident_data.get("created_at", datetime.now().isoformat())
    dt = datetime.fromisoformat(date_time)
    
    location = abch_primary.get("location", "Unknown location")
    time_str = abch_primary.get("time", "Unknown time")
    behaviour = abch_primary.get("behaviour", "Behaviour not specified")
    context = abch_primary.get("context", "")
    consequence = abch_primary.get("consequence", "")
    hypothesis = abch_primary.get("hypothesis", "")
    
    summary = f"""CRITICAL INCIDENT SUMMARY - FOR ADMIN USE ONLY
    
Student: {student['name']} (Grade {student['grade']})
Date/Time: {dt.strftime('%d/%m/%Y')} at {time_str}
Location: {location}

INCIDENT DESCRIPTION:
{behaviour[:200]}{'...' if len(behaviour) > 200 else ''}

CONTEXT/ANTECEDENT:
{context[:200]}{'...' if len(context) > 200 else ''}

IMMEDIATE STAFF RESPONSE:
{consequence[:200]}{'...' if len(consequence) > 200 else ''}

BEHAVIOURAL FUNCTION:
{hypothesis}

OUTCOMES IMPLEMENTED:
{', '.join(intended[:5]) if intended else 'See full form for details'}

REPORTED BY: {staff_name}
FORM COMPLETED: {dt.strftime('%d/%m/%Y %H:%M')}

** This summary is for external departmental incident log entry purposes only **
** Full critical incident form has been saved and distributed to relevant parties **
"""
    
    return summary


def generate_hypothesis_ai(antecedent, behaviour, consequence=""):
    """AI generates structured hypothesis from ABC data"""
    ant_lower = (antecedent or "").lower()
    beh_lower = (behaviour or "").lower()
    cons_lower = (consequence or "").lower()
    
    avoid_keywords = ["instruction", "demand", "task", "transition", "work", "difficult", "challenging"]
    get_keywords = ["attention", "item", "toy", "want", "access", "denied"]
    
    function = "To avoid"
    if any(word in ant_lower for word in get_keywords):
        function = "To get"
    elif any(word in cons_lower for word in ["given", "received", "got"]):
        function = "To get"
    elif "denied" in ant_lower or "can't" in ant_lower:
        function = "To get"
    
    item = "Activity"
    if any(word in ant_lower + beh_lower for word in ["attention", "staff", "peer", "ignored"]):
        item = "Attention"
    elif any(word in ant_lower + beh_lower for word in ["sensory", "loud", "noise", "touch"]):
        item = "Sensory"
    elif any(word in ant_lower + beh_lower for word in ["toy", "item", "object", "food"]):
        item = "Tangible"
    elif any(word in ant_lower for word in ["instruction", "demand", "task", "work"]):
        item = "Activity"
    
    return {"function": function, "item": item}

def format_hypothesis(hyp):
    """Format hypothesis dict to string"""
    if isinstance(hyp, dict):
        return f"{hyp.get('function', 'Unknown')} {hyp.get('item', 'Unknown')}"
    elif isinstance(hyp, str):
        return hyp
    else:
        return "Unknown"

def show_severity_guide():
    st.markdown("""
    <div style='background: white; padding: 1.25rem; border-radius: 8px; margin: 1rem 0; 
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0;'>
        <div style='color: #0f172a; font-weight: 700; margin-bottom: 1rem; font-size: 1rem;'>
            📊 Severity Level Guide (from start to end of incident)
        </div>
        <div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem;'>
            <div style='background: #f8fafc; padding: 1rem; border-radius: 6px; border: 2px solid #cbd5e1;'>
                <div style='color: #0f172a; font-weight: 700; margin-bottom: 0.5rem;'>1 - Low</div>
                <div style='color: #64748b; font-size: 0.8rem;'>Persistent minor</div>
            </div>
            <div style='background: #f1f5f9; padding: 1rem; border-radius: 6px; border: 2px solid #94a3b8;'>
                <div style='color: #0f172a; font-weight: 700; margin-bottom: 0.5rem;'>2 - Disruptive</div>
                <div style='color: #64748b; font-size: 0.8rem;'>Impacts others</div>
            </div>
            <div style='background: #e2e8f0; padding: 1rem; border-radius: 6px; border: 2px solid #64748b;'>
                <div style='color: #0f172a; font-weight: 700; margin-bottom: 0.5rem;'>3 - Concerning</div>
                <div style='color: #475569; font-size: 0.8rem;'>Verbal aggression</div>
            </div>
            <div style='background: #cbd5e1; padding: 1rem; border-radius: 6px; border: 2px solid #475569;'>
                <div style='color: #0f172a; font-weight: 700; margin-bottom: 0.5rem;'>4 - Serious</div>
                <div style='color: #334155; font-size: 0.8rem;'>Physical aggression</div>
            </div>
            <div style='background: #94a3b8; padding: 1rem; border-radius: 6px; border: 2px solid #1e293b;'>
                <div style='color: #fff; font-weight: 700; margin-bottom: 0.5rem;'>5 - Critical</div>
                <div style='color: #f1f5f9; font-size: 0.8rem;'>Severe violence</div>
            </div>
        </div>
        <div style='margin-top: 1rem; padding: 0.75rem; background: #fffbeb; border-radius: 6px; border-left: 4px solid #f59e0b;'>
            <div style='color: #92400e; font-weight: 600; font-size: 0.85rem;'>
                ⚠️ Severity 3 or above requires a Critical Incident ABCH Form
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def send_critical_incident_email(incident_data, student, staff_email, leader_email, admin_email):
    """Send email notification to all parties"""
    st.info(f"""📧 **Email Notification Sent**
    
**To:** {leader_email}, {admin_email}, {staff_email}  
**Subject:** CRITICAL INCIDENT - {student['name']}

**Student:** {student['name']} | **Programme:** {student['program']} | **Grade:** {student['grade']}  

Critical Incident Form completed and saved.
Admin summary included for departmental log.

*(In production, this sends via SMTP)*
    """)



def generate_behaviour_analysis_plan_docx(student, full_df, top_ant, top_beh, top_loc, top_session, risk_score, risk_level):
    """Generate comprehensive BAP with matplotlib graphs (no Chrome/Kaleido needed)"""
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        
        # ARIAL FONT SETUP
        from docx.oxml.ns import qn
        
        def set_arial(run):
            """Set Arial font for a run"""
            run.font.name = 'Arial'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
        
        # GREEN COLOR for headings
        GREEN_RGB = RGBColor(34, 139, 34)
        
        
        PROGRAM_NAMES = {"JP": "Junior Primary", "PY": "Primary Years", "SY": "Senior Years"}
        
        doc = Document()
        
        # Set default font to Arial
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        style.element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
        
        # TITLE
        heading = doc.add_heading('Behaviour Analysis Plan', 0)
        for run in heading.runs:
            run.font.color.rgb = GREEN_RGB
            set_arial(run)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle = doc.add_paragraph('Evidence-Based Analysis & Recommendations')
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in subtitle.runs:
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(100, 116, 139)
        
        doc.add_paragraph()
        
        # Add analysis image
        try:
            # Create image inline
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.patches import FancyBboxPatch, Circle
            import numpy as np
            
            fig, ax = plt.subplots(figsize=(6, 3), dpi=150)
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 5)
            ax.axis('off')
            
            # Background
            ax.add_patch(FancyBboxPatch((0, 0), 10, 5, boxstyle="round,pad=0.1", 
                                        facecolor='#f8fafc', edgecolor='#e2e8f0', linewidth=2))
            
            # Bar chart
            bars_x = [1.5, 2.5, 3.5, 4.5, 5.5]
            bars_y = [2.5, 3.2, 2.8, 3.5, 3.0]
            for x, y in zip(bars_x, bars_y):
                ax.add_patch(plt.Rectangle((x-0.3, 0.5), 0.6, y-0.5, 
                                          facecolor='#3b82f6', alpha=0.7))
            
            # Trend line
            line_x = np.linspace(6.5, 9.5, 50)
            line_y = 1.5 + (line_x - 6.5) * 0.2
            ax.plot(line_x, line_y, color='#22c55e', linewidth=3, alpha=0.8)
            ax.scatter([6.5, 7.5, 8.5, 9.5], [1.5, 1.7, 2.1, 2.3], 
                      s=60, color='#22c55e', zorder=5, alpha=0.8)
            
            # Icons
            circle = Circle((1, 1.5), 0.4, facecolor='none', edgecolor='#0ea5e9', linewidth=3)
            ax.add_patch(circle)
            ax.plot([1.3, 1.6], [1.2, 0.9], color='#0ea5e9', linewidth=3)
            
            plt.tight_layout()
            
            img_stream = BytesIO()
            plt.savefig(img_stream, format='png', dpi=150, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            img_stream.seek(0)
            plt.close()
            
            # Add to document
            doc.add_picture(img_stream, width=Inches(5))
            last_paragraph = doc.paragraphs[-1]
            last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except:
            pass  # If image creation fails, continue without it
        
        doc.add_paragraph()
        branding = doc.add_paragraph('Prepared by: Learning and Behaviour Unit')
        branding.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in branding.runs:
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = RGBColor(14, 165, 233)
        
        doc.add_page_break()
        
        # STUDENT INFO
        heading = doc.add_heading('Student Information', 1)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        info_table = doc.add_table(rows=5, cols=2)
        info_table.style = 'Light Grid Accent 1'
        info_table.rows[0].cells[0].text = 'Student:'
        info_table.rows[0].cells[1].text = student['name']
        info_table.rows[1].cells[0].text = 'Program:'
        info_table.rows[1].cells[1].text = PROGRAM_NAMES.get(student['program'], student['program'])
        info_table.rows[2].cells[0].text = 'Grade:'
        info_table.rows[2].cells[1].text = student['grade']
        info_table.rows[3].cells[0].text = 'Analysis Date:'
        info_table.rows[3].cells[1].text = datetime.now().strftime('%d %B %Y')
        info_table.rows[4].cells[0].text = 'Data Period:'
        info_table.rows[4].cells[1].text = f"{full_df['date_parsed'].min().strftime('%d/%m/%Y')} - {full_df['date_parsed'].max().strftime('%d/%m/%Y')}"
        
        doc.add_paragraph()
        
        # SUMMARY
        heading = doc.add_heading('Executive Summary', 1)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        summary = doc.add_paragraph()
        summary.add_run('Total Incidents: ').bold = True
        summary.add_run(f"{len(full_df)}\n")
        summary.add_run('Critical Incidents: ').bold = True
        summary.add_run(f"{len(full_df[full_df['incident_type'] == 'Critical'])}\n")
        summary.add_run('Average Severity: ').bold = True
        summary.add_run(f"{full_df['severity'].mean():.2f}/5\n")
        summary.add_run('Risk Level: ').bold = True
        summary.add_run(f"{risk_level} ({risk_score}/100)")
        
        doc.add_paragraph()
        
        # FINDINGS
        heading = doc.add_heading('Key Findings', 1)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        findings = doc.add_paragraph()
        findings.add_run('Primary Behaviour: ').bold = True
        findings.add_run(f"{top_beh}\n\n")
        findings.add_run('Most Common Trigger: ').bold = True
        findings.add_run(f"{top_ant}\n\n")
        findings.add_run('Hotspot Location: ').bold = True
        findings.add_run(f"{top_loc}\n\n")
        findings.add_run('Peak Time: ').bold = True
        findings.add_run(f"{top_session}")
        
        doc.add_page_break()
        
        # GRAPHS WITH MATPLOTLIB
        heading = doc.add_heading('Visual Analytics', 1)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        doc.add_paragraph('The following graphs provide visual representation of incident patterns and trends.')
        
        plt.style.use('default')
        
        # GRAPH 1: Daily Frequency
        heading = doc.add_heading('1. Daily Incident Frequency', 2)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        daily = full_df.groupby(full_df["date_parsed"].dt.date).size().reset_index(name="count")
        fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
        ax.plot(daily["date_parsed"], daily["count"], marker='o', linewidth=2, markersize=5, color='#334155')
        ax.fill_between(daily["date_parsed"], daily["count"], alpha=0.2, color='#334155')
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax.set_ylabel('Incident Count', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        doc.add_picture(img_buffer, width=Inches(6))
        plt.close()
        doc.add_paragraph("Daily incident frequency shows temporal patterns.")
        doc.add_paragraph()
        
        # GRAPH 2: Behaviours
        heading = doc.add_heading('2. Most Common Behaviours', 2)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        beh_counts = full_df["behaviour_type"].value_counts().head(5)
        fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
        ax.barh(beh_counts.index, beh_counts.values, color='#334155')
        ax.set_xlabel('Frequency', fontsize=11, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for i, v in enumerate(beh_counts.values):
            ax.text(v + 0.5, i, str(v), va='center', fontweight='bold')
        plt.tight_layout()
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        doc.add_picture(img_buffer, width=Inches(6))
        plt.close()
        doc.add_paragraph(f"Primary: {beh_counts.index[0]} ({beh_counts.values[0]} incidents).")
        doc.add_paragraph()
        
        # GRAPH 3: Triggers
        heading = doc.add_heading('3. Most Common Triggers', 2)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        ant_counts = full_df["antecedent"].value_counts().head(5)
        fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
        ax.barh(ant_counts.index, ant_counts.values, color='#475569')
        ax.set_xlabel('Frequency', fontsize=11, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for i, v in enumerate(ant_counts.values):
            ax.text(v + 0.5, i, str(v), va='center', fontweight='bold')
        plt.tight_layout()
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        doc.add_picture(img_buffer, width=Inches(6))
        plt.close()
        doc.add_paragraph(f"Key trigger: {ant_counts.index[0]}.")
        doc.add_paragraph()
        
        # GRAPH 4: Severity
        heading = doc.add_heading('4. Severity Over Time', 2)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
        ax.scatter(full_df["date_parsed"], full_df["severity"], alpha=0.6, s=50, color='#334155')
        if len(full_df) >= 2:
            z = np.polyfit(range(len(full_df)), full_df["severity"], 1)
            p = np.poly1d(z)
            ax.plot(full_df["date_parsed"], p(range(len(full_df))), linestyle='--', linewidth=2, color='#94a3b8')
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax.set_ylabel('Severity', fontsize=11, fontweight='bold')
        ax.set_ylim(0, 6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        doc.add_picture(img_buffer, width=Inches(6))
        plt.close()
        doc.add_paragraph("Severity trend over time.")
        doc.add_paragraph()
        
        # GRAPH 5: Locations
        heading = doc.add_heading('5. Location Hotspots', 2)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        loc_counts = full_df["location"].value_counts().head(5)
        fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
        ax.barh(loc_counts.index, loc_counts.values, color='#64748b')
        ax.set_xlabel('Frequency', fontsize=11, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for i, v in enumerate(loc_counts.values):
            ax.text(v + 0.5, i, str(v), va='center', fontweight='bold')
        plt.tight_layout()
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        doc.add_picture(img_buffer, width=Inches(6))
        plt.close()
        doc.add_paragraph(f"Most incidents in: {loc_counts.index[0]}.")
        doc.add_paragraph()
        
        # GRAPH 6: Time
        heading = doc.add_heading('6. Time of Day Patterns', 2)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        session_counts = full_df["session"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
        ax.bar(session_counts.index, session_counts.values, color='#475569')
        ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for i, v in enumerate(session_counts.values):
            ax.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        plt.tight_layout()
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        doc.add_picture(img_buffer, width=Inches(6))
        plt.close()
        doc.add_paragraph(f"Peak time: {session_counts.index[0]}.")
        
        doc.add_page_break()
        
        # INTERPRETATION & RECOMMENDATIONS (same as before)
        heading = doc.add_heading('Clinical Interpretation', 1)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        doc.add_paragraph('Based on Applied Behaviour Analysis, Trauma-Informed Practice, Berry Street Education Model, and CPI principles.')
        
        interp = doc.add_paragraph()
        interp.add_run('Pattern Analysis: ').bold = True
        interp.add_run(f"{student['name']} is most vulnerable when '{top_ant}' occurs in {top_loc} during {top_session}. ")
        interp.add_run("This behaviour is communication and safety strategy.\n\n")
        interp.add_run('Berry Street Lens: ').bold = True
        interp.add_run("Focus on Body (regulation) and Relationship (connection) domains first. ")
        interp.add_run("Build foundation before expecting Engagement or Character development.\n\n")
        interp.add_run('CPI Alignment: ').bold = True
        interp.add_run("Supportive Stance, behaviour as communication, maintain dignity.")
        
        doc.add_paragraph()
        
        # DFE PROTECTIVE PRACTICES FRAMEWORK
        dfe_heading = doc.add_heading('DFE Protective Practices Framework', 1)
        for run in dfe_heading.runs:
            run.font.color.rgb = GREEN_RGB
            set_arial(run)
        
        dfe_intro = doc.add_paragraph("The Department for Education's Protective Practices Framework provides evidence-based approaches aligned with trauma-informed care and positive behaviour support. These six practices create safe, supportive environments that promote wellbeing and learning.")
        for run in dfe_intro.runs:
            set_arial(run)
        
        dfe_practices = doc.add_heading('Six Protective Practices', 2)
        for run in dfe_practices.runs:
            run.font.color.rgb = GREEN_RGB
            set_arial(run)
        
        # Practice 1
        prac1 = doc.add_paragraph()
        r1 = prac1.add_run('1. Strengthening Relationships: ')
        r1.bold = True
        set_arial(r1)
        r1b = prac1.add_run(f"Build predictable, safe relationships with {student['name']}. Key adult check-ins, relationship-building activities, and consistent routines form the foundation for all learning and behaviour support.\n\n")
        set_arial(r1b)
        
        # Practice 2
        prac2 = doc.add_paragraph()
        r2 = prac2.add_run('2. Promoting Inclusion: ')
        r2.bold = True
        set_arial(r2)
        r2b = prac2.add_run("Ensure meaningful access to curriculum and social opportunities with appropriate accommodations and modifications. Student belongs in learning spaces with peers.\n\n")
        set_arial(r2b)
        
        # Practice 3
        prac3 = doc.add_paragraph()
        r3 = prac3.add_run('3. Attuning to Need: ')
        r3.bold = True
        set_arial(r3)
        r3b = prac3.add_run(f"Recognize early warning signs when {student['name']} requires additional support. Pattern analysis shows particular vulnerability during {top_session} when '{top_ant}' occurs. Attunement prevents escalation.\n\n")
        set_arial(r3b)
        
        # Practice 4
        prac4 = doc.add_paragraph()
        r4 = prac4.add_run('4. Responding to Need: ')
        r4.bold = True
        set_arial(r4)
        r4b = prac4.add_run("Provide timely, appropriate responses using CPI principles, co-regulation, and Berry Street strategies. Early supportive intervention prevents crisis and maintains dignity.\n\n")
        set_arial(r4b)
        
        # Practice 5
        prac5 = doc.add_paragraph()
        r5 = prac5.add_run('5. Teaching Skills: ')
        r5.bold = True
        set_arial(r5)
        r5b = prac5.add_run("Explicitly teach replacement behaviours, coping strategies, and self-regulation skills. Link to Personal and Social Capability curriculum. Practice and reinforce new skills.\n\n")
        set_arial(r5b)
        
        # Practice 6
        prac6 = doc.add_paragraph()
        r6 = prac6.add_run('6. Supporting Recovery: ')
        r6.bold = True
        set_arial(r6)
        r6b = prac6.add_run("After incidents, support re-regulation and relationship repair through restorative practices. Recovery maintains connection and reinforces that behaviour is not identity.\n\n")
        set_arial(r6b)
        
        # Integration paragraph
        integration_heading = doc.add_heading('Integration with Current Plan', 2)
        for run in integration_heading.runs:
            run.font.color.rgb = GREEN_RGB
            set_arial(run)
        
        integration = doc.add_paragraph()
        ri1 = integration.add_run('Alignment: ')
        ri1.bold = True
        set_arial(ri1)
        ri2 = integration.add_run("This plan integrates DFE Protective Practices with Berry Street Education Model domains (Body, Relationship, Stamina, Engagement, Character), CPI crisis prevention principles, and trauma-informed approaches. All strategies prioritize relationship, safety, and skill-building before behavioural expectations. The protective practices framework underpins every recommendation in this plan.")
        set_arial(ri2)
        
        
        
        # WINDOW OF TOLERANCE FRAMEWORK
        wot_heading = doc.add_heading('Window of Tolerance Framework', 1)
        for run in wot_heading.runs:
            run.font.color.rgb = GREEN_RGB
            set_arial(run)
        
        wot_intro = doc.add_paragraph("The Window of Tolerance (Siegel, 1999; Ogden & Fisher, 2015) describes the optimal zone of arousal where students can process information, regulate emotions, and engage in learning. Understanding this framework is essential for trauma-informed behaviour support.")
        for run in wot_intro.runs:
            set_arial(run)
        
        doc.add_paragraph()
        
        # Three zones explanation
        zones_heading = doc.add_heading('Three Zones of Arousal', 2)
        for run in zones_heading.runs:
            run.font.color.rgb = GREEN_RGB
            set_arial(run)
        
        # Zone 1: Within Window
        zone1 = doc.add_paragraph()
        z1a = zone1.add_run('Within Window of Tolerance (Optimal Zone): ')
        z1a.bold = True
        set_arial(z1a)
        z1b = zone1.add_run(f"When {student['name']} is in their window, they can think clearly, regulate emotions, problem-solve, and access learning. Signs include: calm body, focused attention, able to follow instructions, receptive to support, can use coping strategies effectively.\n\n")
        set_arial(z1b)
        
        # Zone 2: Hyper-arousal
        zone2 = doc.add_paragraph()
        z2a = zone2.add_run('Above Window (Hyper-arousal/Fight-Flight): ')
        z2a.bold = True
        set_arial(z2a)
        z2b = zone2.add_run("When arousal is too high, the nervous system enters survival mode. The student may display: increased aggression, verbal outbursts, elopement, property destruction, inability to process verbal information, resistance to demands. The brain's 'thinking centre' goes offline - logic and reasoning are not accessible.\n\n")
        set_arial(z2b)
        
        # Zone 3: Hypo-arousal
        zone3 = doc.add_paragraph()
        z3a = zone3.add_run('Below Window (Hypo-arousal/Freeze-Shutdown): ')
        z3a.bold = True
        set_arial(z3a)
        z3b = zone3.add_run("When arousal drops too low, the student may appear: withdrawn, non-responsive, dissociated, physically immobile, unable to engage, 'shut down.' This is also a survival response and requires gentle support to re-regulate.\n\n")
        set_arial(z3b)
        
        doc.add_paragraph()
        
        # Application to this student
        application_heading = doc.add_heading('Application to Current Patterns', 2)
        for run in application_heading.runs:
            run.font.color.rgb = GREEN_RGB
            set_arial(run)
        
        application = doc.add_paragraph()
        app1 = application.add_run('Pattern Analysis: ')
        app1.bold = True
        set_arial(app1)
        app2 = application.add_run(f"Data shows {student['name']} is most vulnerable during {top_session} when '{top_ant}' occurs. These triggers appear to push the student outside their window of tolerance. Incidents in {top_loc} suggest this environment may contain additional stressors that narrow the window further.\n\n")
        set_arial(app2)
        
        app3 = application.add_run('Intervention Focus: ')
        app3.bold = True
        set_arial(app3)
        app4 = application.add_run("Strategies must focus on: (1) Widening the window through consistent regulation practice, (2) Recognizing early warning signs of dysregulation, (3) Co-regulating to bring student back into window before escalation, (4) Teaching student to recognize their own arousal states and use tools independently.\n\n")
        set_arial(app4)
        
        app5 = application.add_run('Research Base: ')
        app5.bold = True
        set_arial(app5)
        app6 = application.add_run("Polyvagal Theory (Porges, 2011) explains the autonomic nervous system's role in these responses. Trauma and chronic stress narrow the window. Consistent, predictable relationships and regulation supports gradually widen it. This is neurobiological - not behavioural choice.")
        set_arial(app6)
        
        doc.add_page_break()
        
        heading = doc.add_heading('Evidence-Based Recommendations', 1)
        for run in heading.runs:
            run.font.color.rgb = GREEN_RGB
            set_arial(run)
        
        heading = doc.add_heading('1. Body Domain (Regulation)', 2)

        for run in heading.runs:

            run.font.color.rgb = GREEN_RGB

            set_arial(run)
        doc.add_paragraph(f"• Regulated start before {top_session}", style='List Bullet')
        doc.add_paragraph(f"• Visual check-in before '{top_ant}'", style='List Bullet')
        doc.add_paragraph(f"• Environmental modification in {top_loc}", style='List Bullet')
        doc.add_paragraph("• Sensory regulation opportunities", style='List Bullet')
        
        heading = doc.add_heading('2. Relationship Domain (Connection)', 2)

        
        for run in heading.runs:

        
            run.font.color.rgb = GREEN_RGB

        
            set_arial(run)
        doc.add_paragraph("• Supportive Stance with low, slow voice", style='List Bullet')
        doc.add_paragraph("• One key adult maintains connection", style='List Bullet')
        doc.add_paragraph("• Acknowledge feelings", style='List Bullet')
        doc.add_paragraph("• Offer choices for control", style='List Bullet')
        
        heading = doc.add_heading('3. Stamina Domain (Persistence)', 2)

        
        for run in heading.runs:

        
            run.font.color.rgb = GREEN_RGB

        
            set_arial(run)
        doc.add_paragraph("• Teach help-seeking with visual cues", style='List Bullet')
        doc.add_paragraph("• Practice requesting breaks", style='List Bullet')
        doc.add_paragraph("• Emotional literacy skills", style='List Bullet')
        doc.add_paragraph("• Build coping strategies", style='List Bullet')
        
        heading = doc.add_heading('4. SMART Goal', 2)

        
        for run in heading.runs:

        
            run.font.color.rgb = GREEN_RGB

        
            set_arial(run)
        goal = doc.add_paragraph()
        goal.add_run('Measurable: ').bold = True
        goal.add_run("Over 5 weeks, use help-seeking strategy in 4/5 opportunities with support.")
        doc.add_paragraph()
        doc.add_paragraph('Review Date: ' + (datetime.now() + timedelta(weeks=5)).strftime('%d %B %Y'))
        
        doc.add_page_break()
        
        # FOOTER
        footer = doc.add_paragraph()
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer.add_run('\n\nLearning and Behaviour Unit\n')
        footer_run.font.size = Pt(10)
        footer_run.font.bold = True
        footer_run.font.color.rgb = RGBColor(14, 165, 233)
        
        footer2 = doc.add_paragraph()
        footer2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer2_run = footer2.add_run('Evidence-based: ABA, Trauma-Informed, Berry Street, CPI\n')
        footer2_run.font.size = Pt(9)
        footer2_run.font.color.rgb = RGBColor(100, 116, 139)
        
        footer3 = doc.add_paragraph()
        footer3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer3_run = footer3.add_run(datetime.now().strftime('%d %B %Y'))
        footer3_run.font.size = Pt(9)
        footer3_run.font.color.rgb = RGBColor(100, 116, 139)
        
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
        
    except Exception as e:
        import traceback
        st.error(f"BAP Error: {e}")
        st.error(traceback.format_exc())
        return None


# ============================================
# SUPABASE DATABASE FUNCTIONS
# ============================================

def hash_password(plain_password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def load_students_from_db():
    """Load students from Supabase database"""
    if not supabase:
        return MOCK_STUDENTS  # Fallback to mock data
    
    try:
        response = supabase.table('students').select('*').execute()
        students = []
        for row in response.data:
            students.append({
                "id": str(row['id']),
                "name": row['name'],
                "edid": row['edid'],
                "grade": row['grade'],
                "dob": row['dob'],
                "program": row['program'],
                "placement_start": row['placement_start'],
                "placement_end": row['placement_end']
            })
        return students  # Return empty list if no students in database
    except Exception as e:
        st.error(f"Error loading students: {e}")
        return []  # Return empty list on error

def save_student_to_db(student):
    """Save a student to Supabase database"""
    if not supabase:
        return False
    
    try:
        data = {
            "name": student['name'],
            "edid": student['edid'],
            "grade": student['grade'],
            "dob": student['dob'],
            "program": student['program'],
            "placement_start": student['placement_start'],
            "placement_end": student.get('placement_end')
        }
        
        if 'id' in student and student['id'].startswith('stu_'):
            # New student (generated ID from app)
            supabase.table('students').insert(data).execute()
        else:
            # Existing student (UUID from database)
            supabase.table('students').update(data).eq('id', student['id']).execute()
        return True
    except Exception as e:
        st.error(f"Error saving student: {e}")
        return False

def delete_student_from_db(student_id):
    """Delete a student from Supabase database"""
    if not supabase:
        return False
    
    try:
        supabase.table('students').delete().eq('id', student_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting student: {e}")
        return False

def load_staff_from_db():
    """Load staff from Supabase database"""
    if not supabase:
        return MOCK_STAFF
    
    try:
        response = supabase.table('staff').select('*').execute()
        staff = []
        for row in response.data:
            staff.append({
                "id": str(row['id']),
                "name": row['name'],
                "email": row['email'],
                "password": row.get('password'),  # Keep for backward compatibility
                "password_hash": row.get('password_hash', row.get('password')),  # Use password_hash if available
                "role": row['role'],
                "program": row.get('program'),
                "phone": row.get('phone'),
                "notes": row.get('notes'),
                "receive_critical_emails": row.get('receive_critical_emails', True),
                "created_date": row.get('created_at', '')[:10] if row.get('created_at') else None
            })
        return staff  # Return what we have from database
    except Exception as e:
        st.error(f"Error loading staff: {e}")
        return []  # Return empty list on error

def save_staff_to_db(staff_member):
    """Save a staff member to Supabase database"""
    if not supabase:
        return False
    
    try:
        data = {
            "name": staff_member['name'],
            "email": staff_member['email'],
            "password": staff_member['password'],
            "role": staff_member['role'],
            "program": staff_member.get('program'),
            "phone": staff_member.get('phone'),
            "notes": staff_member.get('notes'),
            "receive_critical_emails": staff_member.get('receive_critical_emails', True)
        }
        
        if 'id' in staff_member and staff_member['id'].startswith('staff_'):
            # New staff (generated ID from app)
            supabase.table('staff').insert(data).execute()
        else:
            # Existing staff (UUID from database)
            supabase.table('staff').update(data).eq('id', staff_member['id']).execute()
        return True
    except Exception as e:
        st.error(f"Error saving staff: {e}")
        return False

def delete_staff_from_db(staff_id):
    """Delete a staff member from Supabase database"""
    if not supabase:
        return False
    
    try:
        supabase.table('staff').delete().eq('id', staff_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting staff: {e}")
        return False

def load_incidents_from_db(student_id=None):
    """Load incidents from Supabase database"""
    if not supabase:
        return []
    
    try:
        query = supabase.table('incidents').select('*')
        if student_id:
            query = query.eq('student_id', student_id)
        response = query.execute()
        
        incidents = []
        for row in response.data:
            incidents.append({
                "id": str(row['id']),
                "student_id": str(row['student_id']),
                "date": row['date'],
                "time": row['time'],
                "day": row['day_of_week'],
                "session": row['session'],
                "location": row['location'],
                "behaviour_type": row['behaviour_type'],
                "antecedent": row['antecedent'],
                "intervention": row['intervention'],  # Already array in DB
                "severity": row['severity'],
                "reported_by": str(row['reported_by']) if row.get('reported_by') else None,
                "description": row.get('description', ''),
                "duration_minutes": row.get('duration_minutes'),
                "hypothesis_function": row.get('hypothesis_function'),
                "hypothesis_item": row.get('hypothesis_item'),
                "is_critical": row.get('is_critical', False)
            })
        return incidents
    except Exception as e:
        st.error(f"Error loading incidents: {e}")
        return []

def save_incident_to_db(incident):
    """Save an incident to Supabase database"""
    if not supabase:
        return False
    
    try:
        data = {
            "student_id": incident['student_id'],
            "date": incident['date'],
            "time": incident['time'],
            "day_of_week": incident['day'],
            "session": incident['session'],
            "location": incident['location'],
            "behaviour_type": incident['behaviour_type'],
            "antecedent": incident['antecedent'],
            "intervention": incident['intervention'],
            "severity": incident['severity'],
            "reported_by": incident.get('reported_by'),
            "description": incident.get('description', ''),
            "duration_minutes": incident.get('duration_minutes'),
            "hypothesis_function": incident.get('hypothesis_function'),
            "hypothesis_item": incident.get('hypothesis_item'),
            "is_critical": incident.get('is_critical', False)
        }
        
        if 'id' not in incident or not incident['id']:
            # New incident
            supabase.table('incidents').insert(data).execute()
        else:
            # Update existing
            supabase.table('incidents').update(data).eq('id', incident['id']).execute()
        return True
    except Exception as e:
        st.error(f"Error saving incident: {e}")
        return False

def load_critical_incidents_from_db(student_id=None):
    """Load critical incidents from Supabase database"""
    if not supabase:
        return []
    
    try:
        query = supabase.table('critical_incidents').select('*')
        if student_id:
            query = query.eq('student_id', student_id)
        response = query.execute()
        
        critical = []
        for row in response.data:
            critical.append({
                "id": str(row['id']),
                "student_id": str(row['student_id']),
                "severity": row['severity'],
                "reported_by": str(row['reported_by']) if row.get('reported_by') else None,
                "ABCH_primary": {
                    "location": row['primary_location'],
                    "context": row['primary_context'],
                    "time": row['primary_time'],
                    "behaviour": row['primary_behaviour'],
                    "consequence": row['primary_consequence'],
                    "hypothesis_function": row.get('primary_hypothesis_function'),
                    "hypothesis_item": row.get('primary_hypothesis_item')
                },
                "ABCH_additional": row.get('additional_entries', []),
                "outcomes": row['outcomes'],
                "sapol_reference": row.get('sapol_reference'),
                "admin_summary": row.get('admin_summary'),
                "created_at": row.get('created_at')
            })
        return critical
    except Exception as e:
        st.error(f"Error loading critical incidents: {e}")
        return []

def save_critical_incident_to_db(critical):
    """Save a critical incident to Supabase database"""
    if not supabase:
        return False
    
    try:
        primary = critical.get('ABCH_primary', {})
        data = {
            "student_id": critical['student_id'],
            "severity": critical['severity'],
            "reported_by": critical.get('reported_by'),
            "primary_location": primary.get('location', ''),
            "primary_context": primary.get('context', ''),
            "primary_time": primary.get('time', ''),
            "primary_behaviour": primary.get('behaviour', ''),
            "primary_consequence": primary.get('consequence', ''),
            "primary_hypothesis_function": primary.get('hypothesis_function'),
            "primary_hypothesis_item": primary.get('hypothesis_item'),
            "additional_entries": critical.get('ABCH_additional', []),
            "outcomes": critical.get('outcomes', []),
            "sapol_reference": critical.get('sapol_reference'),
            "admin_summary": critical.get('admin_summary')
        }
        
        if 'id' not in critical or not critical['id']:
            # New critical incident
            supabase.table('critical_incidents').insert(data).execute()
        else:
            # Update existing
            supabase.table('critical_incidents').update(data).eq('id', critical['id']).execute()
        return True
    except Exception as e:
        st.error(f"Error saving critical incident: {e}")
        return False


def init_state():
    ss = st.session_state
    if "logged_in" not in ss: ss.logged_in = False
    if "current_user" not in ss: ss.current_user = None
    if "current_page" not in ss: ss.current_page = "login"
    
    # Load from Supabase if available, otherwise use mock data
    if "students" not in ss: 
        ss.students = load_students_from_db() if supabase else MOCK_STUDENTS
    if "staff" not in ss: 
        ss.staff = load_staff_from_db() if supabase else MOCK_STAFF
    if "incidents" not in ss: 
        ss.incidents = load_incidents_from_db() if supabase else generate_mock_incidents(70)
    if "critical_incidents" not in ss: 
        ss.critical_incidents = load_critical_incidents_from_db() if supabase else []
    
    if "selected_program" not in ss: ss.selected_program = "JP"
    if "selected_student_id" not in ss: ss.selected_student_id = None
    if "current_incident_id" not in ss: ss.current_incident_id = None
    if "abch_rows" not in ss: ss.abch_rows = []
    if "show_critical_prompt" not in ss: ss.show_critical_prompt = False

def login_user(email: str, password: str) -> bool:
    """Login user with bcrypt password verification"""
    email = (email or "").strip().lower()
    password = (password or "").strip()
    if not email or not password: 
        return False
    
    for staff in st.session_state.staff:
        if staff.get("email", "").lower() == email:
            # Get the stored hash
            stored_hash = staff.get("password_hash", "")
            if not stored_hash:
                continue
            
            # Verify password against bcrypt hash
            try:
                # Handle both string and bytes
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')
                if isinstance(password, str):
                    password_bytes = password.encode('utf-8')
                
                if bcrypt.checkpw(password_bytes, stored_hash):
                    st.session_state.logged_in = True
                    st.session_state.current_user = staff
                    st.session_state.current_page = "landing"
                    return True
            except Exception as e:
                # If bcrypt fails, try plain text comparison as fallback (for migration)
                if staff.get("password") == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = staff
                    st.session_state.current_page = "landing"
                    return True
                continue
    
    return False

def go_to(page: str, **kwargs):
    if page not in VALID_PAGES: return
    st.session_state.current_page = page
    for k, v in kwargs.items():
        setattr(st.session_state, k, v)
    st.rerun()

def get_student(sid): 
    return next((s for s in st.session_state.students if s["id"] == sid), None)

def get_session_from_time(t): 
    return "Morning" if t.hour < 11 else "Middle" if t.hour < 13 else "Afternoon"

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
            "antecedent": random.choice(ANTECEDENTS), 
            "intervention": [random.choice(INTERVENTIONS)],  # Changed to list
            "severity": sev, "reported_by": random.choice(MOCK_STAFF)["name"],
            "description": "Mock incident", "is_critical": sev >= 3, "duration_minutes": random.randint(2, 25)
        })
    return incidents

# PAGES
def render_login_page():
    st.markdown("## 🔐 Staff Login")
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
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.current_page = "login"
            st.rerun()
    
    # Admin portal button for admin users
    if st.session_state.current_user.get("role") == "ADM":
        st.markdown("---")
        if st.button("🔧 Admin Portal", use_container_width=True, key="goto_admin"):
            go_to("admin_portal")
    
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
    
    col1, col2 = st.columns([6, 1])
    with col1:
        if st.button("⬅ Back to Landing", key="back_students"):
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
    
    # Navigation buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("⬅ Back to Students", key="back_log_top"):
            go_to("program_students", selected_program=student["program"])
    with col2:
        if st.button("🏠 Program Landing", key="home_log"):
            go_to("landing")
    
    show_severity_guide()
    
    # Check if critical form is required
    if st.session_state.show_critical_prompt:
        inc_info = st.session_state.get("last_incident_info", {})
        if inc_info.get("severity", 0) >= 3:
            st.error(f"⚠️ **Severity {inc_info['severity']} Detected** - Critical Incident ABCH Form Required")
        else:
            st.error("⚠️ **Critical Incident Flagged** - Critical Incident ABCH Form Required")
        st.info("Please complete the Critical Incident ABCH form to document this event fully.")
        
        # Only one button - REMOVED "Skip for Now"
        if st.button("📋 Complete Critical Form Now", type="primary", key="crit_now", use_container_width=True):
            st.session_state.show_critical_prompt = False
            go_to("critical_incident", current_incident_id=st.session_state.current_incident_id)
        st.markdown("---")
        st.stop()
    
    # INCIDENT FORM
    with st.form("incident_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            inc_date = st.date_input("Date *", date.today(), key="inc_date")
            inc_time = st.time_input("Time *", datetime.now().time(), key="inc_time")
            location = st.selectbox("Location *", [""] + LOCATIONS, key="inc_loc")
        with col2:
            behaviour = st.selectbox("Behaviour Type *", [""] + BEHAVIOUR_TYPES, key="inc_beh")
            antecedent = st.selectbox("Antecedent/Trigger *", [""] + ANTECEDENTS, key="inc_ant")
            # MULTIPLE INTERVENTIONS
            interventions = st.multiselect("Interventions Used *", INTERVENTIONS, key="inc_ints")
        
        duration = st.number_input("Duration (minutes) *", min_value=1, value=1, key="inc_dur")
        severity = st.slider("Severity Level (from start to end of incident) *", 1, 5, 1, key="inc_sev")
        description = st.text_area("Brief Description (Optional)", placeholder="Factual, objective description...", key="inc_desc")
        manual_critical = st.checkbox("This incident requires a Critical Incident ABCH Form (regardless of severity)", key="manual_crit")
        submitted = st.form_submit_button("Submit Incident", type="primary")
    
    if submitted:
        if not location or not behaviour or not antecedent or not interventions:
            st.error("Please complete all required fields marked with *")
        else:
            new_id = str(uuid.uuid4())
            is_critical = (severity >= 3) or manual_critical
            rec = {
                "id": new_id, "student_id": student_id, "student_name": student["name"],
                "date": inc_date.isoformat(), "time": inc_time.strftime("%H:%M:%S"),
                "day": inc_date.strftime("%A"), "session": get_session_from_time(inc_time),
                "location": location, "behaviour_type": behaviour, "antecedent": antecedent,
                "intervention": interventions,  # Save as list
                "severity": severity,
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
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("↩️ Back to Students", key="back_after_log"):
                        go_to("program_students", selected_program=student["program"])
                with col2:
                    if st.button("🏠 Program Landing", key="home_after_log"):
                        go_to("landing")


def render_critical_incident_page():
    """Critical Incident Form with Police Reference and Improved Labels"""
    inc_id = st.session_state.get("current_incident_id")
    quick_inc = next((i for i in st.session_state.incidents if i["id"] == inc_id), None)
    
    if not quick_inc:
        st.error("No incident found")
        return
    
    student = get_student(quick_inc["student_id"])
    st.markdown(f"## 🚨 Critical Incident ABCH Form")
    
    # Navigation
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("⬅ Back to Students", key="back_crit_top"):
            go_to("program_students", selected_program=student["program"])
    with col2:
        if st.button("🏠 Program Landing", key="home_crit"):
            go_to("landing")
    
    st.markdown("### Incident Details (from Quick Log)")
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**Student:** {student['name']}")
            st.markdown(f"**Grade:** {student['grade']}")
        with col2:
            st.markdown(f"**Date:** {quick_inc['date']}")
            st.markdown(f"**Time:** {format_time_12hr(quick_inc['time'])}")
        with col3:
            st.markdown(f"**Location:** {quick_inc['location']}")
            st.markdown(f"**Session:** {quick_inc['session']}")
        with col4:
            st.markdown(f"**Severity:** {quick_inc['severity']}")
            st.markdown(f"**Behaviour:** {quick_inc['behaviour_type']}")
    
    st.markdown("---")
    st.markdown("### ABCH Chronology")
    st.caption("Document the sequence of events. Add continuation entries if incident was prolonged.")
    
    if "abch_rows" not in st.session_state:
        st.session_state.abch_rows = []
    
    # PRIMARY ROW
    st.markdown("#### Initial Incident")
    col_header = st.columns([2, 2, 2, 2, 2])
    with col_header[0]: st.markdown("**ANTECEDENT (Triggers)**")
    with col_header[2]: st.markdown("**BEHAVIOUR**")
    with col_header[4]: st.markdown("**CONSEQUENCES**")
    
    col_subheader = st.columns([1, 1, 1, 1, 2, 2])
    with col_subheader[0]: st.caption("Location")
    with col_subheader[1]: st.caption("Context (what was happening?)")
    with col_subheader[2]: st.caption("Time")
    with col_subheader[3]: st.caption("Observed Behaviour")
    with col_subheader[4]: st.caption("What happened after?")
    with col_subheader[5]: st.caption("HYPOTHESIS (Function)")
    
    col_inputs1 = st.columns([1, 1, 1, 1, 2, 2])
    
    with col_inputs1[0]:
        location_1 = st.text_input("", value=quick_inc['location'], key="loc_1", label_visibility="collapsed")
    with col_inputs1[1]:
        context_1 = st.text_area("", placeholder="What was going on before?", 
                                key="context_1", height=100, label_visibility="collapsed")
    with col_inputs1[2]:
        time_1 = st.text_input("", value=format_time_12hr(quick_inc['time']), key="time_1", label_visibility="collapsed")
    with col_inputs1[3]:
        behaviour_1 = st.text_area("", placeholder="What did student do?", 
                                  key="behaviour_1", height=100, label_visibility="collapsed")
    with col_inputs1[4]:
        consequence_1 = st.text_area("", placeholder="Staff response? Student reaction?", 
                                    key="consequence_1", height=100, label_visibility="collapsed")
    with col_inputs1[5]:
        if "hyp_1_generated" not in st.session_state:
            st.session_state.hyp_1_generated = False
        if not st.session_state.hyp_1_generated and context_1 and behaviour_1:
            auto_hyp = generate_hypothesis(context_1, behaviour_1, consequence_1)
            st.session_state.hyp_1_auto = auto_hyp
            st.session_state.hyp_1_generated = True
        hypothesis_1 = st.text_area("", 
                                    value=st.session_state.get("hyp_1_auto", ""),
                                    placeholder="Auto-generated (editable)", 
                                    key="hypothesis_1", height=100, label_visibility="collapsed")
    
    st.markdown("---")
    
    if st.button("➕ Add Continuation Entry", key="add_abch_row"):
        st.session_state.abch_rows.append({})
        st.rerun()
    
    # ADDITIONAL ROWS - Changed labels
    for idx, row in enumerate(st.session_state.abch_rows):
        st.markdown(f"#### Continuation Entry {idx + 1}")
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
            if row.get("context") and row.get("behaviour"):
                auto_hyp_add = generate_hypothesis(row["context"], row["behaviour"], row.get("consequence", ""))
                row["hypothesis"] = st.text_area("", value=auto_hyp_add, key=f"hypothesis_{idx+2}", height=100, label_visibility="collapsed")
            else:
                row["hypothesis"] = st.text_area("", key=f"hypothesis_{idx+2}", height=100, label_visibility="collapsed")
        st.markdown("---")
    
    # INTENDED OUTCOMES with SAPOL reference field
    st.markdown("### Intended Outcomes")
    outcomes_options = [
        "Send Home", "Parent/Caregiver notified via Phone Call",
        "Student Leaving supervised areas/leaving school grounds",
        "Sexualised behaviour", "Incident – student to student",
        "Complaint by co-located school/member of public",
        "Property damage", "Stealing", "Toileting issue",
        "ED155: Staff Injury", "ED155: Student injury",
        "Emergency services - SAPOL",
        "Emergency services - SA Ambulance",
        "Incident Internally Managed - Restorative Session",
        "Incident Internally Managed - Community Service",
        "Incident Internally Managed - Re-Entry",
        "Incident Internally Managed - Case Review",
        "Incident Internally Managed - Make-up Time"
    ]
    
    selected_outcomes = st.multiselect("Select all intended outcomes:", outcomes_options, key="intended_outcomes")
    
    # SAPOL Reference Field - triggered if SAPOL selected
    sapol_reference = ""
    if "Emergency services - SAPOL" in selected_outcomes:
        st.warning("⚠️ SAPOL involvement detected - Police Reference Number required")
        sapol_reference = st.text_input("SAPOL Police Reference Number *", 
                                       placeholder="Enter police reference number",
                                       key="sapol_ref")
    
    tac_notes = st.text_area("Additional Outcome Notes (e.g., TAC meeting):", 
                            placeholder="A TAC meeting will be held...",
                            key="tac_notes", height=100)
    
    st.markdown("---")
    st.markdown("### Notifications & Administration")
    col_notif1, col_notif2 = st.columns(2)
    with col_notif1:
        notified_line_manager = st.checkbox("Notified Line Manager", key="notif_manager", value=True)
        notified_parent = st.checkbox("Notified Parent/Caregiver", key="notif_parent")
    with col_notif2:
        copy_in_file = st.checkbox("Copy in student file", key="copy_file", value=True)
        safety_plan_review = st.checkbox("Safety plan review required", key="safety_review")
    
    st.markdown("---")
    st.markdown("### Staff Agreement")
    staff_name = st.session_state.current_user.get("name", "Staff Member")
    st.markdown(f"**Completing Staff Member:** {staff_name}")
    staff_agrees = st.checkbox(f"✓ I, {staff_name}, confirm this information is accurate and complete.", 
                               key="staff_agrees")
    
    st.markdown("---")
    st.markdown("### Email Distribution")
    col_email1, col_email2 = st.columns(2)
    with col_email1:
        leader_email = st.text_input("Line Manager Email *", 
                                     value="manager@clc.sa.edu.au",
                                     key="leader_email")
    with col_email2:
        admin_email = st.text_input("Admin Email *", 
                                    value="admin@clc.sa.edu.au",
                                    key="admin_email")
    
    st.markdown("---")
    
    if st.button("📧 Submit Critical Incident Form", type="primary", use_container_width=True, key="save_crit"):
        # Validation
        errors = []
        if not context_1 or not behaviour_1 or not consequence_1 or not hypothesis_1:
            errors.append("Please complete all ABCH fields for initial incident")
        if not staff_agrees:
            errors.append("Please confirm your agreement")
        if not leader_email or "@" not in leader_email or not admin_email or "@" not in admin_email:
            errors.append("Please enter valid email addresses")
        if "Emergency services - SAPOL" in selected_outcomes and not sapol_reference:
            errors.append("SAPOL Reference Number is required when SAPOL is involved")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            record = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
                "quick_incident_id": inc_id,
                "student_id": quick_inc["student_id"],
                "student_name": student["name"],
                "incident_type": "Critical",
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
                "sapol_reference": sapol_reference if sapol_reference else None,
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
                "leader_email": leader_email,
                "admin_email": admin_email
            }
            
            st.session_state.critical_incidents.append(record)
            st.session_state.abch_rows = []
            st.session_state.hyp_1_generated = False
            
            st.success("✅ Critical incident form saved to database")
            
            # GENERATE ADMIN SUMMARY
            admin_summary = generate_admin_summary(record, student, staff_name)
            
            # Show admin summary
            with st.expander("📋 ADMIN SUMMARY (For External Incident Log)", expanded=True):
                st.text_area("Copy this summary for departmental log:", admin_summary, height=400, key="admin_summary_display")
                st.download_button(
                    "📥 Download Admin Summary",
                    admin_summary,
                    file_name=f"Admin_Summary_{student['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            
            # SEND EMAILS
            staff_email = st.session_state.current_user.get("email", "staff@example.com")
            send_critical_incident_email(record, student, staff_email, leader_email, admin_email)
            
            st.markdown("---")
            st.info("✉️ Emails sent to Line Manager, Admin, and completing staff member")
            st.info("💾 Critical incident data saved in student's file")
            st.info("📋 Admin summary generated for external log")
            if sapol_reference:
                st.info(f"🚔 SAPOL Reference: {sapol_reference}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 View Analysis", type="primary", use_container_width=True, key="view_analysis"):
                    go_to("student_analysis", selected_student_id=quick_inc["student_id"])
            with col2:
                if st.button("↩️ Back to Students", use_container_width=True, key="back_crit_after"):
                    go_to("program_students", selected_program=student["program"])
            with col3:
                if st.button("🏠 Program Landing", use_container_width=True, key="home_crit_after"):
                    go_to("landing")


def render_student_analysis_page():
    """Comprehensive Data Analysis with Berry Street Education Model"""
    student_id = st.session_state.get("selected_student_id")
    student = get_student(student_id)
    if not student:
        st.error("No student selected")
        return
    
    st.markdown(f"## 📊 Comprehensive Behaviour Analysis — {student['name']}")
    st.caption("Evidence-based analysis prepared by Learning and Behaviour Unit")
    st.caption("Using ABA, Trauma-Informed Practice, Berry Street Education Model, and CPI principles")
    
    # Display placement information
    if student.get('placement_start'):
        try:
            start_dt = datetime.fromisoformat(student['placement_start'])
            if student.get('placement_end'):
                end_dt = datetime.fromisoformat(student['placement_end'])
                status_txt = "Completed"
            else:
                end_dt = datetime.now()
                status_txt = "Ongoing"
            
            days_enrolled = (end_dt.date() - start_dt.date()).days
            
            st.markdown("---")
            pcol1, pcol2, pcol3 = st.columns(3)
            with pcol1:
                st.metric("Placement Start", start_dt.strftime('%d/%m/%Y'))
            with pcol2:
                if student.get('placement_end'):
                    st.metric("Placement End", datetime.fromisoformat(student['placement_end']).strftime('%d/%m/%Y'))
                else:
                    st.metric("Status", status_txt)
            with pcol3:
                st.metric("Days Enrolled", days_enrolled)
            st.markdown("---")
        except:
            pass
    
    # Navigation
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("⬅ Back to Students", key="back_analysis_top"):
            go_to("program_students", selected_program=student["program"])
    with col2:
        if st.button("🏠 Program Landing", key="home_analysis"):
            go_to("landing")
    
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
        # Handle intervention as list
        if "intervention" in quick_df.columns:
            quick_df["intervention_str"] = quick_df["intervention"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
    
    if not crit_df.empty:
        crit_df["incident_type"] = "Critical"
        crit_df["date_parsed"] = pd.to_datetime(crit_df.get("created_at", datetime.now().isoformat()))
        crit_df["severity"] = 5
        crit_df["antecedent"] = crit_df["ABCH_primary"].apply(lambda d: d.get("context","") if isinstance(d, dict) else "")
        crit_df["behaviour_type"] = crit_df["ABCH_primary"].apply(lambda d: d.get("behaviour","") if isinstance(d, dict) else "")
    
    full_df = pd.concat([quick_df, crit_df], ignore_index=True).sort_values("date_parsed")
    full_df["hour"] = pd.to_datetime(full_df["time"], format="%H:%M:%S", errors="coerce").dt.hour
    full_df["day_of_week"] = full_df["date_parsed"].dt.day_name()
    
    # OVERVIEW
    st.markdown("### 📈 Executive Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Total", len(full_df))
    with col2: st.metric("Critical", len(full_df[full_df["incident_type"] == "Critical"]))
    with col3: st.metric("Avg Severity", f"{full_df['severity'].mean():.1f}")
    with col4:
        days = max((full_df["date_parsed"].max() - full_df["date_parsed"].min()).days, 1)
        st.metric("Days Span", days)
    with col5:
        st.metric("Per Day", f"{len(full_df) / days:.1f}")
    
    st.markdown("---")
    
    # GRAPH 1: Daily Frequency
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
        height=280, showlegend=False, xaxis_title="Date", yaxis_title="Total",
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#334155', size=11),
        yaxis=dict(tickmode='linear', tick0=0, dtick=1)
    )
    st.plotly_chart(fig1, use_container_width=True)
    with st.expander("💡 Clinical Interpretation (Berry Street Body Domain)"):
        st.markdown("**Pattern Recognition:** Look for patterns (e.g., Mondays, after breaks). " +
                   "**Berry Street Body:** Schedule extra regulation supports during high-frequency periods - breathing, movement breaks, sensory activities. " +
                   "Increasing frequency may indicate student's nervous system is dysregulated and needs Body domain strategies.")
    st.markdown("---")
    
    # GRAPH 2: Top Behaviours
    st.markdown("### 🎯 Most Common Behaviours")
    beh_counts = full_df["behaviour_type"].value_counts().head(5)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=beh_counts.index, x=beh_counts.values,
        orientation='h', marker=dict(color='#475569'),
        text=beh_counts.values, textposition='outside'
    ))
    fig2.update_layout(
        height=280, showlegend=False, xaxis_title="Total",
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#334155', size=11),
        xaxis=dict(tickmode='linear', tick0=0, dtick=1)
    )
    st.plotly_chart(fig2, use_container_width=True)
    with st.expander("💡 Clinical Interpretation (Behaviour as Communication)"):
        st.markdown(f"**Primary:** {beh_counts.index[0]} ({beh_counts.values[0]} incidents). " +
                   "**Behaviour Analysis:** Focus intervention planning on top 2-3 behaviours. " +
                   "**Berry Street:** Behaviours are communication - what is student trying to tell us? Strengthen Relationship domain through connection.")
    st.markdown("---")
    
    # GRAPH 3: Top Triggers
    st.markdown("### 🔍 Most Common Triggers (Antecedents)")
    ant_counts = full_df["antecedent"].value_counts().head(5)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        y=ant_counts.index, x=ant_counts.values,
        orientation='h', marker=dict(color='#64748b'),
        text=ant_counts.values, textposition='outside'
    ))
    fig3.update_layout(
        height=280, showlegend=False, xaxis_title="Total",
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#334155', size=11)
    )
    st.plotly_chart(fig3, use_container_width=True)
    with st.expander("💡 Clinical Interpretation (Proactive Strategies)"):
        st.markdown(f"**Key trigger:** {ant_counts.index[0]}. " +
                   "**Behaviour Analysis:** Plan proactive supports before this occurs - antecedent manipulation is most effective prevention. " +
                   "**Berry Street Stamina:** Build student's capacity to persist through challenging moments.")
    st.markdown("---")
    
    # GRAPH 4: Severity Trend
    st.markdown("### 📊 Severity Over Time")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=full_df["date_parsed"], y=full_df["severity"],
        mode='markers', marker=dict(size=8, color='#334155', opacity=0.6)
    ))
    if len(full_df) >= 2:
        z = np.polyfit(range(len(full_df)), full_df["severity"], 1)
        p = np.poly1d(z)
        fig4.add_trace(go.Scatter(
            x=full_df["date_parsed"], y=p(range(len(full_df))),
            mode='lines', line=dict(color='#94a3b8', width=2, dash='dash'),
            name='Trend'
        ))
    fig4.update_layout(
        height=280, yaxis=dict(range=[0, 6]), xaxis_title="Date", yaxis_title="Severity",
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#334155', size=11)
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    trend_dir = "increasing" if len(full_df) >= 2 and full_df.tail(5)["severity"].mean() > full_df.head(5)["severity"].mean() else "decreasing"
    with st.expander("💡 Clinical Interpretation (Progress Monitoring)"):
        st.markdown(f"Severity appears **{trend_dir}** over time. " +
                   ("**Action Required:** Review strategies - may need stronger Body and Relationship supports. " if trend_dir == "increasing" 
                    else "**Positive Progress:** Current Berry Street strategies showing effect. Continue Body and Relationship focus. ") +
                   "Monitor for plateaus which may indicate need for strategy adjustment or focus on Engagement domain.")
    st.markdown("---")
    
    # GRAPH 5: Location Hotspots
    st.markdown("### 📍 Location Hotspots")
    loc_counts = full_df["location"].value_counts().head(5)
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        y=loc_counts.index, x=loc_counts.values,
        orientation='h', marker=dict(color='#64748b'),
        text=loc_counts.values, textposition='outside'
    ))
    fig5.update_layout(
        height=280, showlegend=False, xaxis_title="Total",
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#334155', size=11)
    )
    st.plotly_chart(fig5, use_container_width=True)
    with st.expander("💡 Clinical Interpretation (Environmental Strategies)"):
        st.markdown(f"Most incidents in **{loc_counts.index[0]}**. " +
                   "Consider: environmental modifications (lighting, noise, space), increased staff support, " +
                   "**Berry Street Body:** sensory-friendly adjustments, calming spaces, visual supports.")
    st.markdown("---")
    
    # GRAPH 6: Time of Day
    st.markdown("### ⏰ Time of Day Patterns")
    session_counts = full_df["session"].value_counts()
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(
        x=session_counts.index, y=session_counts.values,
        marker=dict(color='#475569'),
        text=session_counts.values, textposition='outside'
    ))
    fig6.update_layout(
        height=280, showlegend=False, yaxis_title="Total",
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#334155', size=11)
    )
    st.plotly_chart(fig6, use_container_width=True)
    with st.expander("💡 Clinical Interpretation (Regulation Timing)"):
        st.markdown(f"Peak time: **{session_counts.index[0]}**. " +
                   "**Berry Street Body:** Provide proactive regulation before this period - breathing exercises, movement breaks, sensory check-ins. " +
                   "Build student's self-regulation capacity through predictable regulation routines.")
    st.markdown("---")

    
    # QUICK VS CRITICAL COMPARISON SECTION
    st.markdown("## 📊 Quick vs Critical Incident Analysis")
    st.caption("Understanding the relationship between quick logs and critical incidents helps identify escalation patterns")
    
    # Separate quick and critical incidents
    quick_only = [i for i in quick if not i.get("is_critical")]
    critical_data = crit
    
    col_q, col_c = st.columns(2)
    with col_q:
        st.metric("Quick Incidents", len(quick_only), help="Standard behaviour logs (Severity 1-2)")
    with col_c:
        st.metric("Critical Incidents", len(critical_data), help="Severity 3+ requiring ABCH form")
    
    st.markdown("---")
    
    # COMPARISON GRAPH 1: Frequency over time
    st.markdown("### 📈 Incident Type Over Time")
    
    if len(quick_only) > 0 or len(critical_data) > 0:
        fig_comp1 = go.Figure()
        
        # Quick incidents line
        if len(quick_only) > 0:
            quick_df_temp = pd.DataFrame(quick_only)
            quick_df_temp["date_parsed"] = pd.to_datetime(quick_df_temp["date"])
            quick_daily = quick_df_temp.groupby(quick_df_temp["date_parsed"].dt.date).size().reset_index(name="count")
            fig_comp1.add_trace(go.Scatter(
                x=quick_daily["date_parsed"], y=quick_daily["count"],
                mode='lines+markers', name='Quick Incidents',
                line=dict(color='#3b82f6', width=2),
                marker=dict(size=6, color='#3b82f6')
            ))
        
        # Critical incidents line
        if len(critical_data) > 0:
            crit_dates = []
            for c in critical_data:
                date_str = c.get("created_at", c.get("date", datetime.now().isoformat()))
                try:
                    crit_dates.append(datetime.fromisoformat(date_str).date())
                except:
                    pass
            
            if crit_dates:
                crit_df_temp = pd.DataFrame({"date": crit_dates})
                crit_daily = crit_df_temp.groupby("date").size().reset_index(name="count")
                fig_comp1.add_trace(go.Scatter(
                    x=crit_daily["date"], y=crit_daily["count"],
                    mode='lines+markers', name='Critical Incidents',
                    line=dict(color='#ef4444', width=2),
                    marker=dict(size=6, color='#ef4444')
                ))
        
        fig_comp1.update_layout(
            height=300, xaxis_title="Date", yaxis_title="Total",
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(color='#334155', size=11),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(tickmode='linear', tick0=0, dtick=1)
        )
        st.plotly_chart(fig_comp1, use_container_width=True)
        
        with st.expander("💡 Clinical Interpretation (Window of Tolerance)"):
            st.markdown("**Pattern Recognition:** Increasing critical incidents suggest student spending more time outside Window of Tolerance. " +
                       "**Window of Tolerance:** Critical incidents indicate hyper-arousal (fight/flight) or hypo-arousal (shutdown). " +
                       "Focus on widening window through consistent co-regulation.")
    
    st.markdown("---")
    
    # COMPARISON GRAPH 2: Severity distribution
    st.markdown("### 📊 Severity Distribution")
    
    if len(quick_only) > 0:
        quick_sev = pd.DataFrame(quick_only)["severity"].value_counts().sort_index()
        crit_sev_counts = [0] * 5
        for c in critical_data:
            sev = c.get("severity", 3)
            if 1 <= sev <= 5:
                crit_sev_counts[sev-1] += 1
        
        fig_sev = go.Figure()
        fig_sev.add_trace(go.Bar(
            x=list(range(1, 6)), y=[quick_sev.get(i, 0) for i in range(1, 6)],
            name='Quick Incidents', marker=dict(color='#3b82f6'),
            text=[quick_sev.get(i, 0) for i in range(1, 6)], textposition='outside'
        ))
        fig_sev.add_trace(go.Bar(
            x=list(range(1, 6)), y=crit_sev_counts,
            name='Critical Incidents', marker=dict(color='#ef4444'),
            text=crit_sev_counts, textposition='outside'
        ))
        
        fig_sev.update_layout(
            height=300, xaxis_title="Severity Level", yaxis_title="Total",
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(color='#334155', size=11), barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(tickmode='linear', tick0=1, dtick=1),
            yaxis=dict(tickmode='linear', tick0=0, dtick=1)
        )
        st.plotly_chart(fig_sev, use_container_width=True)
        
        with st.expander("💡 Clinical Interpretation (Arousal States)"):
            st.markdown("**Severity 1-2:** Student within/near window - accessible to support. " +
                       "**Severity 3+:** Outside window - in survival mode. " +
                       "**Goal:** Intervene at 1-2 before leaving window. Co-regulation most effective when thinking brain still accessible.")
    
    st.markdown("---")
    
    # GRAPH 7-10 and rest of analysis...
    st.markdown("### 📆 Day of Week Patterns")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = full_df["day_of_week"].value_counts().reindex(day_order, fill_value=0)
    fig7 = go.Figure()
    fig7.add_trace(go.Bar(
        x=day_counts.index, y=day_counts.values,
        marker=dict(color='#64748b'),
        text=day_counts.values, textposition='outside'
    ))
    fig7.update_layout(
        height=280, showlegend=False, yaxis_title="Total",
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#334155', size=11)
    )
    st.plotly_chart(fig7, use_container_width=True)
    
    high_day = day_counts.idxmax()
    with st.expander("💡 Clinical Interpretation (Berry Street Relationship)"):
        st.markdown(f"**{high_day}** has most incidents. Consider connection routines: Monday welcome/check-in, Friday regulation support. " +
                   "**Berry Street Relationship:** Strong connections reduce incidents. Pattern may indicate when student needs extra relational support.")
    st.markdown("---")
    
    # CLINICAL SUMMARY with Berry Street
    st.markdown("### 🧠 Clinical Summary")
    st.caption("Evidence-based interpretation using ABA, Trauma-Informed Practice, Berry Street Education Model, and CPI principles")
    
    top_beh = full_df["behaviour_type"].mode()[0] if len(full_df) > 0 else "Unknown"
    top_ant = full_df["antecedent"].mode()[0] if len(full_df) > 0 else "Unknown"
    top_loc = full_df["location"].mode()[0] if len(full_df) > 0 else "Unknown"
    top_session = full_df["session"].mode()[0] if len(full_df) > 0 else "Unknown"
    
    # Calculate risk score
    recent = full_df.tail(7)
    risk_score = min(100, int(
        (len(recent) / 7 * 10) +
        (recent["severity"].mean() * 8) +
        (len(full_df[full_df["incident_type"] == "Critical"]) / len(full_df) * 50)
    ))
    risk_level = "LOW" if risk_score < 30 else "MODERATE" if risk_score < 60 else "HIGH"
    risk_color = "#10b981" if risk_score < 30 else "#f59e0b" if risk_score < 60 else "#ef4444"
    
    st.info(f"""
    **Key Patterns Identified:**
    - Primary behaviour: **{top_beh}**
    - Main trigger: **{top_ant}**
    - Hotspot location: **{top_loc}**
    - Peak time: **{top_session}**
    - Risk Level: **{risk_level}** ({risk_score}/100)
    
    **Behaviour Analysis Framework:** {student['name']} is most vulnerable when "{top_ant}" occurs in {top_loc} during {top_session}. 
    This behaviour is a safety strategy and communication method. The behaviour serves a function - likely escape/avoidance or attention-seeking based on patterns.
    
    **Trauma-Informed & Berry Street Lens:** Behaviours represent adaptive responses to perceived threat. Student's nervous system is responding to environmental cues. 
    **Berry Street Education Model** emphasizes five domains:
    - **Body:** Self-regulation, wellbeing, sensory needs
    - **Relationship:** Positive connections with adults and peers
    - **Stamina:** Persistence, engagement, coping with challenges
    - **Engagement:** Readiness for learning, curiosity
    - **Character:** Values, agency, identity
    
    **Foundation First:** Focus on Body (regulation) and Relationship (connection) domains before expecting Engagement or Character development.
    
    **CPI Alignment:** Use Supportive Stance, low slow voice, reduce audience, one key adult maintains connection. 
    Behaviour is communication - understand the message before responding.
    """)
    
    st.success(f"""
    **Evidence-Based Recommendations (Berry Street Framework):**
    
    **1. Body Domain (Regulation):** Regulated start before {top_session}, breathing exercises, movement breaks, sensory check-ins in {top_loc}, zones of regulation
    
    **2. Relationship Domain (Connection):** Key adult check-in before "{top_ant}", relationship-building activities, acknowledgment of feelings, co-regulation strategies
    
    **3. Stamina Domain (Persistence):** Link to Personal & Social Capability, teach help-seeking, practice requesting breaks, build coping strategies
    
    **4. SMART Goal:** Over 5 weeks, use help-seeking strategy in 4/5 opportunities with support (supports Body and Relationship). Review {(datetime.now() + timedelta(weeks=5)).strftime('%d/%m/%Y')}.
    """)
    
    st.markdown("---")
    
    # EXPORT with Berry Street branding
    st.markdown("### 📄 Export Data & Reports")
    st.caption("Professional reports prepared by Learning and Behaviour Unit using Berry Street Education Model")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = full_df.to_csv(index=False)
        st.download_button(
            "📥 Download Raw Data (CSV)",
            csv,
            file_name=f"{student['name'].replace(' ', '_')}_Incident_Data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        with st.spinner("Generating Behaviour Analysis Plan with graphs..."):
            docx_file = generate_behaviour_analysis_plan_docx(
                student, full_df, top_ant, top_beh, top_loc, top_session, risk_score, risk_level
            )
        if docx_file:
            st.download_button(
                "📄 Behaviour Analysis Plan (Word with Graphs)",
                docx_file,
                file_name=f"BAP_{student['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                help="Professional report with 6 embedded graphs, Berry Street framework, and evidence-based recommendations"
            )
        else:
            st.error("Unable to generate BAP. Please ensure kaleido is installed.")
    
    st.markdown("---")
    
    # Bottom Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back to Students", type="primary", key="back_analysis_bottom", use_container_width=True):
            go_to("program_students", selected_program=student["program"])
    with col2:
        if st.button("🏠 Program Landing", key="home_analysis_bottom", use_container_width=True):
            go_to("landing")

def render_admin_portal():
    """Admin portal for managing students and placement dates"""
    if st.session_state.current_user.get("role") != "ADM":
        st.error("⛔ Access Denied: Admin privileges required")
        if st.button("⬅ Back to Landing"):
            go_to("landing")
        return
    
    st.markdown("## 🔧 Admin Portal")
    
    col1, col2 = st.columns([6, 1])
    with col1:
        if st.button("⬅ Back to Landing", key="back_admin"):
            go_to("landing")
    
    st.markdown("---")
    
    # TABS
    tab1, tab2, tab3 = st.tabs(["👥 Manage Students", "📊 System Overview", "👨‍💼 Staff Management"])
    
    with tab1:
        st.markdown("### Student Management")
        
        # ADD NEW STUDENT
        with st.expander("➕ Add New Student", expanded=False):
            with st.form("add_student_form"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    new_name = st.text_input("Student Name *", placeholder="First L.")
                    new_grade = st.selectbox("Grade *", ["R", "Y1", "Y2", "Y3", "Y4", "Y5", "Y6", "Y7", "Y8", "Y9", "Y10", "Y11", "Y12"])
                
                with col2:
                    new_edid = st.text_input("EDID *", placeholder="ED123456")
                    new_dob = st.date_input("Date of Birth *", value=date(2015, 1, 1))
                
                with col3:
                    new_program = st.selectbox("Program *", ["JP", "PY", "SY"])
                    new_placement_start = st.date_input("Placement Start Date *", value=date.today())
                
                with col4:
                    st.write("")  # Spacer
                    new_placement_end = st.date_input("Placement End Date (Optional)", value=None)
                
                submitted = st.form_submit_button("Add Student", type="primary")
                
                if submitted:
                    if new_name and new_grade and new_program and new_edid:
                        new_student = {
                            "id": f"stu_{uuid.uuid4().hex[:8]}",
                            "name": new_name,
                            "grade": new_grade,
                            "dob": new_dob.isoformat(),
                            "edid": new_edid,
                            "program": new_program,
                            "placement_start": new_placement_start.isoformat(),
                            "placement_end": new_placement_end.isoformat() if new_placement_end else None
                        }
                        st.session_state.students.append(new_student)
                        st.success(f"✅ Added {new_name} (EDID: {new_edid}) to {PROGRAM_NAMES[new_program]}")
                        st.rerun()
                    else:
                        st.error("Please complete all required fields (Name, Grade, EDID, Program)")
        
        st.markdown("---")
        
        # EXISTING STUDENTS
        st.markdown("### Current Students")
        
        for program in ["JP", "PY", "SY"]:
            st.markdown(f"#### {PROGRAM_NAMES[program]}")
            
            program_students = [s for s in st.session_state.students if s["program"] == program]
            
            if not program_students:
                st.caption("No students in this program")
                continue
            
            for student in program_students:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{student['name']}**")
                        st.caption(f"Grade {student['grade']}")
                        if student.get('edid'):
                            st.caption(f"🆔 EDID: {student['edid']}")
                    
                    with col2:
                        if student.get('placement_start'):
                            start_date = datetime.fromisoformat(student['placement_start']).strftime('%d/%m/%Y')
                            st.caption(f"📅 Start: {start_date}")
                            
                            # Calculate days enrolled
                            start = datetime.fromisoformat(student['placement_start']).date()
                            end = datetime.fromisoformat(student['placement_end']).date() if student.get('placement_end') else date.today()
                            days = (end - start).days
                            st.caption(f"📊 {days} days enrolled")
                        else:
                            st.caption("📅 Start: Not set")
                            st.caption("📊 Days: N/A")
                    
                    with col3:
                        if student.get('placement_end'):
                            end_date = datetime.fromisoformat(student['placement_end']).strftime('%d/%m/%Y')
                            st.caption(f"📅 End: {end_date}")
                            st.caption("🔴 Inactive")
                        else:
                            st.caption("📅 End: Ongoing")
                            st.caption("🟢 Active")
                    
                    with col4:
                        if st.button("✏️", key=f"edit_{student['id']}", help="Edit student"):
                            st.session_state.editing_student = student['id']
                            st.rerun()
                
                # EDIT STUDENT
                if st.session_state.get("editing_student") == student['id']:
                    with st.expander("✏️ Edit Student Details", expanded=True):
                        with st.form(f"edit_form_{student['id']}"):
                            edit_col1, edit_col2 = st.columns(2)
                            
                            with edit_col1:
                                # Use existing date or default to today
                                default_start = datetime.fromisoformat(student['placement_start']).date() if student.get('placement_start') else date.today()
                                edit_start = st.date_input("Placement Start", 
                                                          value=default_start,
                                                          key=f"edit_start_{student['id']}")
                            
                            with edit_col2:
                                current_end = datetime.fromisoformat(student['placement_end']).date() if student.get('placement_end') else None
                                edit_end = st.date_input("Placement End (None = Ongoing)",
                                                        value=current_end,
                                                        key=f"edit_end_{student['id']}")
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("Save Changes", type="primary"):
                                    student['placement_start'] = edit_start.isoformat()
                                    student['placement_end'] = edit_end.isoformat() if edit_end else None
                                    st.session_state.editing_student = None
                                    st.success("✅ Updated")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("Cancel"):
                                    st.session_state.editing_student = None
                                    st.rerun()
    
    with tab2:
        st.markdown("### System Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_students = len(st.session_state.students)
            active_students = len([s for s in st.session_state.students if not s.get('placement_end')])
            st.metric("Total Students", total_students)
            st.caption(f"{active_students} active")
        
        with col2:
            st.metric("Total Incidents", len(st.session_state.incidents))
        
        with col3:
            critical = len([i for i in st.session_state.incidents if i.get("is_critical")])
            st.metric("Critical Incidents", critical)
        
        with col4:
            st.metric("Staff Members", len(st.session_state.staff))
        
        st.markdown("---")
        
        # Program breakdown
        st.markdown("#### Students by Program")
        for prog in ["JP", "PY", "SY"]:
            count = len([s for s in st.session_state.students if s["program"] == prog])
            active = len([s for s in st.session_state.students if s["program"] == prog and not s.get('placement_end')])
            st.write(f"**{PROGRAM_NAMES[prog]}:** {count} total ({active} active)")
    
    with tab3:
        st.markdown("### Staff Management")
        
        # ADD NEW STAFF
        with st.expander("➕ Add New Staff Member", expanded=False):
            with st.form("add_staff_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    staff_name = st.text_input("Full Name *", placeholder="Jane Smith")
                    staff_email = st.text_input("Email Address *", placeholder="jane.smith@school.edu.au", 
                                               help="Will be used as username and for critical incident notifications")
                    staff_password = st.text_input("Initial Password *", type="password", value="demo123")
                
                with col2:
                    staff_role = st.selectbox("Role *", 
                                             ["TSS", "Teacher", "Leader", "ADM"],
                                             help="TSS=Teacher/Support Staff, Leader=Program Leader, ADM=Administrator")
                    staff_program = st.selectbox("Program *", ["JP", "PY", "SY", "All Programs"])
                    staff_phone = st.text_input("Phone Number", placeholder="0412 345 678")
                
                staff_notes = st.text_area("Notes (Optional)", placeholder="Additional information about this staff member")
                
                submit_staff = st.form_submit_button("Add Staff Member", type="primary")
                
                if submit_staff:
                    if staff_name and staff_email and staff_password and staff_role:
                        # Check if email already exists
                        if any(s.get("email", "").lower() == staff_email.lower() for s in st.session_state.staff):
                            st.error(f"❌ Email {staff_email} already exists")
                        else:
                            new_staff = {
                                "id": f"staff_{uuid.uuid4().hex[:8]}",
                                "name": staff_name,
                                "email": staff_email.lower().strip(),
                                "password": staff_password,
                                "role": staff_role,
                                "program": staff_program if staff_program != "All Programs" else None,
                                "phone": staff_phone if staff_phone else None,
                                "notes": staff_notes if staff_notes else None,
                                "receive_critical_emails": True,  # Default to receiving emails
                                "created_date": date.today().isoformat()
                            }
                            st.session_state.staff.append(new_staff)
                            st.success(f"✅ Added {staff_name} ({staff_email})")
                            st.rerun()
                    else:
                        st.error("Please complete all required fields (Name, Email, Password, Role)")
        
        st.markdown("---")
        
        # EXISTING STAFF
        st.markdown("### Current Staff")
        
        # Group by role
        for role in ["ADM", "Leader", "Teacher", "TSS"]:
            role_names = {"ADM": "Administrators", "Leader": "Program Leaders", "Teacher": "Teachers", "TSS": "Support Staff"}
            role_staff = [s for s in st.session_state.staff if s.get("role") == role]
            
            if role_staff:
                st.markdown(f"#### {role_names[role]}")
                
                for staff in role_staff:
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.markdown(f"**{staff['name']}**")
                            st.caption(f"📧 {staff['email']}")
                            if staff.get('phone'):
                                st.caption(f"📱 {staff['phone']}")
                        
                        with col2:
                            st.caption(f"**Role:** {staff['role']}")
                            if staff.get('program'):
                                st.caption(f"**Program:** {PROGRAM_NAMES[staff['program']]}")
                            else:
                                st.caption("**Program:** All Programs")
                        
                        with col3:
                            receives_emails = staff.get('receive_critical_emails', True)
                            if receives_emails:
                                st.caption("📬 Receives critical alerts")
                            else:
                                st.caption("📪 No critical alerts")
                            
                            if staff.get('created_date'):
                                st.caption(f"Added: {staff['created_date']}")
                        
                        with col4:
                            if st.button("✏️", key=f"edit_staff_{staff['id']}", help="Edit staff"):
                                st.session_state.editing_staff = staff['id']
                                st.rerun()
                        
                        # EDIT STAFF
                        if st.session_state.get("editing_staff") == staff['id']:
                            with st.expander("✏️ Edit Staff Details", expanded=True):
                                with st.form(f"edit_staff_form_{staff['id']}"):
                                    edit_col1, edit_col2 = st.columns(2)
                                    
                                    with edit_col1:
                                        edit_name = st.text_input("Name", value=staff['name'], key=f"edit_staff_name_{staff['id']}")
                                        edit_email = st.text_input("Email", value=staff['email'], key=f"edit_staff_email_{staff['id']}")
                                        edit_phone = st.text_input("Phone", value=staff.get('phone', ''), key=f"edit_staff_phone_{staff['id']}")
                                    
                                    with edit_col2:
                                        edit_role = st.selectbox("Role", ["TSS", "Teacher", "Leader", "ADM"],
                                                                index=["TSS", "Teacher", "Leader", "ADM"].index(staff['role']),
                                                                key=f"edit_staff_role_{staff['id']}")
                                        edit_program = st.selectbox("Program", ["JP", "PY", "SY", "All Programs"],
                                                                   index=["JP", "PY", "SY", "All Programs"].index(
                                                                       PROGRAM_NAMES.get(staff.get('program'), "All Programs") 
                                                                       if staff.get('program') else "All Programs"
                                                                   ) if staff.get('program') else 3,
                                                                   key=f"edit_staff_program_{staff['id']}")
                                        edit_receive_emails = st.checkbox("Receive critical incident emails",
                                                                         value=staff.get('receive_critical_emails', True),
                                                                         key=f"edit_staff_emails_{staff['id']}")
                                    
                                    edit_notes = st.text_area("Notes", value=staff.get('notes', ''), key=f"edit_staff_notes_{staff['id']}")
                                    
                                    col_save, col_cancel, col_delete = st.columns([1, 1, 1])
                                    with col_save:
                                        if st.form_submit_button("💾 Save Changes", type="primary"):
                                            staff['name'] = edit_name
                                            staff['email'] = edit_email.lower().strip()
                                            staff['phone'] = edit_phone if edit_phone else None
                                            staff['role'] = edit_role
                                            staff['program'] = edit_program if edit_program != "All Programs" else None
                                            staff['receive_critical_emails'] = edit_receive_emails
                                            staff['notes'] = edit_notes if edit_notes else None
                                            st.session_state.editing_staff = None
                                            st.success("✅ Updated")
                                            st.rerun()
                                    
                                    with col_cancel:
                                        if st.form_submit_button("❌ Cancel"):
                                            st.session_state.editing_staff = None
                                            st.rerun()
                                    
                                    with col_delete:
                                        if st.form_submit_button("🗑️ Delete", help="Remove this staff member"):
                                            if staff['role'] != 'ADM' or len([s for s in st.session_state.staff if s.get('role') == 'ADM']) > 1:
                                                st.session_state.staff.remove(staff)
                                                st.session_state.editing_staff = None
                                                st.success("✅ Staff member removed")
                                                st.rerun()
                                            else:
                                                st.error("❌ Cannot delete the last administrator")
        
        st.markdown("---")
        
        # EMAIL NOTIFICATION SETTINGS
        st.markdown("### 📧 Email Notification Recipients")
        st.caption("Staff members who will receive critical incident notifications:")
        
        email_recipients = [s for s in st.session_state.staff if s.get('receive_critical_emails', True)]
        
        if email_recipients:
            for recipient in email_recipients:
                st.write(f"• **{recipient['name']}** ({recipient['email']}) - {recipient['role']}")
        else:
            st.warning("⚠️ No staff members set to receive critical incident emails!")






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
    elif page == "admin_portal": render_admin_portal()
    else: render_landing_page()

if __name__ == "__main__":
    main()

