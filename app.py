# app.py
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import time
import random
from google import genai
from google.genai import types
from dummy_data import ELIGIBILITY_RULES, EXISTING_APPLICANTS
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
from datetime import timedelta

st.set_page_config(page_title="FlexiLoans Smart Onboarding Engine", layout="wide", initial_sidebar_state="expanded")

# ── FlexiLoans Brand CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── CSS Variables ── */
:root {
  --brand-navy:        #1B365D;
  --brand-cyan:        #00B4D8;
  --brand-cyan-hover:  #0097B2;
  --brand-cyan-bg:     #E0F7FA;
  --bg:                #F5F7FA;
  --surface:           #FFFFFF;
  --border:            #E5E7EB;
  --text:              #374151;
  --text2:             #6B7280;
  --text3:             #9CA3AF;
  --green:             #16A34A;
  --green-bg:          rgba(22,163,74,0.1);
  --red:               #DC2626;
  --red-bg:            rgba(220,38,38,0.1);
  --amber:             #D97706;
  --amber-bg:          rgba(217,119,6,0.1);
  --blue:              #2563EB;
  --blue-bg:           rgba(37,99,235,0.1);
}

/* ── Global font & background ── */
html, body, [data-testid="stApp"], .main {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

/* ── Hide Streamlit default branding ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Lock sidebar open — hide the collapse arrow button ── */
[data-testid="collapsedControl"] { display: none !important; }
button[data-testid="baseButton-header"] { display: none !important; }


/* ── Page title ── */
.main h1 {
  color: var(--brand-navy) !important;
  font-size: 22px !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em;
  border-bottom: 3px solid var(--brand-cyan);
  padding-bottom: 10px;
  margin-bottom: 20px;
}
.main h2 { color: var(--brand-navy) !important; font-size: 16px !important; font-weight: 600 !important; }
.main h3 { color: var(--brand-navy) !important; font-size: 14px !important; font-weight: 600 !important; }
.main p, .main li, .block-container label, .block-container .stMarkdown { color: var(--text) !important; font-size: 13px !important; }

/* ── Sidebar — full navy brand ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #1B365D 0%, #162d4e 100%) !important;
  border-right: none !important;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] small { color: rgba(255,255,255,0.85) !important; font-size: 12px !important; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
  color: var(--brand-cyan) !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }
[data-testid="stSidebar"] .stMetric { background: rgba(0,180,216,0.12) !important; border-radius: 8px; padding: 8px; }
[data-testid="stSidebar"] [data-testid="stMetricValue"] { color: var(--brand-cyan) !important; font-size: 18px !important; font-weight: 700 !important; }
[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color: rgba(255,255,255,0.7) !important; font-size: 10px !important; }

/* Sidebar radio buttons */
[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 4px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  background: rgba(255,255,255,0.05) !important;
  border-radius: 8px !important;
  padding: 8px 12px !important;
  margin: 2px 0 !important;
  transition: all 0.2s;
  border-left: 3px solid transparent !important;
  color: rgba(255,255,255,0.85) !important;
  font-size: 13px !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: rgba(255,255,255,0.1) !important;
  border-left-color: var(--brand-cyan) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + div label,
[data-testid="stSidebar"] [data-testid="stRadio"] input:checked ~ label {
  background: rgba(0,180,216,0.18) !important;
  border-left-color: var(--brand-cyan) !important;
  color: #FFFFFF !important;
  font-weight: 600 !important;
}

/* ── Buttons — primary cyan CTA ── */
.stButton > button {
  background: var(--brand-cyan) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 8px 18px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  font-family: 'Inter', sans-serif !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 1px 3px rgba(0,180,216,0.25) !important;
}
.stButton > button:hover {
  background: var(--brand-cyan-hover) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(0,180,216,0.35) !important;
}
.stButton > button[kind="secondary"] {
  background: #FFFFFF !important;
  color: var(--brand-navy) !important;
  border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover {
  background: var(--bg) !important;
}
/* Download buttons */
[data-testid="stDownloadButton"] > button {
  background: var(--brand-navy) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 8px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #152a4a !important; }

/* ── Form submit buttons ── */
[data-testid="stForm"] .stButton > button,
button[kind="primaryFormSubmit"] {
  background: var(--brand-navy) !important;
  width: 100% !important;
}
[data-testid="stForm"] .stButton > button:hover { background: #152a4a !important; }

/* ── Input fields ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  font-size: 13px !important;
  font-family: 'Inter', sans-serif !important;
  color: var(--text) !important;
  background: var(--surface) !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
  border-color: var(--brand-cyan) !important;
  box-shadow: 0 0 0 2px rgba(0,180,216,0.15) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 12px 16px !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
[data-testid="stMetricLabel"] { color: var(--text2) !important; font-size: 11px !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stMetricValue"] { color: var(--brand-navy) !important; font-size: 20px !important; font-weight: 700 !important; font-family: 'DM Mono', monospace !important; }

/* ── Status messages ── */
[data-testid="stSuccess"] {
  background: var(--green-bg) !important;
  border: 1px solid var(--green) !important;
  border-left: 4px solid var(--green) !important;
  border-radius: 8px !important;
  color: #14532D !important;
}
[data-testid="stError"] {
  background: var(--red-bg) !important;
  border: 1px solid var(--red) !important;
  border-left: 4px solid var(--red) !important;
  border-radius: 8px !important;
}
[data-testid="stWarning"] {
  background: var(--amber-bg) !important;
  border: 1px solid var(--amber) !important;
  border-left: 4px solid var(--amber) !important;
  border-radius: 8px !important;
}
[data-testid="stInfo"] {
  background: var(--blue-bg) !important;
  border: 1px solid var(--blue) !important;
  border-left: 4px solid var(--blue) !important;
  border-radius: 8px !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  margin-bottom: 8px !important;
  padding: 12px 16px !important;
}
[data-testid="stChatMessage"][data-testid*="assistant"],
[data-testid="stChatMessage"]:has([data-testid="stChatMessageContent"]:first-child) {
  border-left: 3px solid var(--brand-cyan) !important;
  background: #FAFEFF !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
  border: 2px solid var(--border) !important;
  border-radius: 10px !important;
  font-size: 13px !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus { border-color: var(--brand-cyan) !important; }
[data-testid="stChatInput"] button {
  background: var(--brand-cyan) !important;
  border-radius: 8px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  border: 2px dashed var(--border) !important;
  border-radius: 10px !important;
  background: var(--bg) !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--brand-cyan) !important; }

/* ── Expander (main content) ── */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  background: var(--surface) !important;
}
[data-testid="stExpander"] summary {
  color: var(--brand-navy) !important;
  font-weight: 600 !important;
  font-size: 13px !important;
}

/* ── Sidebar expander — dark-themed ── */
[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
  border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
[data-testid="stSidebar"] [data-testid="stExpander"] summary span {
  color: rgba(255,255,255,0.9) !important;
  font-size: 12px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary svg {
  fill: rgba(255,255,255,0.7) !important;
  stroke: rgba(255,255,255,0.7) !important;
}

/* ── Sidebar inputs & selects — dark-themed ── */
[data-testid="stSidebar"] .stTextInput > div > div > input,
[data-testid="stSidebar"] .stNumberInput > div > div > input,
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stSelectbox > div > div > div {
  background: rgba(255,255,255,0.1) !important;
  color: #FFFFFF !important;
  border-color: rgba(255,255,255,0.2) !important;
}
[data-testid="stSidebar"] .stNumberInput button {
  background: rgba(255,255,255,0.1) !important;
  color: #FFFFFF !important;
  border-color: rgba(255,255,255,0.2) !important;
}

/* ── Sidebar slider labels ── */
[data-testid="stSidebar"] [data-testid="stSlider"] p,
[data-testid="stSidebar"] [data-testid="stSlider"] span,
[data-testid="stSidebar"] [data-testid="stSlider"] label {
  color: rgba(255,255,255,0.85) !important;
}

/* ── Sidebar all text elements — strong override ── */
[data-testid="stSidebar"] p { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] li { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] span:not([data-testid]) { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stMarkdown p { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] .stMarkdown li { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: rgba(255,255,255,0.85) !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li { color: rgba(255,255,255,0.85) !important; }

/* ── Sidebar caption ── */
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] small { color: rgba(255,255,255,0.55) !important; }

/* ── Sidebar selectbox option text ── */
[data-testid="stSidebar"] [data-testid="stSelectbox"] span { color: rgba(255,255,255,0.9) !important; }

/* ── Sidebar info/success/warning/error boxes ── */
[data-testid="stSidebar"] [data-testid="stAlert"] {
  background: rgba(255,255,255,0.1) !important;
  border-color: rgba(255,255,255,0.25) !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] p { color: #FFFFFF !important; }

/* ── Progress bar ── */
.stProgress > div > div { background: var(--brand-cyan) !important; border-radius: 99px !important; }
.stProgress > div { background: var(--border) !important; border-radius: 99px !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--brand-cyan) !important; }

/* ── Balloons (keep default) ── */

/* ── Slider ── */
[data-testid="stSlider"] [role="slider"] { background: var(--brand-cyan) !important; border-color: var(--brand-cyan) !important; }
[data-testid="stSlider"] [data-baseweb="slider"] div[role="progressbar"] { background: var(--brand-cyan) !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
  color: var(--text2) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--brand-navy) !important;
  border-bottom: 2px solid var(--brand-cyan) !important;
  font-weight: 600 !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 16px 0 !important; }

/* ── Subheader overrides ── */
[data-testid="stMarkdownContainer"] h3 {
  color: var(--brand-navy) !important;
  border-bottom: 2px solid var(--brand-cyan);
  padding-bottom: 6px;
  margin-bottom: 14px;
}

/* ── Number inputs mono ── */
.stNumberInput input {
  font-family: 'DM Mono', monospace !important;
}

/* ── FlexiLoans branding header bar ── */
.flexi-topbar {
  background: var(--brand-navy);
  padding: 10px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: -1rem -1rem 20px -1rem;
  border-bottom: 3px solid var(--brand-cyan);
}
.flexi-logo { font-size: 18px; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em; }
.flexi-logo span { color: var(--brand-cyan); }
.flexi-tagline { font-size: 11px; color: rgba(255,255,255,0.55); margin-left: auto; font-style: italic; }

/* ── AI/FlexiBot banner ── */
.ai-banner {
  background: var(--brand-cyan-bg);
  border-left: 3px solid var(--brand-cyan);
  border-radius: 0 8px 8px 0;
  padding: 10px 16px;
  margin-bottom: 12px;
}
.ai-banner .ai-dot {
  display: inline-block;
  width: 8px; height: 8px;
  background: var(--brand-cyan);
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(0,180,216,0.4);
  margin-right: 6px;
}

/* ── Status badges ── */
.badge {
  display: inline-block;
  border-radius: 99px;
  font-size: 10px;
  font-weight: 500;
  padding: 2px 8px;
}
.badge-green  { background: var(--green-bg);  color: var(--green);  }
.badge-red    { background: var(--red-bg);    color: var(--red);    }
.badge-amber  { background: var(--amber-bg);  color: var(--amber);  }
.badge-cyan   { background: var(--brand-cyan-bg); color: var(--brand-cyan); }
.badge-navy   { background: var(--brand-navy); color: #FFFFFF; }

/* ── Select box ── */
[data-testid="stSelectbox"] > div { border-radius: 8px !important; }

/* ── Checkbox ── */
.block-container [data-testid="stCheckbox"] label { color: var(--text) !important; font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)

# Brand header bar
st.markdown("""
<div class="flexi-topbar">
  <div style="width:36px;height:36px;background:#00B4D8;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:800;color:#1B365D;margin-right:10px;letter-spacing:-0.5px;flex-shrink:0">FL</div>
  <div class="flexi-logo">Flexi<span>Loans</span></div>
  <div style="width:1px;height:20px;background:rgba(255,255,255,0.2);margin:0 8px"></div>
  <div style="font-size:11px;color:rgba(255,255,255,0.6);font-weight:400">Smart Onboarding Engine</div>
  <div class="flexi-tagline">Loan Nahi Samjho Tarakki Hai</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "workflow_stream" not in st.session_state:
    st.session_state.workflow_stream = "💬 Chat with FlexiBot"
if "eligibility_passed" not in st.session_state:
    st.session_state.eligibility_passed = False
if "applicant_data" not in st.session_state:
    st.session_state.applicant_data = {}
if "documents_uploaded" not in st.session_state:
    st.session_state.documents_uploaded = {"pan": False, "bank": False}
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_active" not in st.session_state:
    st.session_state.chat_active = False
if "phone_verified" not in st.session_state:
    st.session_state.phone_verified = False
if "app_number_collected" not in st.session_state:
    st.session_state.app_number_collected = False
if "saved_applications" not in st.session_state:
    st.session_state.saved_applications = {}
if "current_stage" not in st.session_state:
    st.session_state.current_stage = "NOT_STARTED"
if "stage_timestamps" not in st.session_state:
    st.session_state.stage_timestamps = {}
if "document_validation" not in st.session_state:
    st.session_state.document_validation = {"pan": None, "bank": None}
if "emi_calculation" not in st.session_state:
    st.session_state.emi_calculation = None
if "apply_with_emi_terms" not in st.session_state:
    st.session_state.apply_with_emi_terms = False
if "show_financial_guidance" not in st.session_state:
    st.session_state.show_financial_guidance = False
if "credit_score_input" not in st.session_state:
    st.session_state.credit_score_input = 700
if "recommendations_generated" not in st.session_state:
    st.session_state.recommendations_generated = False
if "smart_recommendations" not in st.session_state:
    st.session_state.smart_recommendations = None
if "demo_approval_time" not in st.session_state:
    st.session_state.demo_approval_time = None
if "demo_approved" not in st.session_state:
    st.session_state.demo_approved = False
if "topup_active" not in st.session_state:
    st.session_state.topup_active = False
if "topup_approved" not in st.session_state:
    st.session_state.topup_approved = False
if "topup_data" not in st.session_state:
    st.session_state.topup_data = {}
if "topup_approval_time" not in st.session_state:
    st.session_state.topup_approval_time = None
if "flexibot_gathered" not in st.session_state:
    st.session_state.flexibot_gathered = {}
if "flexibot_nav" not in st.session_state:
    st.session_state.flexibot_nav = False
if "flexibot_messages" not in st.session_state:
    st.session_state.flexibot_messages = []   # persists FlexiBot chat across stream switches
if "pending_nav" not in st.session_state:
    st.session_state.pending_nav = None       # queued navigation action to execute
if "chat_pan_uploaded" not in st.session_state:
    st.session_state.chat_pan_uploaded = False
if "chat_approval_time" not in st.session_state:
    st.session_state.chat_approval_time = None
if "chat_approved" not in st.session_state:
    st.session_state.chat_approved = False
if "chat_app_id" not in st.session_state:
    st.session_state.chat_app_id = None
if "chat_offer_ready" not in st.session_state:
    st.session_state.chat_offer_ready = False
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = (
        os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
    )

# Sidebar
st.sidebar.title("🏦 FlexiLoans Onboarding")
st.sidebar.markdown("---")

# API Key input (shown only when not already set via env var)
if not st.session_state.gemini_api_key:
    entered_key = st.sidebar.text_input(
        "🔑 Gemini API Key",
        type="password",
        placeholder="Paste your API key here",
        help="Get a free key at ai.google.dev"
    )
    if entered_key:
        st.session_state.gemini_api_key = entered_key
        st.rerun()
    st.sidebar.warning("Enter your Gemini API Key above to use FlexiBot.")
    st.sidebar.markdown("---")

# Create Gemini client
if st.session_state.gemini_api_key:
    client = genai.Client(api_key=st.session_state.gemini_api_key)
else:
    client = None

stream_choice = st.sidebar.radio(
    "Select Application Stream:",
    ["New Applicant", "Existing Applicant", "💬 Chat with FlexiBot"],
    key="stream_selector"
)

if stream_choice != st.session_state.workflow_stream:
    st.session_state.workflow_stream = stream_choice
    if not st.session_state.flexibot_nav:
        # Manual switch — full reset
        st.session_state.eligibility_passed = False
        st.session_state.applicant_data = {}
        st.session_state.documents_uploaded = {"pan": False, "bank": False}
        st.session_state.messages = []
        st.session_state.chat_active = False
        st.session_state.phone_verified = False
        st.session_state.app_number_collected = False
        st.session_state.demo_approval_time = None
        st.session_state.demo_approved = False
        st.session_state.topup_active = False
        st.session_state.topup_approved = False
        st.session_state.topup_data = {}
        st.session_state.topup_approval_time = None
        st.session_state.chat_pan_uploaded = False
        st.session_state.chat_approval_time = None
        st.session_state.chat_approved = False
        st.session_state.chat_app_id = None
        st.session_state.chat_offer_ready = False
    st.session_state.flexibot_nav = False  # always clear after consuming

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Eligibility Criteria")
st.sidebar.write(f"• Age: {ELIGIBILITY_RULES['min_age']}-{ELIGIBILITY_RULES['max_age']} years")
st.sidebar.write(f"• Annual Turnover: ≥₹{ELIGIBILITY_RULES['min_annual_turnover']:,}")
st.sidebar.write(f"• Monthly Income: ≥₹{ELIGIBILITY_RULES['min_monthly_income']:,}")

st.sidebar.markdown("---")
st.sidebar.subheader("👥 Customer Types")
st.sidebar.write("🎉 **Approved**: Loan processed")
st.sidebar.write("⏳ **In Progress**: Under review")
st.sidebar.write("🆕 **New**: First-time applicant")
st.sidebar.write("❌ **Rejected**: Application declined")

# Show saved applications count
if "saved_applications" in st.session_state and st.session_state.saved_applications:
    st.sidebar.markdown("---")
    st.sidebar.info(f"💾 {len(st.session_state.saved_applications)} saved application(s)")

# Progress Tracking Function
def get_application_progress():
    """Calculate application progress and stage information"""
    stages = {
        "NOT_STARTED": {"name": "Not Started", "progress": 0, "icon": "⚪", "time_estimate": "5 min"},
        "ELIGIBILITY_CHECK": {"name": "Eligibility Check", "progress": 20, "icon": "🔍", "time_estimate": "2 min"},
        "DOCUMENTS_UPLOAD": {"name": "Documents Upload", "progress": 50, "icon": "📎", "time_estimate": "5 min"},
        "VERIFICATION": {"name": "Verification", "progress": 75, "icon": "✅", "time_estimate": "2-3 days"},
        "APPROVED": {"name": "Approved", "progress": 100, "icon": "🎉", "time_estimate": "Complete"}
    }
    
    current_stage = st.session_state.current_stage
    
    # Determine current stage based on application state
    if st.session_state.workflow_stream == "New Applicant":
        if not st.session_state.eligibility_passed:
            current_stage = "NOT_STARTED"
        elif not st.session_state.documents_uploaded["pan"] or not st.session_state.documents_uploaded["bank"]:
            current_stage = "DOCUMENTS_UPLOAD"
            if st.session_state.eligibility_passed and current_stage != st.session_state.current_stage:
                st.session_state.stage_timestamps["ELIGIBILITY_CHECK"] = datetime.now()
        else:
            current_stage = "VERIFICATION"
            if st.session_state.documents_uploaded["pan"] and st.session_state.documents_uploaded["bank"] and current_stage != st.session_state.current_stage:
                st.session_state.stage_timestamps["DOCUMENTS_UPLOAD"] = datetime.now()
    
    elif st.session_state.workflow_stream == "Existing Applicant" and st.session_state.chat_active:
        customer_type = st.session_state.applicant_data.get('customer_type', 'IN_PROGRESS')
        if customer_type == "APPROVED":
            current_stage = "APPROVED"
        elif customer_type == "IN_PROGRESS":
            current_stage = "VERIFICATION"
        else:
            current_stage = "DOCUMENTS_UPLOAD"
    
    st.session_state.current_stage = current_stage
    return stages, current_stage

def render_progress_bar():
    """Render visual progress bar with stages"""
    stages, current_stage = get_application_progress()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Application Progress")
    
    # Progress percentage
    progress_pct = stages[current_stage]["progress"]
    st.sidebar.progress(progress_pct / 100)
    st.sidebar.markdown(f"**{progress_pct}% Complete**")
    
    # Stage indicators
    stage_order = ["NOT_STARTED", "ELIGIBILITY_CHECK", "DOCUMENTS_UPLOAD", "VERIFICATION", "APPROVED"]
    
    for stage_key in stage_order:
        stage_info = stages[stage_key]
        
        if stage_key == current_stage:
            # Current stage - highlighted
            st.sidebar.markdown(f"**{stage_info['icon']} {stage_info['name']}** ⏳")
            st.sidebar.caption(f"Estimated: {stage_info['time_estimate']}")
        elif stage_order.index(stage_key) < stage_order.index(current_stage):
            # Completed stages
            st.sidebar.markdown(f"✅ ~~{stage_info['name']}~~")
        else:
            # Upcoming stages
            st.sidebar.markdown(f"⚪ {stage_info['name']}")
    
    # Time estimate for next stage
    if current_stage != "APPROVED":
        next_stage_idx = stage_order.index(current_stage) + 1
        if next_stage_idx < len(stage_order):
            next_stage = stage_order[next_stage_idx]
            st.sidebar.info(f"⏱️ Next: {stages[next_stage]['name']} (~{stages[next_stage]['time_estimate']})")
    else:
        st.sidebar.success("🎊 Application Complete!")

# Document Quality Checker Function
def validate_document(uploaded_file, doc_type):
    """Simple document validation - checks if file is PDF"""
    if uploaded_file is None:
        return None
    
    validation_result = {
        "valid": False,
        "message": "",
        "file_name": uploaded_file.name,
        "file_type": uploaded_file.type
    }
    
    # Check if file is PDF
    if uploaded_file.type == "application/pdf":
        validation_result["valid"] = True
        validation_result["message"] = f"✅ {doc_type} Document Clear - PDF format accepted!"
    else:
        validation_result["valid"] = False
        validation_result["message"] = f"⚠️ {doc_type} Document quality issue - Please upload PDF format for best results"
    
    return validation_result

def render_document_validation_feedback(validation_result):
    """Render validation feedback UI"""
    if validation_result is None:
        return
    
    if validation_result["valid"]:
        st.success(validation_result["message"])
        st.caption(f"📄 {validation_result['file_name']}")
    else:
        st.warning(validation_result["message"])
        st.caption(f"📄 {validation_result['file_name']} - {validation_result['file_type']}")

# EMI Calculator Function
def calculate_emi(principal, annual_rate, tenure_months):
    """Calculate EMI using standard formula"""
    monthly_rate = annual_rate / (12 * 100)
    
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
    
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    
    return {
        "emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "principal": principal,
        "tenure_months": tenure_months,
        "annual_rate": annual_rate
    }

def render_emi_calculator():
    """Render EMI calculator widget in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧮 EMI Calculator")
    
    with st.sidebar.expander("Calculate Your EMI", expanded=False):
        loan_amount = st.number_input(
            "Loan Amount (₹)",
            min_value=50000,
            max_value=10000000,
            value=500000,
            step=50000,
            key="emi_loan_amount"
        )
        
        tenure_years = st.slider(
            "Loan Tenure (Years)",
            min_value=1,
            max_value=5,
            value=2,
            key="emi_tenure"
        )
        
        interest_rate = st.slider(
            "Interest Rate (% p.a.)",
            min_value=8.0,
            max_value=18.0,
            value=12.0,
            step=0.5,
            key="emi_rate"
        )
        
        if st.button("Calculate EMI", key="calc_emi_btn"):
            tenure_months = tenure_years * 12
            result = calculate_emi(loan_amount, interest_rate, tenure_months)
            st.session_state.emi_calculation = result
        
        if st.session_state.emi_calculation:
            result = st.session_state.emi_calculation
            
            st.markdown("---")
            st.markdown("### 📊 EMI Breakdown")
            
            # Display EMI
            st.metric("Monthly EMI", f"₹{result['emi']:,.0f}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Principal", f"₹{result['principal']:,.0f}")
            with col2:
                st.metric("Tenure", f"{result['tenure_months']} months")
            
            st.metric("Total Interest", f"₹{result['total_interest']:,.0f}")
            st.metric("Total Payment", f"₹{result['total_payment']:,.0f}")
            
            # Interest vs Principal visualization
            principal_pct = (result['principal'] / result['total_payment']) * 100
            interest_pct = (result['total_interest'] / result['total_payment']) * 100
            
            st.markdown("**Payment Breakdown:**")
            st.progress(principal_pct / 100)
            st.caption(f"Principal: {principal_pct:.1f}% | Interest: {interest_pct:.1f}%")
            
            # Apply with these terms button
            if st.button("✅ Apply with These Terms", key="apply_emi_terms", type="primary"):
                st.session_state.apply_with_emi_terms = True
                st.success(f"✓ EMI terms saved: ₹{result['emi']:,.0f}/month for {result['tenure_months']} months")
                
                # Add to chat if active
                if st.session_state.chat_active:
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"I want to apply for a loan of ₹{result['principal']:,.0f} with EMI of ₹{result['emi']:,.0f} per month for {result['tenure_months']} months"
                    })
                    st.rerun()

def render_financial_guidance():
    """Render comprehensive financial guidance and advisory section"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("💡 Financial Guidance")
    
    with st.sidebar.expander("Get Financial Advice", expanded=False):
        guidance_tab = st.selectbox(
            "Select Topic:",
            ["Credit Score Improvement", "EMI Management", "Loan Comparison", "Financial Health Check"],
            key="guidance_topic"
        )
        
        if guidance_tab == "Credit Score Improvement":
            st.markdown("### 📈 Credit Score Improvement")
            
            current_score = st.slider(
                "Your Current Credit Score",
                min_value=300,
                max_value=900,
                value=st.session_state.credit_score_input,
                step=10,
                key="credit_score_slider"
            )
            st.session_state.credit_score_input = current_score
            
            # Credit score analysis
            if current_score >= 750:
                st.success("✅ Excellent Credit Score!")
                score_status = "You qualify for the best interest rates."
            elif current_score >= 700:
                st.info("👍 Good Credit Score")
                score_status = "You qualify for competitive rates."
            elif current_score >= 650:
                st.warning("⚠️ Fair Credit Score")
                score_status = "Focus on improvement strategies."
            else:
                st.error("❌ Poor Credit Score")
                score_status = "Follow improvement plan urgently."
            
            st.caption(score_status)
            
            st.markdown("**Quick Tips:**")
            st.write("✓ Pay EMIs on time (35% impact)")
            st.write("✓ Keep utilization below 30%")
            st.write("✓ Don't apply for multiple loans")
            st.write("✓ Check report for errors")
            
            if st.button("💬 Get Credit Advice", key="credit_advice_btn"):
                if st.session_state.chat_active:
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"My credit score is {current_score}. How can I improve it?"
                    })
                    st.success("✓ Sent to FlexiBot!")
                    st.rerun()
        
        elif guidance_tab == "EMI Management":
            st.markdown("### 💰 EMI Management")
            
            monthly_income = st.number_input("Monthly Income (₹)", min_value=10000, value=50000, step=5000, key="income_emi")
            total_emis = st.number_input("Total EMIs (₹)", min_value=0, value=15000, step=1000, key="total_emis")
            
            emi_ratio = (total_emis / monthly_income) * 100
            
            st.progress(min(emi_ratio / 100, 1.0))
            st.metric("EMI Burden", f"{emi_ratio:.1f}%")
            
            if emi_ratio <= 40:
                st.success("✅ Healthy burden!")
            elif emi_ratio <= 50:
                st.warning("⚠️ Moderate burden")
            else:
                st.error("❌ High burden")
            
            st.write("✓ Keep EMI below 40% of income")
            st.write("✓ Maintain emergency fund")
            st.write("✓ Set up auto-debit")
        
        elif guidance_tab == "Loan Comparison":
            st.markdown("### 🔍 Loan Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Option A**")
                loan_a = st.number_input("Amount", min_value=50000, value=500000, key="loan_a")
                rate_a = st.number_input("Rate %", min_value=8.0, value=12.0, key="rate_a")
                tenure_a = st.number_input("Months", min_value=6, value=24, key="tenure_a")
            
            with col2:
                st.markdown("**Option B**")
                loan_b = st.number_input("Amount", min_value=50000, value=500000, key="loan_b")
                rate_b = st.number_input("Rate %", min_value=8.0, value=14.0, key="rate_b")
                tenure_b = st.number_input("Months", min_value=6, value=36, key="tenure_b")
            
            if st.button("Compare", key="compare_btn"):
                result_a = calculate_emi(loan_a, rate_a, tenure_a)
                result_b = calculate_emi(loan_b, rate_b, tenure_b)
                
                st.metric("A - EMI", f"₹{result_a['emi']:,.0f}")
                st.metric("B - EMI", f"₹{result_b['emi']:,.0f}")
                
                if result_a['total_interest'] < result_b['total_interest']:
                    st.success(f"💡 A saves ₹{result_b['total_interest'] - result_a['total_interest']:,.0f}!")
        
        elif guidance_tab == "Financial Health Check":
            st.markdown("### 🏥 Health Check")
            
            income = st.number_input("Income", min_value=10000, value=50000, key="income_fhc")
            expenses = st.number_input("Expenses", min_value=0, value=25000, key="expenses_fhc")
            savings = st.number_input("Savings", min_value=0, value=10000, key="savings_fhc")
            debt = st.number_input("Total Debt", min_value=0, value=200000, key="debt_fhc")
            
            if st.button("Check Health", key="fhc_btn"):
                savings_rate = (savings / income) * 100
                debt_ratio = (debt / (income * 12)) * 100
                
                health_score = 100
                if savings_rate < 10:
                    health_score -= 20
                if debt_ratio > 50:
                    health_score -= 30
                
                st.progress(health_score / 100)
                st.metric("Health Score", f"{health_score}/100")
                
                if health_score >= 80:
                    st.success("🌟 Excellent!")
                elif health_score >= 60:
                    st.info("👍 Good")
                else:
                    st.warning("⚠️ Needs attention")

# PDF Generation Functions
def generate_application_pdf(applicant_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1f4788'), alignment=TA_CENTER, spaceAfter=30)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1f4788'), spaceAfter=12)
    
    elements.append(Paragraph("FLEXILOANS", title_style))
    elements.append(Paragraph("Loan Application Form", styles['Heading2']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(f"Application ID: <b>{applicant_data['application_id']}</b>", styles['Normal']))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Applicant Information", heading_style))
    
    data = [
        ['Field', 'Details'],
        ['Full Name', applicant_data['name']],
        ['Phone Number', applicant_data['phone']],
        ['Age', str(applicant_data['age'])],
        ['Gross Annual Turnover', f"Rs.{applicant_data['turnover']:,}"],
        ['Net Monthly Income', f"Rs.{applicant_data['income']:,}"],
    ]

    table = Table(data, colWidths=[2.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Document Status", heading_style))
    elements.append(Paragraph(f"PAN Card: {'Uploaded' if st.session_state.documents_uploaded['pan'] else 'Pending'}", styles['Normal']))
    elements.append(Paragraph(f"Bank Statement: {'Uploaded' if st.session_state.documents_uploaded['bank'] else 'Pending'}", styles['Normal']))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("<i>This is a system-generated document. No signature required.</i>", styles['Italic']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_sanction_letter_pdf(applicant_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1f4788'), alignment=TA_CENTER, spaceAfter=30)
    
    elements.append(Paragraph("FLEXILOANS", title_style))
    elements.append(Paragraph("LOAN SANCTION LETTER", ParagraphStyle('SubTitle', parent=styles['Heading2'], alignment=TA_CENTER, textColor=colors.green)))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph(f"Dear <b>{applicant_data['name']}</b>,", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("We are pleased to inform you that your loan application has been <b>APPROVED</b>.", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    data = [
        ['Loan Details', ''],
        ['Application ID', applicant_data['application_id']],
        ['Applicant Name', applicant_data['name']],
        ['Sanctioned Amount', f"Rs.{applicant_data.get('loan_amount', 0):,}"],
        ['Approval Date', applicant_data.get('approved_date', 'N/A')],
        ['Disbursement Date', applicant_data.get('disbursement_date', 'Processing')],
    ]
    
    table = Table(data, colWidths=[2.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("<b>Next Steps:</b>", styles['Heading3']))
    elements.append(Paragraph("1. The loan amount will be disbursed to your registered bank account.", styles['Normal']))
    elements.append(Paragraph("2. You will receive EMI schedule details via email and SMS.", styles['Normal']))
    elements.append(Paragraph("3. Please ensure timely repayment to maintain a good credit score.", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Congratulations on your loan approval!", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Best Regards,<br/><b>FlexiLoans Team</b>", styles['Normal']))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("<i>This is a system-generated sanction letter.</i>", styles['Italic']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_application_submission_pdf(applicant_data, documents_status):
    """Generate application submission confirmation PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1f4788'), alignment=TA_CENTER, spaceAfter=30)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1f4788'), spaceAfter=12)
    
    elements.append(Paragraph("FLEXILOANS", title_style))
    elements.append(Paragraph("Application Submission Confirmation", ParagraphStyle('SubTitle', parent=styles['Heading2'], alignment=TA_CENTER, textColor=colors.HexColor('#1f4788'))))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph(f"<b>Application ID:</b> {applicant_data['application_id']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Submission Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Dear Customer,", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Thank you for submitting your loan application with FlexiLoans. We have successfully received your application and all required documents.", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Application Details", heading_style))
    
    data = [
        ['Field', 'Details'],
        ['Full Name', applicant_data['name']],
        ['Phone Number', applicant_data['phone']],
        ['Age', str(applicant_data['age'])],
        ['Gross Annual Turnover', f"Rs.{applicant_data['turnover']:,}"],
        ['Net Monthly Income', f"Rs.{applicant_data['income']:,}"],
        ['Application Status', 'Submitted - Under Review']
    ]
    
    table = Table(data, colWidths=[2.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Document Submission Status", heading_style))
    
    doc_data = [
        ['Document Type', 'Status'],
        ['PAN Card', 'Submitted' if documents_status.get('pan') else 'Pending'],
        ['Bank Statement', 'Submitted' if documents_status.get('bank') else 'Pending']
    ]
    
    doc_table = Table(doc_data, colWidths=[3*inch, 3.5*inch])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(doc_table)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("<b>What Happens Next?</b>", heading_style))
    elements.append(Paragraph("1. <b>Verification (2-3 business days):</b> Our team will verify your documents and information.", styles['Normal']))
    elements.append(Paragraph("2. <b>Credit Assessment:</b> We will evaluate your creditworthiness and loan eligibility.", styles['Normal']))
    elements.append(Paragraph("3. <b>Approval Decision:</b> You will receive an email and SMS notification about your application status.", styles['Normal']))
    elements.append(Paragraph("4. <b>Disbursement:</b> Upon approval, funds will be disbursed to your registered bank account.", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("<b>Important Notes:</b>", heading_style))
    elements.append(Paragraph(f"• Keep your Application ID safe: <b>{applicant_data['application_id']}</b>", styles['Normal']))
    elements.append(Paragraph("• You can check your application status anytime using your Application ID and phone number.", styles['Normal']))
    elements.append(Paragraph("• For any queries, contact our support team at support@flexiloans.com or call 1800-XXX-XXXX.", styles['Normal']))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("Thank you for choosing FlexiLoans!", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Best Regards,<br/><b>FlexiLoans Team</b>", styles['Normal']))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("<i>This is a system-generated confirmation document.</i>", styles['Italic']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_offer_letter_pdf(applicant_data, emi_details=None):
    """Generate loan offer letter PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1f4788'), alignment=TA_CENTER, spaceAfter=30)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1f4788'), spaceAfter=12)
    
    elements.append(Paragraph("FLEXILOANS", title_style))
    elements.append(Paragraph("LOAN OFFER LETTER", ParagraphStyle('SubTitle', parent=styles['Heading2'], alignment=TA_CENTER, textColor=colors.green, fontSize=16)))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Offer Valid Until:</b> {(datetime.now() + timedelta(days=15)).strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(f"Dear <b>{applicant_data['name']}</b>,", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("Congratulations! We are delighted to offer you a loan from FlexiLoans based on your application and creditworthiness.", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Loan Offer Details", heading_style))
    
    loan_amount = applicant_data.get('loan_amount', 500000)
    if emi_details:
        loan_amount = emi_details.get('principal', loan_amount)
        interest_rate = emi_details.get('annual_rate', 12.0)
        tenure_months = emi_details.get('tenure_months', 24)
        monthly_emi = emi_details.get('emi', 0)
    else:
        interest_rate = 12.0
        tenure_months = 24
        monthly_emi = loan_amount * (interest_rate/1200) * ((1 + interest_rate/1200)**tenure_months) / (((1 + interest_rate/1200)**tenure_months) - 1)
    
    data = [
        ['Offer Details', ''],
        ['Application ID', applicant_data['application_id']],
        ['Applicant Name', applicant_data['name']],
        ['Loan Amount Offered', f"Rs.{loan_amount:,}"],
        ['Interest Rate', f"{interest_rate}% per annum"],
        ['Loan Tenure', f"{tenure_months} months ({tenure_months//12} years)"],
        ['Monthly EMI', f"Rs.{monthly_emi:,.0f}"],
        ['Processing Fee', f"Rs.{loan_amount * 0.02:,.0f} (2% of loan amount)"],
        ['Offer Validity', '15 days from date of issue']
    ]
    
    table = Table(data, colWidths=[2.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("<b>Terms and Conditions:</b>", heading_style))
    elements.append(Paragraph("1. This offer is subject to final verification of documents and information provided.", styles['Normal']))
    elements.append(Paragraph("2. The loan will be disbursed to your registered bank account within 2-3 business days of acceptance.", styles['Normal']))
    elements.append(Paragraph("3. EMI payments will commence from the month following disbursement.", styles['Normal']))
    elements.append(Paragraph("4. Prepayment is allowed after 6 months with no prepayment charges.", styles['Normal']))
    elements.append(Paragraph("5. Late payment charges of 2% per month will apply on overdue EMIs.", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("<b>How to Accept This Offer:</b>", heading_style))
    elements.append(Paragraph("1. Log in to your FlexiLoans account using your Application ID.", styles['Normal']))
    elements.append(Paragraph("2. Review the offer details and terms carefully.", styles['Normal']))
    elements.append(Paragraph("3. Click 'Accept Offer' to proceed with loan disbursement.", styles['Normal']))
    elements.append(Paragraph("4. Complete any pending KYC or documentation requirements.", styles['Normal']))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("We look forward to serving your financial needs!", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Best Regards,<br/><b>FlexiLoans Team</b>", styles['Normal']))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("<i>This is a system-generated offer letter. For queries, contact support@flexiloans.com</i>", styles['Italic']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_topup_offer_pdf(applicant_data, topup_data):
    """Generate Top-Up Loan Offer Letter PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#1f4788'), alignment=TA_CENTER, spaceAfter=20)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1f4788'), spaceAfter=10)

    elements.append(Paragraph("FLEXILOANS", title_style))
    elements.append(Paragraph("TOP-UP LOAN OFFER LETTER", ParagraphStyle('Sub', parent=styles['Heading2'], alignment=TA_CENTER, textColor=colors.HexColor('#e67e00'), fontSize=15)))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Valid Until:</b> {(datetime.now() + timedelta(days=15)).strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph(f"Dear <b>{applicant_data.get('name', 'Valued Customer')}</b>,", styles['Normal']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "Congratulations! Based on your excellent repayment history and credit profile, "
        "FlexiLoans is pleased to offer you a Top-Up Loan on your existing loan account.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Existing Loan Summary", heading_style))
    orig_data = [
        ['Field', 'Details'],
        ['Application ID', applicant_data.get('application_id', 'N/A')],
        ['Applicant Name', applicant_data.get('name', 'N/A')],
        ['Original Loan Amount', f"Rs.{applicant_data.get('loan_amount', 0):,}"],
        ['Original Tenure', f"{applicant_data.get('tenure_months', 24)} months"],
        ['Approved Date', applicant_data.get('approved_date', 'N/A')],
    ]
    t1 = Table(orig_data, colWidths=[2.5*inch, 4*inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8f4fd')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f4fd')]),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Top-Up Loan Details", heading_style))
    topup_amount = topup_data.get('amount', 100000)
    topup_rate = topup_data.get('rate', 12.5)
    topup_tenure = topup_data.get('tenure_months', 18)
    topup_emi = topup_data.get('emi', 0)
    total_interest = topup_data.get('total_interest', 0)

    topup_table_data = [
        ['Top-Up Details', ''],
        ['Top-Up Amount', f"Rs.{topup_amount:,}"],
        ['Interest Rate', f"{topup_rate}% per annum"],
        ['Tenure', f"{topup_tenure} months"],
        ['Monthly EMI', f"Rs.{topup_emi:,.0f}"],
        ['Total Interest', f"Rs.{total_interest:,.0f}"],
        ['Total Repayment', f"Rs.{topup_amount + total_interest:,.0f}"],
        ['Processing Fee', f"Rs.{topup_amount * 0.01:,.0f} (1% — existing customer benefit)"],
        ['Disbursement', 'Within 24 hours of acceptance'],
    ]
    t2 = Table(topup_table_data, colWidths=[2.5*inch, 4*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e67e00')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff3e0')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff3e0')]),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Exclusive Benefits for Existing Customers", heading_style))
    benefits = [
        "1% processing fee (vs 2% for new customers)",
        "Disbursement within 24 hours — no fresh documentation required",
        "No credit score re-check for loyal customers",
        "Flexible repayment — prepay anytime with zero penalty",
    ]
    for b in benefits:
        elements.append(Paragraph(f"• {b}", styles['Normal']))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Terms & Conditions", heading_style))
    elements.append(Paragraph("1. This offer is valid for 15 days from the date of issue.", styles['Normal']))
    elements.append(Paragraph("2. Final disbursement subject to internal credit policy.", styles['Normal']))
    elements.append(Paragraph("3. EMI auto-debit will be set up from your registered bank account.", styles['Normal']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<i>This is a system-generated top-up offer. Contact support@flexiloans.com for queries.</i>", styles['Italic']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

import re as _re

def _lookup_application(identifier, saved_applications, existing_applicants):
    """
    Unified lookup by application ID or phone number.
    Returns (source, data_dict) where source is 'saved' | 'existing' | None.
    data_dict has keys: applicant_data, documents_uploaded, customer_type, stage, phone, etc.
    """
    identifier = str(identifier).strip()

    # By application ID
    if identifier.startswith("FL-2026-"):
        if identifier in saved_applications:
            s = saved_applications[identifier]
            return "saved", {
                "applicant_data": s["applicant_data"],
                "documents_uploaded": s.get("documents_uploaded", {"pan": False, "bank": False}),
                "messages": s.get("messages", []),
                "stage": s.get("stage", "ELIGIBILITY_CHECK"),
                "customer_type": "NEW",
                "phone": s["applicant_data"].get("phone", ""),
            }
        for ph, ap in existing_applicants.items():
            if ap["application_id"] == identifier:
                return "existing", {
                    "applicant_data": dict(ap, phone=ph),
                    "documents_uploaded": {"pan": True, "bank": True},
                    "messages": [],
                    "stage": ap.get("stage", ""),
                    "customer_type": ap.get("customer_type", "IN_PROGRESS"),
                    "phone": ph,
                }
        return None, None

    # By phone number
    if _re.match(r'^\d{10}$', identifier):
        if identifier in existing_applicants:
            ap = existing_applicants[identifier]
            return "existing", {
                "applicant_data": dict(ap, phone=identifier),
                "documents_uploaded": {"pan": True, "bank": True},
                "messages": [],
                "stage": ap.get("stage", ""),
                "customer_type": ap.get("customer_type", "IN_PROGRESS"),
                "phone": identifier,
            }
        # Search saved_applications by phone
        for app_id, s in saved_applications.items():
            if s["applicant_data"].get("phone") == identifier:
                return "saved", {
                    "applicant_data": s["applicant_data"],
                    "documents_uploaded": s.get("documents_uploaded", {"pan": False, "bank": False}),
                    "messages": s.get("messages", []),
                    "stage": s.get("stage", "ELIGIBILITY_CHECK"),
                    "customer_type": "NEW",
                    "phone": identifier,
                }

    return None, None


def extract_profile_from_messages(messages):
    """Extract user profile fields from the full conversation history."""
    all_text = " ".join(m["content"] for m in messages)
    profile = {}

    phones = _re.findall(r'\b(\d{10})\b', all_text)
    if phones:
        profile["phone"] = phones[-1]

    app_ids = _re.findall(r'(FL-2026-\d+)', all_text)
    if app_ids:
        profile["application_id"] = app_ids[-1]

    # Only user messages for financial figures to avoid picking up bot examples
    user_text = " ".join(m["content"] for m in messages if m["role"] == "user")
    raw_nums = [int(n.replace(",", "")) for n in _re.findall(r'[\d,]+', user_text)
                if n.replace(",", "").isdigit() and len(n.replace(",", "")) >= 4]
    if raw_nums:
        turnovers = [n for n in raw_nums if n >= 500000]
        incomes   = [n for n in raw_nums if 10000 <= n < 500000]
        ages      = [n for n in raw_nums if 18 <= n <= 80]
        if turnovers: profile["turnover"] = max(turnovers)
        if incomes:   profile["income"]   = max(incomes)
        if ages:      profile["age"]      = ages[0]

    name_match = _re.search(
        r"(?:my name is|i am|i'm|name[:\s]+)\s*([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)",
        all_text, _re.IGNORECASE
    )
    if name_match:
        candidate = name_match.group(1).strip()
        # reject common false positives
        if candidate.lower() not in ("flexibot", "flexiloans", "india", "nbfc"):
            profile["name"] = candidate

    return profile


def build_application_context(messages, saved_applications, existing_applicants):
    """
    Scan conversation for all FL-2026-XXXX ids and 10-digit phones.
    Return a rich text block for the LLM system prompt + a list of detected actions.
    """
    all_text = " ".join(m["content"] for m in messages)

    app_ids = list(dict.fromkeys(_re.findall(r'FL-2026-\d+', all_text)))
    phones  = list(dict.fromkeys(_re.findall(r'\b(\d{10})\b', all_text)))

    context_lines = []
    nav_actions   = []
    seen_ids      = set()

    def _process(identifier):
        if identifier in seen_ids:
            return
        seen_ids.add(identifier)
        source, rec = _lookup_application(identifier, saved_applications, existing_applicants)
        if source is None:
            if identifier.startswith("FL-2026-"):
                context_lines.append(
                    f"\nAPPLICATION NOT FOUND — {identifier}: "
                    "No record in our system. Tell user clearly and ask to verify ID.\n"
                )
            return

        ad   = rec["applicant_data"]
        docs = rec["documents_uploaded"]
        ctype = rec["customer_type"]
        stage = rec["stage"]
        ph    = rec["phone"]

        if source == "saved":
            pan_ok  = docs.get("pan", False)
            bank_ok = docs.get("bank", False)
            missing = [d for d, ok in [("PAN Card", pan_ok), ("Bank Statement", bank_ok)] if not ok]
            if missing:
                stage_label = f"Documents Pending: {', '.join(missing)}"
                ns = (f"URGENT: Upload {' and '.join(missing)} immediately.\n"
                      "→ I will show a button to take you directly to document upload.")
                nav_actions.append({
                    "type": "resume_new_applicant",
                    "label": f"📋 Continue Application — Upload {' & '.join(missing)}",
                    "headline": f"Your application {ad.get('application_id','')} needs documents",
                    "saved": rec,
                })
            else:
                stage_label = "Under Verification"
                ns = "Both documents uploaded. Verification in progress (2-3 business days)."
                nav_actions.append({
                    "type": "resume_new_applicant",
                    "label": f"📄 View Application Status — {ad.get('application_id','')}",
                    "headline": "View your application progress",
                    "saved": rec,
                })
            context_lines.append(f"""
APPLICATION FOUND — {ad.get('application_id','')} (Session):
  Name: {ad.get('name','N/A')} | Phone: {ph} | Age: {ad.get('age','N/A')}
  Annual Turnover: Rs.{ad.get('turnover',0):,} | Monthly Income: Rs.{ad.get('income',0):,}
  PAN Card: {'Uploaded' if pan_ok else 'PENDING'}  Bank Statement: {'Uploaded' if bank_ok else 'PENDING'}
  Stage: {stage_label}
  Next Steps: {ns}
""")

        elif source == "existing":
            if ctype == "APPROVED":
                loan_amt = ad.get("loan_amount", 0)
                disb     = ad.get("disbursement_date", "N/A")
                income   = ad.get("monthly_income", ad.get("income", 75000))
                max_topup = int(min(loan_amt * 0.75, income * 3)) if loan_amt else 100000
                ns = (f"APPROVED! Loan Rs.{loan_amt:,} — disbursement: {disb}.\n"
                      f"Eligible for Top-Up up to Rs.{max_topup:,}. Disbursement in 24 hours, no fresh docs needed.")
                nav_actions.append({
                    "type": "goto_existing_customer",
                    "label": f"🎉 View Approved Loan — {ad.get('name','')}",
                    "headline": f"{ad.get('name','')} — Loan Approved",
                    "phone": ph, "data": ad,
                })
                nav_actions.append({
                    "type": "goto_topup",
                    "label": f"🔄 Apply for Top-Up up to Rs.{max_topup:,}",
                    "headline": f"Instant Top-Up — Rs.{max_topup:,} available in 24 hrs",
                    "phone": ph, "data": ad,
                })
            elif ctype == "IN_PROGRESS":
                pending = ad.get("pending_documents", [])
                if pending:
                    ns = f"ACTION REQUIRED: Submit {', '.join(pending)}. Use Existing Applicant stream."
                else:
                    ns = f"Under review. Estimated completion: {ad.get('estimated_completion','soon')}."
                nav_actions.append({
                    "type": "goto_existing_customer",
                    "label": f"🔍 Track Application — {ad.get('name','')}",
                    "headline": f"{ad.get('name','')} — Application In Progress",
                    "phone": ph, "data": ad,
                })
            elif ctype == "REJECTED":
                ns = (f"REJECTED. Reason: {ad.get('rejection_reason','N/A')}. "
                      f"Eligible to reapply after: {ad.get('reapply_after_date','N/A')}.")
                nav_actions.append({
                    "type": "goto_existing_customer",
                    "label": f"❌ View Rejection Details — {ad.get('name','')}",
                    "headline": f"{ad.get('name','')} — Application Rejected",
                    "phone": ph, "data": ad,
                })
            else:
                ns = "Contact support@flexiloans.com."

            context_lines.append(f"""
APPLICATION FOUND — {ad.get('application_id','')} (Existing Customer):
  Name: {ad.get('name','N/A')} | Phone: {ph} | Stage: {stage}
  Status: {ctype}
  Submitted: {ad.get('submitted_date','N/A')}
  Next Steps: {ns}
""")

    for aid in app_ids:
        _process(aid)
    for ph in phones:
        _process(ph)

    return "\n".join(context_lines), nav_actions


def _switch_stream(target):
    """Flip the sidebar radio + stream + set nav flag, then rerun."""
    st.session_state.flexibot_nav      = True
    st.session_state.workflow_stream   = target
    st.session_state.stream_selector   = target
    st.session_state.pending_nav       = None
    st.rerun()


def flexibot_navigate(action):
    """Pre-populate session state then switch to the target stream."""
    atype = action["type"]

    if atype == "resume_new_applicant":
        rec = action["saved"]
        st.session_state.applicant_data       = rec["applicant_data"]
        st.session_state.documents_uploaded   = rec.get("documents_uploaded", {"pan": False, "bank": False})
        st.session_state.eligibility_passed   = True
        st.session_state.phone_verified       = True
        st.session_state.chat_active          = True
        st.session_state.demo_approval_time   = None
        st.session_state.demo_approved        = False
        # Keep FlexiBot history so user sees the conversation
        fb_msgs = st.session_state.get("flexibot_messages", [])
        st.session_state.messages = fb_msgs if fb_msgs else rec.get("messages", [])
        _switch_stream("New Applicant")

    elif atype in ("goto_existing_customer", "goto_topup", "goto_existing_by_appid"):
        ap = action.get("data", action.get("applicant_data", {}))
        ph = action.get("phone", ap.get("phone", ""))
        ap_copy = dict(ap)
        ap_copy["phone"] = ph
        st.session_state.applicant_data  = ap_copy
        st.session_state.phone_verified  = True
        st.session_state.chat_active     = True
        st.session_state.app_number_collected = True
        ctype = ap.get("customer_type", "IN_PROGRESS")
        st.session_state.current_stage   = "APPROVED" if ctype == "APPROVED" else "VERIFICATION"
        if atype == "goto_topup":
            st.session_state.topup_active = True
        fb_msgs = st.session_state.get("flexibot_messages", [])
        st.session_state.messages = fb_msgs if fb_msgs else []
        _switch_stream("Existing Applicant")

    elif atype == "goto_new_applicant_prefill":
        profile = action.get("profile", {})
        # If all 5 fields collected → skip form, go straight to doc upload
        required = {"name", "phone", "age", "income", "turnover"}
        if required.issubset(profile.keys()) and len(str(profile.get("phone","")))==10:
            app_id = f"FL-2026-{random.randint(1000,9999)}"
            ad = {
                "name": profile["name"],
                "phone": str(profile["phone"]),
                "age": int(profile["age"]),
                "income": int(profile["income"]),
                "turnover": int(profile["turnover"]),
                "application_id": app_id,
            }
            st.session_state.applicant_data     = ad
            st.session_state.eligibility_passed = True
            st.session_state.phone_verified     = True
            st.session_state.chat_active        = True
            st.session_state.demo_approval_time = None
            st.session_state.demo_approved      = False
            st.session_state.documents_uploaded = {"pan": False, "bank": False}
            st.session_state.saved_applications[app_id] = {
                "applicant_data": ad,
                "phone": str(profile["phone"]),
                "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "documents_uploaded": {"pan": False, "bank": False},
                "messages": [],
                "stage": "ELIGIBILITY_CHECK",
            }
            fb_msgs = st.session_state.get("flexibot_messages", [])
            st.session_state.messages = fb_msgs if fb_msgs else []
        else:
            st.session_state.flexibot_gathered = profile
        _switch_stream("New Applicant")


def render_topup_section(applicant_data, key_prefix=""):
    """Render Top-Up Loan section for approved customers."""
    st.markdown("---")
    st.subheader("🔄 Top-Up Loan")
    st.info("As an approved FlexiLoans customer, you are eligible for an instant top-up on your existing loan.")

    original_loan = applicant_data.get("loan_amount", 500000)
    monthly_income = applicant_data.get("income", applicant_data.get("monthly_income", 75000))

    # Compute max top-up: lesser of 75% of original loan or 3x monthly income
    max_topup = int(min(original_loan * 0.75, monthly_income * 3))
    max_topup = max(max_topup, 100000)

    if not st.session_state.topup_active and not st.session_state.topup_approved:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Original Loan:** Rs.{original_loan:,}  |  **Max Top-Up Eligible:** Rs.{max_topup:,}")
            st.caption("Processing fee: 1% only (existing customer benefit) • Disbursed within 24 hours • Zero additional documentation")
        with col2:
            if st.button("Apply for Top-Up", key=f"{key_prefix}topup_apply_btn", type="primary"):
                st.session_state.topup_active = True
                st.rerun()

    elif st.session_state.topup_active and not st.session_state.topup_approved:
        st.markdown("### 💰 Configure Your Top-Up")
        with st.form(f"{key_prefix}topup_form"):
            topup_amount = st.slider(
                "Top-Up Amount (Rs.)",
                min_value=50000,
                max_value=max_topup,
                value=min(200000, max_topup),
                step=25000,
                format="Rs.%d"
            )
            topup_tenure = st.select_slider(
                "Repayment Tenure",
                options=[6, 12, 18, 24],
                value=18,
                format_func=lambda x: f"{x} months"
            )
            topup_rate = applicant_data.get("interest_rate", 12.0) + 0.5
            emi_res = calculate_emi(topup_amount, topup_rate, topup_tenure)

            st.markdown(f"**Estimated EMI:** Rs.{emi_res['emi']:,.0f}/month  |  "
                        f"**Rate:** {topup_rate}% p.a.  |  "
                        f"**Total Interest:** Rs.{emi_res['total_interest']:,.0f}")

            submitted = st.form_submit_button("Confirm & Apply for Top-Up", type="primary")
            cancel = st.form_submit_button("Cancel")

            if submitted:
                st.session_state.topup_data = {
                    "amount": topup_amount,
                    "rate": topup_rate,
                    "tenure_months": topup_tenure,
                    "emi": emi_res["emi"],
                    "total_interest": emi_res["total_interest"],
                }
                st.session_state.topup_approval_time = datetime.now()
                st.rerun()
            if cancel:
                st.session_state.topup_active = False
                st.rerun()

    elif st.session_state.topup_data and not st.session_state.topup_approved:
        # 3-second countdown then auto-approve
        elapsed = (datetime.now() - st.session_state.topup_approval_time).total_seconds()
        if elapsed < 3:
            remaining = int(3 - elapsed)
            st.info(f"⚡ Processing your top-up request... approved in {remaining} second{'s' if remaining != 1 else ''}.")
            time.sleep(1)
            st.rerun()
        else:
            st.session_state.topup_approved = True
            td = st.session_state.topup_data
            st.session_state.messages.append({
                "role": "model",
                "content": (
                    f"Great news! Your Top-Up Loan of Rs.{td['amount']:,} has been APPROVED! "
                    f"EMI: Rs.{td['emi']:,.0f}/month for {td['tenure_months']} months. "
                    "Disbursement within 24 hours. Download your Top-Up Offer Letter below!"
                )
            })
            st.balloons()
            st.rerun()

    if st.session_state.topup_approved:
        td = st.session_state.topup_data
        st.success("✅ TOP-UP LOAN APPROVED!")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Top-Up Amount", f"Rs.{td['amount']:,}")
        with col2:
            st.metric("Monthly EMI", f"Rs.{td['emi']:,.0f}")
        with col3:
            st.metric("Tenure", f"{td['tenure_months']} months")
        with col4:
            st.metric("Disbursement", "Within 24 hrs")

        topup_pdf = generate_topup_offer_pdf(applicant_data, td)
        st.download_button(
            label="📥 Download Top-Up Offer Letter",
            data=topup_pdf,
            file_name=f"FlexiLoans_TopUp_Offer_{applicant_data.get('application_id','')}.pdf",
            mime="application/pdf",
            key=f"{key_prefix}topup_pdf_btn"
        )
        st.info("The top-up amount will be credited to your registered bank account within 24 hours.")

# Main Panel
st.title("Smart Onboarding Engine")

# Render progress bar in sidebar
if st.session_state.workflow_stream:
    render_progress_bar()

# Render EMI Calculator in sidebar
render_emi_calculator()

# Render Financial Guidance in sidebar
render_financial_guidance()

# Render Smart Recommendations in sidebar
def generate_smart_recommendations(applicant_data, credit_score=700):
    """Generate personalized loan and product recommendations"""
    
    monthly_income = applicant_data.get('income', 50000)
    annual_turnover = applicant_data.get('turnover', 12000000)
    age = applicant_data.get('age', 35)
    
    recommendations = {
        "optimal_loan": {},
        "tenure": {},
        "cross_sell": [],
        "upsell": {},
        "next_actions": []
    }
    
    # 1. OPTIMAL LOAN AMOUNT
    max_emi = monthly_income * 0.40
    interest_rate = 12.0
    tenure_months = 24
    monthly_rate = interest_rate / (12 * 100)
    optimal_loan_amount = max_emi * (((1 + monthly_rate) ** tenure_months) - 1) / (monthly_rate * ((1 + monthly_rate) ** tenure_months))
    
    if credit_score >= 750:
        optimal_loan_amount *= 1.2
        interest_rate = 10.5
    elif credit_score >= 700:
        optimal_loan_amount *= 1.1
        interest_rate = 11.5
    elif credit_score < 650:
        optimal_loan_amount *= 0.8
        interest_rate = 14.0
    
    optimal_loan_amount = min(optimal_loan_amount, annual_turnover * 0.25)
    optimal_loan_amount = max(optimal_loan_amount, 100000)
    optimal_loan_amount = min(optimal_loan_amount, 5000000)
    
    recommendations["optimal_loan"] = {
        "amount": round(optimal_loan_amount, -3),
        "interest_rate": interest_rate,
        "reasoning": f"Based on 40% EMI-to-income ratio",
        "max_emi": round(max_emi, 0)
    }
    
    # 2. TENURE RECOMMENDATION
    if age < 30:
        recommended_tenure = 36
        tenure_reason = "Longer tenure for lower EMI"
    elif age < 45:
        recommended_tenure = 24
        tenure_reason = "Balanced tenure"
    else:
        recommended_tenure = 12
        tenure_reason = "Shorter tenure recommended"
    
    emi_result = calculate_emi(optimal_loan_amount, interest_rate, recommended_tenure)
    
    recommendations["tenure"] = {
        "months": recommended_tenure,
        "years": recommended_tenure / 12,
        "reasoning": tenure_reason,
        "monthly_emi": emi_result["emi"],
        "total_interest": emi_result["total_interest"]
    }
    
    # 3. CROSS-SELL
    cross_sell_products = []
    
    insurance_premium = optimal_loan_amount * 0.005
    cross_sell_products.append({
        "product": "Loan Protection Insurance",
        "description": "Covers loan in emergencies",
        "cost": f"₹{insurance_premium:,.0f}/year",
        "benefit": "Peace of mind",
        "priority": "High",
        "icon": "🛡️"
    })
    
    if credit_score >= 700:
        credit_limit = min(monthly_income * 3, 500000)
        cross_sell_products.append({
            "product": "Premium Credit Card",
            "description": "Rewards credit card",
            "cost": "Free first year",
            "benefit": f"Limit ₹{credit_limit:,.0f}, 2% cashback",
            "priority": "Medium",
            "icon": "💳"
        })
    
    if annual_turnover >= 20000000:
        credit_line = annual_turnover * 0.15
        cross_sell_products.append({
            "product": "Business Credit Line",
            "description": "Flexible business credit",
            "cost": "Interest on usage only",
            "benefit": f"Up to ₹{credit_line:,.0f}",
            "priority": "High",
            "icon": "💼"
        })
    
    recommendations["cross_sell"] = cross_sell_products
    
    # 4. UPSELL
    if credit_score >= 750 and monthly_income >= 75000:
        higher_loan = optimal_loan_amount * 1.5
        higher_emi = calculate_emi(higher_loan, interest_rate, recommended_tenure)
        
        recommendations["upsell"] = {
            "qualified": True,
            "higher_amount": round(higher_loan, -3),
            "additional_amount": round(higher_loan - optimal_loan_amount, -3),
            "new_emi": higher_emi["emi"],
            "reasoning": "Excellent credit qualifies for more"
        }
    else:
        recommendations["upsell"] = {"qualified": False}
    
    # 5. NEXT ACTIONS
    next_actions = [
        {
            "action": "Complete Application",
            "priority": "High",
            "icon": "🎯",
            "description": "Fill eligibility form",
            "time_estimate": "2 min"
        },
        {
            "action": "Upload Documents",
            "priority": "High",
            "icon": "📄",
            "description": "PAN & Bank Statement",
            "time_estimate": "2 min"
        }
    ]
    
    if credit_score < 750:
        next_actions.append({
            "action": "Improve Credit Score",
            "priority": "Medium",
            "icon": "📈",
            "description": f"From {credit_score} to 750+",
            "time_estimate": "3-6 months"
        })
    
    recommendations["next_actions"] = next_actions
    
    return recommendations

def render_smart_recommendations():
    """Render Smart Recommendation Engine"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Smart Recommendations")
    
    with st.sidebar.expander("AI Loan Advisor", expanded=False):
        rec_income = st.number_input("Income (₹)", min_value=10000, value=50000, step=5000, key="rec_income")
        rec_turnover = st.number_input("Turnover (₹)", min_value=1000000, value=12000000, step=1000000, key="rec_turnover")
        rec_age = st.number_input("Age", min_value=21, max_value=65, value=35, key="rec_age")
        rec_credit = st.slider("Credit Score", 300, 900, 700, 10, key="rec_credit")
        
        if st.button("🔮 Generate", key="gen_rec", type="primary"):
            temp_data = {'income': rec_income, 'turnover': rec_turnover, 'age': rec_age}
            st.session_state.smart_recommendations = generate_smart_recommendations(temp_data, rec_credit)
            st.session_state.recommendations_generated = True
        
        if st.session_state.recommendations_generated and st.session_state.smart_recommendations:
            rec = st.session_state.smart_recommendations
            
            st.markdown("### 💰 Optimal Loan")
            st.metric("Amount", f"₹{rec['optimal_loan']['amount']:,.0f}")
            st.caption(f"@ {rec['optimal_loan']['interest_rate']}% p.a.")
            
            st.markdown("### ⏱️ Tenure")
            st.metric("Best", f"{rec['tenure']['years']:.0f} years")
            st.write(f"EMI: ₹{rec['tenure']['monthly_emi']:,.0f}")
            
            if rec['cross_sell']:
                st.markdown("### 🎁 Products")
                for p in rec['cross_sell'][:2]:
                    st.write(f"{p['icon']} **{p['product']}**")
                    st.caption(p['benefit'])
            
            if rec['upsell']['qualified']:
                st.markdown("### 🚀 Upsell")
                st.success(f"Qualify for ₹{rec['upsell']['higher_amount']:,.0f}!")
            
            st.markdown("### ✅ Next Steps")
            for a in rec['next_actions'][:3]:
                st.write(f"{a['icon']} {a['action']}")

render_smart_recommendations()

# STREAM A: NEW APPLICANT
if st.session_state.workflow_stream == "New Applicant":
    
    if not st.session_state.eligibility_passed:
        st.subheader("📝 New Application Form")
        st.info("Complete the form below to check your eligibility")

        # Pre-fill from FlexiBot if data was gathered in chat
        _fg = st.session_state.flexibot_gathered
        if _fg:
            st.success("💡 FlexiBot pre-filled your profile from the chat. Review and submit.")

        with st.form("eligibility_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Applicant Name*", value=_fg.get("name", ""), placeholder="Enter full name")
                phone = st.text_input("Phone Number*", value=_fg.get("phone", ""), placeholder="10-digit mobile number")
                age = st.number_input("Age*", min_value=18, max_value=100, value=int(_fg.get("age", 30)))

            with col2:
                turnover = st.number_input("Gross Annual Turnover (₹)*", min_value=0, value=int(_fg.get("turnover", 15000000)), step=100000)
                income = st.number_input("Net Monthly Income (₹)*", min_value=0, value=int(_fg.get("income", 75000)), step=5000)
            
            submitted = st.form_submit_button("🔍 Check Eligibility")
            
            if submitted:
                errors = []
                
                if not name or not phone:
                    errors.append("Name and Phone Number are required")
                elif len(phone) != 10 or not phone.isdigit():
                    errors.append("Phone Number must be exactly 10 digits")
                
                if age < ELIGIBILITY_RULES["min_age"]:
                    errors.append(f"Age below minimum limit of {ELIGIBILITY_RULES['min_age']} years")
                elif age > ELIGIBILITY_RULES["max_age"]:
                    errors.append(f"Age above maximum limit of {ELIGIBILITY_RULES['max_age']} years")
                
                if turnover < ELIGIBILITY_RULES["min_annual_turnover"]:
                    errors.append(f"Turnover below limit of ₹{ELIGIBILITY_RULES['min_annual_turnover']:,}")
                
                if income < ELIGIBILITY_RULES["min_monthly_income"]:
                    errors.append(f"Monthly Income below limit of ₹{ELIGIBILITY_RULES['min_monthly_income']:,}")
                
                if errors:
                    st.error("❌ Eligibility Check Failed")
                    for error in errors:
                        st.warning(f"• {error}")
                else:
                    app_id = f"FL-2026-{random.randint(1000, 9999)}"
                    st.session_state.applicant_data = {
                        "name": name,
                        "phone": phone,
                        "age": age,
                        "turnover": turnover,
                        "income": income,
                        "application_id": app_id
                    }
                    st.session_state.eligibility_passed = True
                    st.session_state.phone_verified = True
                    st.session_state.current_stage = "ELIGIBILITY_CHECK"
                    st.session_state.stage_timestamps["ELIGIBILITY_CHECK"] = datetime.now()
                    # Register application so it can be looked up in Stream B
                    st.session_state.saved_applications[app_id] = {
                        "applicant_data": st.session_state.applicant_data,
                        "phone": phone,
                        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "documents_uploaded": {"pan": False, "bank": False},
                        "messages": [],
                        "stage": "ELIGIBILITY_CHECK"
                    }
                    st.success(f"✅ Eligibility Passed! Application ID: {app_id}")
                    st.rerun()
    
    else:
        st.success(f"✅ Eligibility Approved - Application ID: {st.session_state.applicant_data['application_id']}")
        
        # Show progress milestone
        st.info("📍 Current Stage: Document Upload")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Applicant", st.session_state.applicant_data['name'])
            st.metric("Phone", st.session_state.applicant_data['phone'])
        with col2:
            st.metric("Age", st.session_state.applicant_data['age'])
            st.metric("Application ID", st.session_state.applicant_data['application_id'])
        
        # Download application form button
        pdf_buffer = generate_application_pdf(st.session_state.applicant_data)
        st.download_button(
            label="📄 Download Application Form PDF",
            data=pdf_buffer,
            file_name=f"FlexiLoans_Application_{st.session_state.applicant_data['application_id']}.pdf",
            mime="application/pdf",
            key="download_app_form"
        )
        
        st.markdown("---")
        st.subheader("📎 Document Upload Workspace")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.documents_uploaded["pan"]:
                if st.button("📄 Upload PAN Card", key="pan_upload"):
                    st.session_state.documents_uploaded["pan"] = True
                    st.session_state.messages.append({
                        "role": "user",
                        "content": "[PAN Card uploaded]"
                    })
                    if "PAN_UPLOAD" not in st.session_state.stage_timestamps:
                        st.session_state.stage_timestamps["PAN_UPLOAD"] = datetime.now()
                    st.rerun()
            else:
                st.success("✅ PAN Card Saved")
        
        with col2:
            if not st.session_state.documents_uploaded["bank"]:
                if st.button("🏦 Upload Bank Statement", key="bank_upload"):
                    st.session_state.documents_uploaded["bank"] = True
                    st.session_state.messages.append({
                        "role": "user",
                        "content": "[Bank Statement uploaded]"
                    })
                    if "BANK_UPLOAD" not in st.session_state.stage_timestamps:
                        st.session_state.stage_timestamps["BANK_UPLOAD"] = datetime.now()
                    
                    # Check if both documents uploaded
                    if st.session_state.documents_uploaded["pan"] and st.session_state.documents_uploaded["bank"]:
                        st.session_state.current_stage = "VERIFICATION"
                        st.session_state.stage_timestamps["DOCUMENTS_COMPLETE"] = datetime.now()
                        # Start 5-second demo approval countdown
                        if st.session_state.demo_approval_time is None:
                            st.session_state.demo_approval_time = datetime.now()
                        st.balloons()

                    st.rerun()
            else:
                st.success("✅ Bank Statement Saved")

        # Show completion message if both docs uploaded
        if st.session_state.documents_uploaded["pan"] and st.session_state.documents_uploaded["bank"]:
            # ── DEMO AUTO-APPROVAL after 5 seconds ──────────────────────────
            if st.session_state.demo_approval_time is None:
                st.session_state.demo_approval_time = datetime.now()

            elapsed = (datetime.now() - st.session_state.demo_approval_time).total_seconds()

            if not st.session_state.demo_approved and elapsed < 5:
                remaining = int(5 - elapsed)
                st.success("🎉 Both documents uploaded! Instant verification in progress...")
                st.info(f"⏳ Verifying your application... auto-approving in {remaining} second{'s' if remaining != 1 else ''}.")
                time.sleep(1)
                st.rerun()

            elif not st.session_state.demo_approved and elapsed >= 5:
                st.session_state.demo_approved = True
                st.session_state.current_stage = "APPROVED"
                st.session_state.applicant_data["customer_type"] = "APPROVED"
                st.session_state.applicant_data["approved_date"] = datetime.now().strftime("%Y-%m-%d")
                st.session_state.applicant_data["disbursement_date"] = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
                # Compute smart loan amount
                income = st.session_state.applicant_data.get("income", 75000)
                turnover = st.session_state.applicant_data.get("turnover", 15000000)
                reco = generate_smart_recommendations(st.session_state.applicant_data)
                loan_amount = int(reco["optimal_loan"]["amount"])
                st.session_state.applicant_data["loan_amount"] = loan_amount
                st.session_state.applicant_data["interest_rate"] = reco["optimal_loan"]["interest_rate"]
                st.session_state.applicant_data["tenure_months"] = reco["tenure"]["months"]
                st.session_state.applicant_data["monthly_emi"] = round(reco["tenure"]["monthly_emi"], 0)
                st.session_state.messages.append({
                    "role": "model",
                    "content": (
                        f"Congratulations {st.session_state.applicant_data['name']}! "
                        f"Your loan application {st.session_state.applicant_data['application_id']} has been APPROVED! "
                        f"Loan Amount: Rs.{loan_amount:,} | EMI: Rs.{reco['tenure']['monthly_emi']:,.0f}/month. "
                        "Your offer letter is ready to download below!"
                    )
                })
                st.balloons()
                st.rerun()

            if st.session_state.demo_approved:
                st.success("✅ APPLICATION APPROVED!")
                st.markdown("---")
                st.subheader("🎉 Congratulations! Your Loan is Approved")

                app = st.session_state.applicant_data
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Loan Amount", f"Rs.{app.get('loan_amount',500000):,}")
                with col2:
                    st.metric("Monthly EMI", f"Rs.{app.get('monthly_emi',0):,.0f}")
                with col3:
                    st.metric("Disbursement", app.get("disbursement_date", "In 2 days"))

                st.markdown("---")
                st.subheader("📄 Your Documents")

                col_a, col_b = st.columns(2)
                with col_a:
                    emi_details = {
                        "principal": app.get("loan_amount", 500000),
                        "annual_rate": app.get("interest_rate", 12.0),
                        "tenure_months": app.get("tenure_months", 24),
                        "emi": app.get("monthly_emi", 0)
                    }
                    offer_pdf = generate_offer_letter_pdf(app, emi_details)
                    st.download_button(
                        label="📥 Download Offer Letter",
                        data=offer_pdf,
                        file_name=f"FlexiLoans_Offer_Letter_{app['application_id']}.pdf",
                        mime="application/pdf",
                        key="stream_a_offer_letter"
                    )
                with col_b:
                    sanction_pdf = generate_sanction_letter_pdf(app)
                    st.download_button(
                        label="📥 Download Sanction Letter",
                        data=sanction_pdf,
                        file_name=f"FlexiLoans_Sanction_Letter_{app['application_id']}.pdf",
                        mime="application/pdf",
                        key="stream_a_sanction_letter"
                    )
                st.info("The loan amount will be disbursed to your registered bank account within 2 business days.")
                render_topup_section(st.session_state.applicant_data, key_prefix="stream_a_")
                # Skip further doc upload UI — application is done
                st.stop()
        
        if not st.session_state.chat_active and (st.session_state.documents_uploaded["pan"] or st.session_state.documents_uploaded["bank"]):
            st.session_state.chat_active = True
            st.session_state.messages.append({
                "role": "model",
                "content": f"Hello {st.session_state.applicant_data['name']}! I'm FlexiBot. I see you've started uploading documents. Let me help you complete your application smoothly. Please note your Application Number: {st.session_state.applicant_data['application_id']} for future reference. Do you have any questions about the process?"
            })
            st.session_state.app_number_collected = True
        
        if st.session_state.chat_active:
            st.markdown("---")
            st.subheader("💬 Application Assistant")

            if not client:
                st.error("Please enter your Gemini API Key in the sidebar to use FlexiBot.")
                st.stop()

            for message in st.session_state.messages:
                avatar = "🤝" if message["role"] == "model" else "👤"
                with st.chat_message(message["role"], avatar=avatar):
                    st.write(message["content"])
            
            uploaded_file = st.file_uploader("📎 Attach Document (Optional)", type=["pdf", "jpg", "jpeg", "png"], key="doc_uploader")
            
            # Validate uploaded file
            if uploaded_file is not None:
                validation_result = validate_document(uploaded_file, "Document")
                render_document_validation_feedback(validation_result)
            
            if user_input := st.chat_input("Type your message..."):
                message_content = user_input

                # Check for save/exit intent
                user_input_lower = user_input.lower()
                save_keywords = ["save", "exit", "leave", "pause", "continue later", "stop", "quit"]
                if any(keyword in user_input_lower for keyword in save_keywords):
                    # Save current application state
                    app_id = st.session_state.applicant_data['application_id']
                    st.session_state.saved_applications[app_id] = {
                        "applicant_data": st.session_state.applicant_data.copy(),
                        "documents_uploaded": st.session_state.documents_uploaded.copy(),
                        "messages": st.session_state.messages.copy(),
                        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                
                # Check if file is uploaded
                if uploaded_file is not None:
                    file_name = uploaded_file.name
                    message_content += f" [Attached: {file_name}]"
                    
                    # Validate document
                    validation = validate_document(uploaded_file, "Uploaded")
                    if validation and validation["valid"]:
                        message_content += " ✅"
                    else:
                        message_content += " ⚠️"
                    
                    # Detect document type from message
                    if "pan" in user_input_lower and not st.session_state.documents_uploaded["pan"]:
                        st.session_state.documents_uploaded["pan"] = True
                        st.session_state.document_validation["pan"] = validation
                    elif "bank" in user_input_lower and not st.session_state.documents_uploaded["bank"]:
                        st.session_state.documents_uploaded["bank"] = True
                        st.session_state.document_validation["bank"] = validation
                
                # Show EMI terms if applied
                if st.session_state.apply_with_emi_terms and st.session_state.emi_calculation:
                    emi_info = st.session_state.emi_calculation
                    message_content += f" [EMI Terms: ₹{emi_info['emi']:,.0f}/month for {emi_info['tenure_months']} months]"
                
                st.session_state.messages.append({"role": "user", "content": message_content})
                
                with st.chat_message("user", avatar="👤"):
                    st.write(message_content)
                
                with st.spinner("FlexiBot responding..."):
                    # Detect document upload in message
                    doc_detected = ""
                    user_input_lower = user_input.lower()

                    # Check for save/exit intent
                    save_intent = False
                    save_keywords = ["save", "exit", "leave", "pause", "continue later", "stop", "quit"]
                    if any(keyword in user_input_lower for keyword in save_keywords):
                        save_intent = True
                    
                    if uploaded_file is not None:
                        if "pan" in user_input_lower:
                            doc_detected = "PAN Card"
                            if not st.session_state.documents_uploaded["pan"]:
                                st.session_state.documents_uploaded["pan"] = True
                        elif "bank" in user_input_lower or "statement" in user_input_lower:
                            doc_detected = "Bank Statement"
                            if not st.session_state.documents_uploaded["bank"]:
                                st.session_state.documents_uploaded["bank"] = True
                    
                    # Include EMI terms in context if available
                    emi_context = ""
                    if st.session_state.emi_calculation:
                        emi_info = st.session_state.emi_calculation
                        emi_context = f"\n\nCUSTOMER EMI PREFERENCE: ₹{emi_info['emi']:,.0f}/month for {emi_info['tenure_months']} months (Loan: ₹{emi_info['principal']:,.0f} @ {emi_info['annual_rate']}% p.a.)"
                    
                    system_instruction = f"""
You are 'FlexiBot', an AI assistant for FlexiLoans helping {st.session_state.applicant_data['name']} (Application ID: {st.session_state.applicant_data['application_id']}) complete their loan application.

CURRENT STATUS:
- PAN Card: {'Uploaded ✅' if st.session_state.documents_uploaded['pan'] else 'Pending ⏳'}
- Bank Statement: {'Uploaded ✅' if st.session_state.documents_uploaded['bank'] else 'Pending ⏳'}
{emi_context}

{f"DOCUMENT JUST UPLOADED: {doc_detected}" if doc_detected else ""}
{f"USER WANTS TO SAVE AND EXIT" if save_intent else ""}

YOUR ROLE:
1. If a document was just uploaded, acknowledge it enthusiastically and confirm it's saved
2. If the user mentions uploading a document but you don't see which one, politely ask them to specify (PAN Card or Bank Statement)
3. IMPORTANT: Always remind them to save their Application Number: {st.session_state.applicant_data['application_id']} for future reference
4. If documents are pending, actively guide them to upload through chat by saying "You can attach your [document name] right here in the chat using the attachment button"
5. **EMI TERMS**: If customer has calculated EMI terms, acknowledge and confirm: "I see you're interested in ₹X/month EMI. We'll process your application with these preferred terms."
6. **SAVE & EXIT HANDLING**: If user wants to save/exit/pause/leave/continue later:
   - Confirm: "I've saved your application progress. Your Application ID is {st.session_state.applicant_data['application_id']}"
   - Inform: "You can continue anytime by selecting 'Existing Applicant' and entering your Application ID and phone number"
   - Summarize: What's completed and what's pending
   - Reassure: "Your data is safely stored and you can resume exactly where you left off"
7. Guide the user through any remaining steps
8. Answer questions about document requirements, eligibility, or loan terms
9. Clear any doubts about data safety and compliance
10. Explain the application process in simple terms
11. Actively drive the conversation toward completing document upload
12. Be encouraging and supportive

If both documents are uploaded, congratulate them and explain next steps (verification will take 2-3 business days, approval timeline).
Keep responses concise and action-oriented.

"""
                    
                    chat_history = []
                    for msg in st.session_state.messages[:-1]:
                        if msg["role"] == "user":
                            chat_history.append(types.Content(role="user", parts=[types.Part.from_text(text=msg["content"])]))
                        else:
                            chat_history.append(types.Content(role="model", parts=[types.Part.from_text(text=msg["content"])]))
                    
                    chat_session = client.chats.create(
                        model="gemini-2.5-flash",
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.3
                        ),
                        history=chat_history
                    )
                    
                    response = chat_session.send_message(user_input)
                
                st.session_state.messages.append({"role": "model", "content": response.text})
                
                with st.chat_message("model", avatar="🤝"):
                    st.write(response.text)
                
                st.rerun()

# STREAM B: EXISTING APPLICANT
elif st.session_state.workflow_stream == "Existing Applicant":
    
    if not st.session_state.chat_active:
        st.subheader("🔍 Application Status Lookup")
        st.info("Enter your details to check your application status")
        
        # First ask for application number
        if not st.session_state.app_number_collected:
            with st.form("app_number_form"):
                app_id = st.text_input("Application ID*", placeholder="FL-2026-XXXX")
                app_number_submitted = st.form_submit_button("Continue")
                
                if app_number_submitted:
                    if app_id and app_id.startswith("FL-2026-"):
                        st.session_state.applicant_data["application_id"] = app_id
                        st.session_state.app_number_collected = True
                        st.success("✅ Application ID recorded")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Application ID format. Must start with FL-2026-")
        
        else:
            # Then ask for phone verification
            with st.form("phone_verification_form"):
                st.info(f"Application ID: {st.session_state.applicant_data.get('application_id', 'N/A')}")
                phone = st.text_input("Phone Number* (10 digits)", placeholder="10-digit mobile number")
                
                phone_submitted = st.form_submit_button("🔎 Retrieve Application")
                
                if phone_submitted:
                    if len(phone) != 10 or not phone.isdigit():
                        st.error("❌ Phone number must be exactly 10 digits")
                    else:
                        app_id = st.session_state.applicant_data.get("application_id")
                        
                        # Check saved applications first
                        if app_id in st.session_state.saved_applications:
                            saved_app = st.session_state.saved_applications[app_id]
                            if saved_app["applicant_data"]["phone"] == phone:
                                # Restore saved application
                                st.session_state.applicant_data = saved_app["applicant_data"]
                                st.session_state.documents_uploaded = saved_app["documents_uploaded"]
                                st.session_state.messages = saved_app["messages"]
                                st.session_state.chat_active = True
                                st.session_state.phone_verified = True
                                
                                # Restore stage
                                if st.session_state.documents_uploaded["pan"] and st.session_state.documents_uploaded["bank"]:
                                    st.session_state.current_stage = "VERIFICATION"
                                else:
                                    st.session_state.current_stage = "DOCUMENTS_UPLOAD"
                                
                                st.session_state.messages.append({
                                    "role": "model",
                                    "content": f"Welcome back, {saved_app['applicant_data']['name']}! I've restored your application from {saved_app['saved_at']}. Let's continue where you left off."
                                })
                                
                                st.success("✅ Saved Application Restored!")
                                st.rerun()
                            else:
                                st.error("❌ Phone number does not match the application")
                        
                        # Check existing applicants database
                        elif phone in EXISTING_APPLICANTS:
                            applicant = EXISTING_APPLICANTS[phone]
                            
                            if applicant["application_id"] == app_id:
                                st.session_state.applicant_data = applicant
                                st.session_state.applicant_data["phone"] = phone
                                st.session_state.chat_active = True
                                st.session_state.phone_verified = True
                                
                                # Set stage based on customer type
                                customer_type = applicant.get('customer_type', 'IN_PROGRESS')
                                if customer_type == "APPROVED":
                                    st.session_state.current_stage = "APPROVED"
                                elif customer_type == "IN_PROGRESS":
                                    st.session_state.current_stage = "VERIFICATION"
                                else:
                                    st.session_state.current_stage = "DOCUMENTS_UPLOAD"
                                
                                st.session_state.messages = [{
                                    "role": "model",
                                    "content": f"Welcome back, {applicant['name']}! I've pulled up your application {applicant['application_id']}. Your current status is: {applicant['stage']}. How can I assist you today?"
                                }]
                                
                                st.success("✅ Application Found!")
                                st.rerun()
                            else:
                                st.error("❌ Application ID does not match the phone number")
                        else:
                            st.error("❌ No application found for this phone number")
    
    else:
        st.success(f"✅ Application Retrieved - {st.session_state.applicant_data['application_id']}")
        
        customer_type = st.session_state.applicant_data.get('customer_type', 'IN_PROGRESS')
        
        # Show progress milestone based on customer type
        if customer_type == "APPROVED":
            st.success("📍 Current Stage: Approved & Disbursement")
        elif customer_type == "IN_PROGRESS":
            st.info("📍 Current Stage: Verification in Progress")
        elif customer_type == "REJECTED":
            st.error("📍 Current Stage: Application Rejected")
        
        # Display different layouts based on customer type
        if customer_type == "APPROVED":
            st.success("🎉 LOAN APPROVED")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Applicant", st.session_state.applicant_data['name'])
            with col2:
                st.metric("Application ID", st.session_state.applicant_data['application_id'])
            with col3:
                st.metric("Loan Amount", f"₹{st.session_state.applicant_data.get('loan_amount', 0):,}")
            with col4:
                st.metric("Status", st.session_state.applicant_data['stage'])
            
            st.info(f"📅 Submitted: {st.session_state.applicant_data['submitted_date']} | Approved: {st.session_state.applicant_data.get('approved_date', 'N/A')}")
            
            if "Disbursed" in st.session_state.applicant_data['stage']:
                st.success(f"💰 Disbursement Date: {st.session_state.applicant_data.get('disbursement_date', 'N/A')}")
            else:
                st.warning(f"⏳ Expected Disbursement: {st.session_state.applicant_data.get('disbursement_date', 'Processing')}")
            
            # Generate sanction letter
            sanction_pdf = generate_sanction_letter_pdf(st.session_state.applicant_data)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📜 Download Sanction Letter",
                    data=sanction_pdf,
                    file_name=f"FlexiLoans_Sanction_Letter_{st.session_state.applicant_data['application_id']}.pdf",
                    mime="application/pdf",
                    key="download_sanction"
                )
            
            with col2:
                # Generate offer letter with EMI details if available
                offer_pdf = generate_offer_letter_pdf(
                    st.session_state.applicant_data,
                    st.session_state.emi_calculation
                )
                st.download_button(
                    label="🎁 Download Offer Letter",
                    data=offer_pdf,
                    file_name=f"FlexiLoans_Offer_Letter_{st.session_state.applicant_data['application_id']}.pdf",
                    mime="application/pdf",
                    key="download_offer"
                )

            render_topup_section(st.session_state.applicant_data, key_prefix="stream_b_")

        elif customer_type == "IN_PROGRESS":
            st.info("⏳ APPLICATION IN PROGRESS")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Applicant", st.session_state.applicant_data['name'])
            with col2:
                st.metric("Application ID", st.session_state.applicant_data['application_id'])
            with col3:
                st.metric("Current Stage", st.session_state.applicant_data['stage'])
            
            st.info(f"📅 Submitted: {st.session_state.applicant_data['submitted_date']}")
            
            pending_docs = st.session_state.applicant_data.get('pending_documents', [])
            if pending_docs:
                st.warning("📋 Pending Documents:")
                for doc in pending_docs:
                    st.write(f"• {doc}")
            
            st.info(f"⏱️ Estimated Completion: {st.session_state.applicant_data.get('estimated_completion', 'Processing')}")
        
        elif customer_type == "REJECTED":
            st.error("❌ APPLICATION REJECTED")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Applicant", st.session_state.applicant_data['name'])
            with col2:
                st.metric("Application ID", st.session_state.applicant_data['application_id'])
            with col3:
                st.metric("Status", st.session_state.applicant_data['stage'])
            
            st.info(f"📅 Submitted: {st.session_state.applicant_data['submitted_date']} | Rejected: {st.session_state.applicant_data.get('rejected_date', 'N/A')}")
            
            st.error(f"🚫 Rejection Reason: {st.session_state.applicant_data.get('rejection_reason', 'Not specified')}")
            
            if st.session_state.applicant_data.get('reapply_eligible', False):
                st.warning(f"🔄 You can reapply after: {st.session_state.applicant_data.get('reapply_after_date', 'Contact support')}")
            else:
                st.error("⛔ Currently not eligible to reapply. Please contact support.")
        
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Applicant", st.session_state.applicant_data['name'])
            with col2:
                st.metric("Application ID", st.session_state.applicant_data['application_id'])
            with col3:
                st.metric("Status", st.session_state.applicant_data['stage'])
            
            st.info(f"📅 Submitted: {st.session_state.applicant_data['submitted_date']}")
        
        st.markdown("---")
        st.subheader("💬 Application Support Chat")

        if not client:
            st.error("Please enter your Gemini API Key in the sidebar to use FlexiBot.")
            st.stop()

        for message in st.session_state.messages:
            avatar = "🤝" if message["role"] == "model" else "👤"
            with st.chat_message(message["role"], avatar=avatar):
                st.write(message["content"])
        
        uploaded_file = st.file_uploader("📎 Attach Document (Optional)", type=["pdf", "jpg", "jpeg", "png"], key="existing_doc_uploader")
        
        # Validate uploaded file
        if uploaded_file is not None:
            validation_result = validate_document(uploaded_file, "Document")
            render_document_validation_feedback(validation_result)
        
        if user_input := st.chat_input("Type your message..."):
            message_content = user_input
            
            # Check for save/exit intent
            user_input_lower = user_input.lower()
            save_keywords = ["save", "exit", "leave", "pause", "continue later", "stop", "quit"]
            if any(keyword in user_input_lower for keyword in save_keywords):
                # For existing applicants, just acknowledge - their state is already in database
                pass
            
            # Check if file is uploaded
            if uploaded_file is not None:
                file_name = uploaded_file.name
                message_content += f" [Attached: {file_name}]"
                
                # Validate document
                validation = validate_document(uploaded_file, "Uploaded")
                if validation and validation["valid"]:
                    message_content += " ✅"
                else:
                    message_content += " ⚠️"
            
            st.session_state.messages.append({"role": "user", "content": message_content})
            
            with st.chat_message("user", avatar="👤"):
                st.write(message_content)
            
            with st.spinner("FlexiBot responding..."):
                # Detect document upload in message
                doc_detected = ""
                user_input_lower = user_input.lower()
                
                # Check for save/exit intent
                save_intent = False
                save_keywords = ["save", "exit", "leave", "pause", "continue later", "stop", "quit"]
                if any(keyword in user_input_lower for keyword in save_keywords):
                    save_intent = True
                
                if uploaded_file is not None:
                    if "pan" in user_input_lower:
                        doc_detected = "PAN Card"
                    elif "bank" in user_input_lower or "statement" in user_input_lower:
                        doc_detected = "Bank Statement"
                    else:
                        doc_detected = "Additional Document"
                
                customer_type = st.session_state.applicant_data.get('customer_type', 'IN_PROGRESS')
                
                # Build context based on customer type
                if customer_type == "APPROVED":
                    context = f"""
CUSTOMER TYPE: APPROVED (Loan Already Processed)
CURRENT STATUS: {st.session_state.applicant_data['stage']}
LOAN AMOUNT: ₹{st.session_state.applicant_data.get('loan_amount', 0):,}
APPROVED DATE: {st.session_state.applicant_data.get('approved_date', 'N/A')}
DISBURSEMENT: {st.session_state.applicant_data.get('disbursement_date', 'Processing')}

{f"USER WANTS TO SAVE AND EXIT" if save_intent else ""}

YOUR ROLE:
1. Congratulate them on their approved loan
2. Provide information about disbursement timeline and process
3. Explain how to track disbursement status
4. Answer questions about loan terms, repayment schedule, EMI details
5. Guide them on next steps after disbursement
6. Inform them they can download their Sanction Letter from above
7. Provide support contact information if needed
8. **SAVE & EXIT**: If user wants to exit, confirm they can return anytime with their Application ID
9. Be celebratory and helpful
"""
                elif customer_type == "IN_PROGRESS":
                    pending_docs = st.session_state.applicant_data.get('pending_documents', [])
                    context = f"""
CUSTOMER TYPE: IN PROGRESS (Application Under Review)
CURRENT STATUS: {st.session_state.applicant_data['stage']}
SUBMITTED DATE: {st.session_state.applicant_data['submitted_date']}
ESTIMATED COMPLETION: {st.session_state.applicant_data.get('estimated_completion', 'Processing')}
PENDING DOCUMENTS: {', '.join(pending_docs) if pending_docs else 'None'}

{f"USER WANTS TO SAVE AND EXIT" if save_intent else ""}

YOUR ROLE:
1. Provide updates on their application progress
2. Explain what their current stage means and what's happening
3. If documents are pending, actively guide them to upload through chat by saying "You can attach your [document name] right here in the chat using the attachment button"
4. If document was just uploaded, acknowledge and confirm receipt
5. Answer questions about verification process and timeline
6. Reassure them about the process
7. **SAVE & EXIT**: If user wants to exit, confirm they can return anytime with their Application ID and phone number
8. Be supportive and informative
"""
                elif customer_type == "REJECTED":
                    context = f"""
CUSTOMER TYPE: REJECTED (Application Declined)
REJECTION REASON: {st.session_state.applicant_data.get('rejection_reason', 'Not specified')}
REJECTED DATE: {st.session_state.applicant_data.get('rejected_date', 'N/A')}
REAPPLY ELIGIBLE: {st.session_state.applicant_data.get('reapply_eligible', False)}
REAPPLY AFTER: {st.session_state.applicant_data.get('reapply_after_date', 'Contact support')}

{f"USER WANTS TO SAVE AND EXIT" if save_intent else ""}

YOUR ROLE:
1. Be empathetic and understanding about the rejection
2. Clearly explain the reason for rejection
3. Provide guidance on how to improve their application
4. Inform them about reapplication eligibility and timeline
5. Suggest steps they can take to become eligible (improve credit score, increase turnover, etc.)
6. Offer alternative loan products if applicable
7. Provide support contact for appeals or clarifications
8. **SAVE & EXIT**: If user wants to exit, confirm they can return anytime for guidance
9. Be compassionate but honest
"""
                else:
                    context = f"""
CUSTOMER TYPE: EXISTING CUSTOMER
CURRENT STATUS: {st.session_state.applicant_data['stage']}
"""
                
                system_instruction = f"""
You are 'FlexiBot', an AI assistant for FlexiLoans helping {st.session_state.applicant_data['name']} with their application {st.session_state.applicant_data['application_id']}.

{context}

{f"DOCUMENT JUST UPLOADED: {doc_detected}" if doc_detected else ""}

Keep responses clear, concise, and action-oriented. Adapt your tone based on customer type:
- APPROVED: Celebratory and guiding
- IN_PROGRESS: Reassuring and informative
- REJECTED: Empathetic and constructive
"""
                
                chat_history = []
                for msg in st.session_state.messages[:-1]:
                    if msg["role"] == "user":
                        chat_history.append(types.Content(role="user", parts=[types.Part.from_text(text=msg["content"])]))
                    else:
                        chat_history.append(types.Content(role="model", parts=[types.Part.from_text(text=msg["content"])]))
                
                chat_session = client.chats.create(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3
                    ),
                    history=chat_history
                )
                
                response = chat_session.send_message(user_input)
            
            st.session_state.messages.append({"role": "model", "content": response.text})
            
            with st.chat_message("model", avatar="🤝"):
                st.write(response.text)
            
            st.rerun()

# STREAM C: DIRECT CHAT WITH FLEXIBOT
elif st.session_state.workflow_stream == "💬 Chat with FlexiBot":

    if not client:
        st.error("Please enter your Gemini API Key in the sidebar to use FlexiBot.")
        st.stop()

    # Restore FlexiBot messages if returning to this stream
    if not st.session_state.messages and st.session_state.flexibot_messages:
        st.session_state.messages = st.session_state.flexibot_messages

    if not st.session_state.messages:
        welcome = (
            "Hi! I'm **FlexiBot**, your complete FlexiLoans agent. I handle everything — no need to navigate anywhere yourself.\n\n"
            "Just tell me what you need:\n"
            "- **'I want to apply for a loan'** — I'll guide you step by step\n"
            "- **Share your Application ID** (FL-2026-XXXX) — I'll fetch your status instantly\n"
            "- **Share your phone number** — I'll find your application\n"
            "- **'Calculate EMI for 5 lakh, 12%, 24 months'** — instant calculation\n"
            "- **'Am I eligible?'** — share your age, income & turnover\n\n"
            "What can I help you with today?"
        )
        st.session_state.messages = [{"role": "model", "content": welcome}]
        st.session_state.flexibot_messages = st.session_state.messages.copy()
        st.session_state.chat_active = True

    # ── Pending navigation banner (set after LLM response, consumed on click) ──
    if st.session_state.pending_nav:
        nav = st.session_state.pending_nav
        st.markdown(f"""
<div style="background:#1a472a;padding:18px 22px;border-radius:10px;margin-bottom:16px;border-left:5px solid #2ecc71">
<h4 style="color:#2ecc71;margin:0 0 6px 0">FlexiBot Action Ready</h4>
<p style="color:#ecf0f1;margin:0 0 12px 0">{nav.get('headline','')}</p>
</div>""", unsafe_allow_html=True)
        col_go, col_stay = st.columns([2, 1])
        with col_go:
            if st.button(f"→ {nav['label']}", key="pending_nav_go", type="primary", use_container_width=True):
                st.session_state.flexibot_messages = st.session_state.messages.copy()
                flexibot_navigate(nav)
        with col_stay:
            if st.button("Stay in chat", key="pending_nav_stay", use_container_width=True):
                st.session_state.pending_nav = None
                st.rerun()
        st.markdown("---")

    # ── Chat message display ────────────────────────────────────────────────
    for message in st.session_state.messages:
        avatar = "🤝" if message["role"] == "model" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])

    # ── In-chat document upload (appears after profile complete + eligible) ──
    gathered_check = extract_profile_from_messages(st.session_state.messages)
    all_profile    = {"name","phone","age","income","turnover"}.issubset(gathered_check.keys())

    if all_profile and not st.session_state.chat_offer_ready:
        _age      = gathered_check.get("age", 0)
        _income   = gathered_check.get("income", 0)
        _turnover = gathered_check.get("turnover", 0)
        is_eligible = (
            ELIGIBILITY_RULES["min_age"] <= _age <= ELIGIBILITY_RULES["max_age"] and
            _income   >= ELIGIBILITY_RULES["min_monthly_income"] and
            _turnover >= ELIGIBILITY_RULES["min_annual_turnover"]
        )

        if is_eligible:
            # Generate app ID once
            if not st.session_state.chat_app_id:
                st.session_state.chat_app_id = f"FL-2026-{1100 + len(st.session_state.saved_applications)}"

            st.markdown("---")
            st.markdown("""
<div style="background:linear-gradient(135deg,#1a472a,#145a32);padding:18px 22px;border-radius:12px;border-left:5px solid #2ecc71;margin-bottom:16px">
<h4 style="color:#2ecc71;margin:0 0 4px 0">✅ You're Eligible for a FlexiLoan!</h4>
<p style="color:#ecf0f1;margin:0;font-size:13px">Upload your PAN Card below to complete your application instantly.</p>
</div>""", unsafe_allow_html=True)

            if not st.session_state.chat_pan_uploaded:
                pan_file = st.file_uploader(
                    "🪪 Upload PAN Card (PDF / JPG / PNG)",
                    type=["pdf", "jpg", "jpeg", "png"],
                    key="chat_pan_uploader"
                )
                if pan_file:
                    st.session_state.chat_pan_uploaded = True
                    # Register application
                    max_emi      = _income * 0.4
                    optimal_loan = max(min(int(max_emi * 24), 2000000), 100000)
                    rate         = 12.0
                    t            = 24
                    monthly_emi  = optimal_loan * (rate/1200) * (1+rate/1200)**t / ((1+rate/1200)**t - 1)
                    app_id       = st.session_state.chat_app_id
                    st.session_state.saved_applications[app_id] = {
                        "applicant_data": {
                            "application_id": app_id,
                            "name":           gathered_check.get("name", "Customer"),
                            "phone":          str(gathered_check.get("phone", "")),
                            "age":            _age,
                            "monthly_income": _income,
                            "annual_turnover":_turnover,
                            "loan_amount":    optimal_loan,
                            "interest_rate":  rate,
                            "tenure_months":  t,
                            "monthly_emi":    round(monthly_emi, 0),
                            "disbursement_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                            "customer_type":  "IN_PROGRESS",
                        },
                        "documents_uploaded": {"pan": True, "bank": False},
                        "messages": [],
                        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    st.session_state.chat_approval_time = datetime.now()
                    st.rerun()
            else:
                st.success("✓ PAN Card uploaded successfully")

            # Countdown + approval
            if st.session_state.chat_pan_uploaded and st.session_state.chat_approval_time and not st.session_state.chat_approved:
                elapsed   = (datetime.now() - st.session_state.chat_approval_time).total_seconds()
                remaining = max(0, 5 - int(elapsed))
                if remaining > 0:
                    st.info(f"⏳ Verifying your PAN Card... **{remaining}s** — please wait")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.chat_approved     = True
                    st.session_state.chat_offer_ready  = True
                    app_id = st.session_state.chat_app_id
                    st.session_state.saved_applications[app_id]["applicant_data"]["customer_type"] = "APPROVED"
                    app_data    = st.session_state.saved_applications[app_id]["applicant_data"]
                    loan_amount = app_data["loan_amount"]
                    approval_msg = (
                        f"🎉 **Congratulations {app_data['name']}! Your loan application is APPROVED!**\n\n"
                        f"**Application ID:** {app_id}\n"
                        f"**Approved Amount:** Rs.{loan_amount:,}\n"
                        f"**Monthly EMI:** Rs.{app_data['monthly_emi']:,.0f}\n"
                        f"**Disbursement:** {app_data['disbursement_date']}\n\n"
                        "Your Offer Letter is ready to download below! 👇"
                    )
                    st.session_state.messages.append({"role": "model", "content": approval_msg})
                    st.session_state.flexibot_messages = st.session_state.messages.copy()
                    st.rerun()

    # ── Offer letter download (shown after chat approval) ─────────────────
    if st.session_state.chat_offer_ready and st.session_state.chat_app_id:
        app_id   = st.session_state.chat_app_id
        app_data = st.session_state.saved_applications.get(app_id, {}).get("applicant_data", {})
        st.markdown("---")
        st.markdown("""
<div style="background:linear-gradient(135deg,#1B365D,#1e3f6f);padding:18px 22px;border-radius:12px;border-left:5px solid #00B4D8;margin-bottom:16px">
<h4 style="color:#00B4D8;margin:0 0 4px 0">📄 Your Documents are Ready</h4>
<p style="color:rgba(255,255,255,0.85);margin:0;font-size:13px">Download your loan documents below.</p>
</div>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            emi_details = {
                "principal":      app_data.get("loan_amount", 500000),
                "annual_rate":    app_data.get("interest_rate", 12.0),
                "tenure_months":  app_data.get("tenure_months", 24),
                "emi":            app_data.get("monthly_emi", 0),
            }
            offer_pdf = generate_offer_letter_pdf(app_data, emi_details)
            st.download_button("📥 Offer Letter", offer_pdf,
                               f"FlexiLoans_Offer_{app_id}.pdf", "application/pdf",
                               key="chat_offer_dl", use_container_width=True)
        with col2:
            sanction_pdf = generate_sanction_letter_pdf(app_data)
            st.download_button("📥 Sanction Letter", sanction_pdf,
                               f"FlexiLoans_Sanction_{app_id}.pdf", "application/pdf",
                               key="chat_sanction_dl", use_container_width=True)
        with col3:
            sub_pdf = generate_application_submission_pdf(app_data, {"pan": True, "bank": False})
            st.download_button("📥 Application Form", sub_pdf,
                               f"FlexiLoans_Application_{app_id}.pdf", "application/pdf",
                               key="chat_app_dl", use_container_width=True)
        st.info("💸 Loan amount will be disbursed to your registered bank account within 2 business days.")
        render_topup_section(app_data, key_prefix="chat_topup_")
        st.markdown("---")

    if user_input := st.chat_input("Type your message — I'll guide you completely..."):
        st.session_state.chat_active = True
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user", avatar="👤"):
            st.write(user_input)

        with st.spinner("FlexiBot thinking..."):

            # ── Live EMI ──────────────────────────────────────────────────────
            emi_context = ""
            if any(kw in user_input.lower() for kw in ["emi", "calculate", "monthly payment", "instalment", "installment"]):
                nums = sorted([float(n) for n in _re.findall(r'\d+(?:\.\d+)?', user_input) if float(n) > 0], reverse=True)
                principals = [n for n in nums if n >= 10000]
                rates      = [n for n in nums if 1 <= n <= 36]
                tenures    = [n for n in nums if 6 <= n <= 360]
                if principals:
                    p = principals[0]
                    r = rates[0] if rates else 12.0
                    t = int(tenures[0]) if tenures else 24
                    res = calculate_emi(p, r, t)
                    emi_context = (
                        f"\nLIVE EMI RESULT: Rs.{p:,.0f} at {r}% p.a. for {t} months → "
                        f"EMI=Rs.{res['emi']:,.0f} | Total Interest=Rs.{res['total_interest']:,.0f} | "
                        f"Total Payment=Rs.{res['total_payment']:,.0f} | "
                        f"Principal {res['principal']/res['total_payment']*100:.1f}% | "
                        f"Interest {res['total_interest']/res['total_payment']*100:.1f}%\n"
                        "Present this breakdown clearly.\n"
                    )

            # ── Smart recommendations ─────────────────────────────────────────
            reco_context = ""
            gathered = extract_profile_from_messages(st.session_state.messages)
            if gathered.get("income") or gathered.get("turnover"):
                if any(kw in user_input.lower() for kw in ["recommend","suggest","how much","afford","eligible","best loan","smart"]):
                    prof = {"income": gathered.get("income",75000), "turnover": gathered.get("turnover",15000000), "age": gathered.get("age",35)}
                    reco = generate_smart_recommendations(prof, st.session_state.credit_score_input)
                    reco_context = (
                        f"\nSMART RECOMMENDATION: Optimal loan Rs.{reco['optimal_loan']['amount']:,.0f} "
                        f"at {reco['optimal_loan']['interest_rate']}% p.a. | "
                        f"Max safe EMI Rs.{reco['optimal_loan']['max_emi']:,.0f}/month | "
                        f"Tenure: {reco['tenure']['months']} months | "
                        f"Monthly EMI: Rs.{reco['tenure']['monthly_emi']:,.0f}\n"
                        "Present with explanation.\n"
                    )

            # ── Application / phone lookup ────────────────────────────────────
            app_context_block, detected_nav = build_application_context(
                st.session_state.messages,
                st.session_state.saved_applications,
                EXISTING_APPLICANTS
            )

            # ── Profile summary ───────────────────────────────────────────────
            profile_lines = []
            for k, label in [("name","Name"),("phone","Phone"),("age","Age"),("income","Monthly Income"),("turnover","Annual Turnover")]:
                if k in gathered:
                    val = f"Rs.{gathered[k]:,}" if k in ("income","turnover") else gathered[k]
                    profile_lines.append(f"{label}: {val}")
            gathered_block = ("PROFILE COLLECTED IN THIS CHAT: " + " | ".join(profile_lines)) if profile_lines else ""

            # ── Missing fields for new applicant flow ─────────────────────────
            required_fields = {"name","phone","age","income","turnover"}
            missing_fields  = required_fields - set(gathered.keys())
            missing_note = ""
            if missing_fields and any(kw in " ".join(m["content"] for m in st.session_state.messages).lower()
                                      for kw in ["apply","loan","want","need","start"]):
                missing_note = f"STILL NEED FROM USER: {', '.join(missing_fields)}. Ask for the next missing field."

            system_instruction = f"""You are FlexiBot — the complete, intelligent virtual loan agent for FlexiLoans (India's leading digital NBFC for business loans). You guide every customer end-to-end with zero handoff.
Date: 2026-05-25

{gathered_block}
{missing_note}
{f"LIVE APPLICATION DATA:{app_context_block}" if app_context_block else ""}
{emi_context}
{reco_context}

━━━ PORTAL KNOWLEDGE ━━━
ELIGIBILITY: Age 21–65 | Annual Turnover ≥ Rs.12,00,000 | Monthly Income ≥ Rs.50,000
MANDATORY DOCS: PAN Card + 6-month Bank Statement
OPTIONAL DOCS: Business Registration, GST Returns, ITR (last 2 years)
LOAN RANGE: Rs.1 Lakh – Rs.2 Crore | 12–60 months | 10–18% p.a.
EMI RULE: Safe EMI = 40% of monthly income
TOP-UP (approved customers): max(75% of loan, 3× income) | Rate+0.5% | Tenure 6–24 months | 24-hr disbursal | 1% fee
STATUSES → APPROVED: celebrate + offer top-up | IN_PROGRESS: check pending docs | REJECTED: explain + improvement plan + reapply date

━━━ HOW TO BEHAVE ━━━
APPLY FLOW: Collect name→age→phone→income→turnover one at a time. Once all 5 collected, check eligibility instantly.
  - If ELIGIBLE: say "Great news — you qualify! A PAN Card upload section has appeared just below our chat. Please upload your PAN Card there and your loan will be approved instantly!"
  - If INELIGIBLE: explain which criteria failed, give improvement advice, do NOT ask for documents.
STATUS CHECK: Use LIVE APPLICATION DATA. Never say "I can't access" — you have all data. Give exact stage + next action.
PHONE LOOKUP: If phone found in data → greet by name, give status, offer action.
NOT FOUND: Say clearly "I could not find application [ID]. Please verify — it looks like FL-2026-XXXX."
EMI: Use LIVE EMI RESULT above. If not computed, ask amount/rate/tenure.
TOP-UP: For approved customers — calculate amount, quote EMI, tell "I've queued the top-up application — click the button."

RULES:
1. Never say "I don't have access" or "call support" — solve everything yourself
2. One question at a time when collecting profile data
3. For new applicants — NEVER tell them to go to another section; the PAN upload section appears automatically in this chat
4. Use Rs. not rupee symbol
5. Be warm, specific, action-oriented
6. End every response with one clear next step
"""

            chat_history = []
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                chat_history.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

            chat_session = client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.25),
                history=chat_history
            )
            response = chat_session.send_message(user_input)

        bot_reply = response.text
        st.session_state.messages.append({"role": "model", "content": bot_reply})
        st.session_state.flexibot_messages = st.session_state.messages.copy()

        with st.chat_message("model", avatar="🤝"):
            st.write(bot_reply)

        # ── Queue navigation if anything was detected ─────────────────────────
        _, detected_nav = build_application_context(
            st.session_state.messages,
            st.session_state.saved_applications,
            EXISTING_APPLICANTS
        )
        # Only queue existing-applicant navs; new-applicant flow is handled in-chat
        gathered_now = extract_profile_from_messages(st.session_state.messages)
        all_have     = {"name","phone","age","income","turnover"}.issubset(gathered_now.keys())
        # Suppress goto_new_applicant_prefill — PAN upload section renders in chat instead
        detected_nav = [n for n in detected_nav if n.get("type") != "goto_new_applicant_prefill"]

        if detected_nav and st.session_state.pending_nav is None:
            st.session_state.pending_nav = detected_nav[0]

        st.rerun()

# Sidebar metrics
if st.session_state.chat_active:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Session Metrics")
    st.sidebar.metric("Messages", len(st.session_state.messages))
    st.sidebar.metric("Stream", st.session_state.workflow_stream)
    
    if st.session_state.workflow_stream == "Existing Applicant":
        customer_type = st.session_state.applicant_data.get('customer_type', 'UNKNOWN')
        if customer_type == "APPROVED":
            st.sidebar.success("🎉 Customer: APPROVED")
        elif customer_type == "IN_PROGRESS":
            st.sidebar.info("⏳ Customer: IN PROGRESS")
        elif customer_type == "REJECTED":
            st.sidebar.error("❌ Customer: REJECTED")
    elif st.session_state.workflow_stream == "💬 Chat with FlexiBot":
        st.sidebar.info("💬 Direct Chat Mode")
    else:
        st.sidebar.info("🆕 Customer: NEW APPLICANT")
    
    if st.sidebar.button("🔄 Reset Session"):
        # Save current application before reset if it's a new applicant
        if st.session_state.workflow_stream == "New Applicant" and st.session_state.eligibility_passed:
            app_id = st.session_state.applicant_data.get('application_id')
            if app_id:
                st.session_state.saved_applications[app_id] = {
                    "applicant_data": st.session_state.applicant_data.copy(),
                    "documents_uploaded": st.session_state.documents_uploaded.copy(),
                    "messages": st.session_state.messages.copy(),
                    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        
        # Preserve saved applications
        saved_apps = st.session_state.saved_applications.copy()
        
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        st.session_state.saved_applications = saved_apps
        st.rerun()
