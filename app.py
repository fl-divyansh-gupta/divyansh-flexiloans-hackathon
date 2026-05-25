# app.py
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

st.set_page_config(page_title="FlexiLoans Smart Onboarding Engine", layout="wide")

GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or "AIzaSyDQoE-Gz0laemhkZGP5dOgMurtd1TKcUSE"
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize session state
if "workflow_stream" not in st.session_state:
    st.session_state.workflow_stream = None
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

# Sidebar - Stream Selection
st.sidebar.title("🏦 FlexiLoans Onboarding")
st.sidebar.markdown("---")

stream_choice = st.sidebar.radio(
    "Select Application Stream:",
    ["New Applicant", "Existing Applicant"],
    key="stream_selector"
)

if stream_choice != st.session_state.workflow_stream:
    st.session_state.workflow_stream = stream_choice
    st.session_state.eligibility_passed = False
    st.session_state.applicant_data = {}
    st.session_state.documents_uploaded = {"pan": False, "bank": False}
    st.session_state.messages = []
    st.session_state.chat_active = False
    st.session_state.phone_verified = False
    st.session_state.app_number_collected = False

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
        ['Gross Annual Turnover', f"₹{applicant_data['turnover']:,}"],
        ['Net Monthly Income', f"₹{applicant_data['income']:,}"],
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
    elements.append(Paragraph(f"PAN Card: {'✓ Uploaded' if st.session_state.documents_uploaded['pan'] else '✗ Pending'}", styles['Normal']))
    elements.append(Paragraph(f"Bank Statement: {'✓ Uploaded' if st.session_state.documents_uploaded['bank'] else '✗ Pending'}", styles['Normal']))
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
        ['Sanctioned Amount', f"₹{applicant_data.get('loan_amount', 0):,}"],
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
        ['Gross Annual Turnover', f"₹{applicant_data['turnover']:,}"],
        ['Net Monthly Income', f"₹{applicant_data['income']:,}"],
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
        ['PAN Card', '✓ Submitted' if documents_status.get('pan') else '✗ Pending'],
        ['Bank Statement', '✓ Submitted' if documents_status.get('bank') else '✗ Pending']
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
        ['Loan Amount Offered', f"₹{loan_amount:,}"],
        ['Interest Rate', f"{interest_rate}% per annum"],
        ['Loan Tenure', f"{tenure_months} months ({tenure_months//12} years)"],
        ['Monthly EMI', f"₹{monthly_emi:,.0f}"],
        ['Processing Fee', f"₹{loan_amount * 0.02:,.0f} (2% of loan amount)"],
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

# Main Panel
st.title("💼 FlexiLoans Smart Onboarding Engine")

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
        
        with st.form("eligibility_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Applicant Name*", placeholder="Enter full name")
                phone = st.text_input("Phone Number*", placeholder="10-digit mobile number")
                age = st.number_input("Age*", min_value=18, max_value=100, value=30)
            
            with col2:
                turnover = st.number_input("Gross Annual Turnover (₹)*", min_value=0, value=15000000, step=100000)
                income = st.number_input("Net Monthly Income (₹)*", min_value=0, value=75000, step=5000)
            
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
                    st.success(f"✅ Eligibility Passed! Application ID: {app_id}")
                    
                    # Generate application PDF
                    pdf_buffer = generate_application_pdf(st.session_state.applicant_data)
                    st.download_button(
                        label="📄 Download Application Form",
                        data=pdf_buffer,
                        file_name=f"FlexiLoans_Application_{app_id}.pdf",
                        mime="application/pdf"
                    )
                    
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
                        st.balloons()
                    
                    st.rerun()
            else:
                st.success("✅ Bank Statement Saved")
        
        # Show completion message if both docs uploaded
        if st.session_state.documents_uploaded["pan"] and st.session_state.documents_uploaded["bank"]:
            st.success("🎉 All documents uploaded! Your application is now under verification.")
            
            # Generate application submission confirmation PDF
            st.markdown("---")
            st.subheader("📄 Application Submission Confirmation")
            submission_pdf = generate_application_submission_pdf(
                st.session_state.applicant_data,
                st.session_state.documents_uploaded
            )
            st.download_button(
                label="📥 Download Submission Confirmation",
                data=submission_pdf,
                file_name=f"FlexiLoans_Submission_Confirmation_{st.session_state.applicant_data['application_id']}.pdf",
                mime="application/pdf",
                key="download_submission_conf"
            )
            st.info("✓ Your application has been successfully submitted. Download your confirmation for your records.")
        
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
