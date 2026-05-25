# 🏦 FlexiLoans Smart Onboarding Engine

An AI-powered customer acquisition, automated underwriting, and conversion engine built for FlexiLoans. Features a twin-stream pipeline that handles real-time eligibility scoring, document routing pipelines, intelligent conversational doubt-clearing, and comprehensive financial advisory tools using Google Gemini 2.5 Flash.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Features Deep Dive](#features-deep-dive)
- [Project Structure](#project-structure)
- [API Integration](#api-integration)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

FlexiLoans Smart Onboarding Engine is a comprehensive loan application and financial advisory platform that combines:

- **Automated Eligibility Assessment** with real-time validation
- **AI-Powered Conversational Assistant** for customer support
- **Document Quality Validation** with instant feedback
- **Financial Advisory Tools** for credit score improvement and EMI management
- **Multi-Stage Application Tracking** with visual progress indicators
- **PDF Generation** for application confirmations and offer letters

Built for hackathon evaluation, this system demonstrates enterprise-grade loan processing with a focus on customer experience and conversion optimization.

---

## ✨ Key Features

### 🔄 Twin-Stream Application Pipeline

#### Stream A: New Applicant Journey
- Real-time eligibility validation against configurable rules
- Automated application ID generation (FL-2026-XXXX format)
- Document upload workspace with quality validation
- AI-guided application completion
- Application submission confirmation PDF

#### Stream B: Existing Applicant Journey
- Secure application retrieval with phone + ID verification
- Status-based routing (Approved/In Progress/Rejected)
- Document submission for pending requirements
- Sanction letter and offer letter generation

### 🤖 AI-Powered Features

- **FlexiBot Assistant**: Context-aware conversational AI using Google Gemini 2.5 Flash
- **Smart Document Guidance**: Proactive prompts for document upload
- **Save & Resume**: Intelligent session management with state persistence
- **Personalized Responses**: Adapts tone based on customer type and stage

### 📊 Financial Advisory Suite

1. **Credit Score Improvement Tool**
   - Interactive score assessment (300-900 range)
   - Personalized improvement strategies
   - Impact analysis and timeline estimates

2. **EMI Management Calculator**
   - EMI-to-Income ratio analysis
   - Financial burden assessment
   - Best practice recommendations

3. **Loan Comparison Tool**
   - Side-by-side loan option comparison
   - Total interest calculation
   - Smart savings recommendations

4. **Financial Health Check**
   - Comprehensive financial assessment
   - Savings rate and debt ratio analysis
   - Overall health score (0-100)
   - Personalized improvement plan

### 📈 Progress Tracking

- **5-Stage Visual Pipeline**: Not Started → Eligibility → Documents → Verification → Approved
- **Real-time Progress Bar**: Shows completion percentage
- **Time Estimates**: Displays expected duration for each stage
- **Stage Timestamps**: Tracks completion time for analytics

### 📄 Document Management

- **Quality Validation**: PDF format verification with instant feedback
- **Upload via Chat**: Seamless document submission through conversation
- **Status Tracking**: Real-time document checklist
- **Auto-detection**: Identifies document type from user messages

### 🧮 EMI Calculator

- **Interactive Inputs**: Loan amount, tenure, interest rate sliders
- **Comprehensive Breakdown**: Principal, interest, total payment
- **Visual Representation**: Progress bars for payment split
- **Apply with Terms**: One-click application with calculated EMI

### 📑 PDF Generation

1. **Application Form PDF**: Generated after eligibility approval
2. **Submission Confirmation PDF**: Issued when all documents uploaded
3. **Offer Letter PDF**: Personalized loan offer with terms
4. **Sanction Letter PDF**: Official approval documentation

---

## 🛠️ Tech Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Primary programming language |
| **Streamlit** | 1.28.0+ | Web application framework |
| **Google Gemini API** | 2.5 Flash | AI conversational engine |
| **ReportLab** | 4.0.0+ | PDF generation library |

### Frontend Framework

- **Streamlit Components**
  - `st.chat_message`: Conversational UI
  - `st.file_uploader`: Document upload
  - `st.form`: Form handling
  - `st.sidebar`: Navigation and tools
  - `st.progress`: Visual indicators
  - `st.metric`: KPI display

### AI/ML Integration

- **Google GenAI SDK** (`google-genai`)
  - Model: `gemini-2.5-flash`
  - Temperature: 0.2-0.3 (controlled responses)
  - Context window: Automatic compaction
  - Streaming: Real-time response generation

### Document Processing

- **ReportLab**
  - PDF generation with custom styling
  - Table layouts with color coding
  - Professional document templates
  - A4 page format support

### Data Management

- **Session State Management**
  - Streamlit session state for persistence
  - In-memory application storage
  - State restoration for saved applications

### Utilities

- **Python Standard Library**
  - `datetime`: Timestamp management
  - `random`: Application ID generation
  - `io.BytesIO`: In-memory file handling
  - `os`: Environment variable access

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Sidebar    │  │  Main Panel  │  │  Chat Widget │      │
│  │  - Progress  │  │  - Forms     │  │  - FlexiBot  │      │
│  │  - EMI Calc  │  │  - Documents │  │  - Messages  │      │
│  │  - Guidance  │  │  - Status    │  │  - Upload    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Logic Layer                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Eligibility Engine  │  Document Validator           │   │
│  │  Progress Tracker    │  PDF Generator                │   │
│  │  EMI Calculator      │  Financial Advisor            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Google Gemini   │         │   ReportLab      │          │
│  │  2.5 Flash API   │         │   PDF Engine     │          │
│  └──────────────────┘         └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Storage                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Session State (In-Memory)                           │   │
│  │  - Application Data                                  │   │
│  │  - Document Status                                   │   │
│  │  - Chat History                                      │   │
│  │  - Saved Applications                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
New Applicant Flow:
User Input → Eligibility Check → Document Upload → AI Chat → Verification → Approval

Existing Applicant Flow:
App ID + Phone → Verification → Status Retrieval → AI Support → Document Submission
```

### Component Interaction

```python
# Simplified component interaction
Streamlit UI → Session State → Business Logic → External APIs → Response
     ↓              ↓               ↓                ↓             ↓
  User Input   State Mgmt    Validation      Gemini/PDF      UI Update
```

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Google Gemini API key (optional - fallback key included)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/flexiloans-onboarding.git
cd flexiloans-onboarding
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set API Key (Optional)

```bash
# Option 1: Environment Variable
export GOOGLE_API_KEY="your-api-key-here"

# Option 2: Use included fallback key (for demo purposes)
# No action needed - app uses fallback key automatically
```

### Step 5: Run Application

```bash
streamlit run app.py
```

The application will open automatically in your default browser at `http://localhost:8501`

---

## 🚀 Usage

### Quick Start Guide

#### For New Applicants:

1. **Select Stream**: Choose "New Applicant" from sidebar
2. **Fill Form**: Enter name, phone, age, turnover, income
3. **Check Eligibility**: Click "Check Eligibility"
4. **Download Form**: Get application form PDF
5. **Upload Documents**: Upload PAN card and bank statement
6. **Chat with FlexiBot**: Get guidance and complete application
7. **Download Confirmation**: Get submission confirmation PDF

#### For Existing Applicants:

1. **Select Stream**: Choose "Existing Applicant" from sidebar
2. **Enter Application ID**: Provide your FL-2026-XXXX ID
3. **Verify Phone**: Enter 10-digit phone number
4. **View Status**: See current application stage
5. **Download Documents**: Get sanction/offer letters (if approved)
6. **Chat Support**: Get help from FlexiBot

### Test Credentials

**Existing Applicant Test Data:**

| Phone Number | Application ID | Status | Type |
|--------------|----------------|--------|------|
| 9876543210 | FL-2026-1001 | Approved - Disbursed | APPROVED |
| 9876543211 | FL-2026-1002 | Approved - Pending | APPROVED |
| 9876543212 | FL-2026-1003 | Document Verification | IN_PROGRESS |
| 9876543213 | FL-2026-1004 | Additional Docs Required | IN_PROGRESS |
| 9876543214 | FL-2026-1005 | Credit Assessment | IN_PROGRESS |
| 9876543215 | FL-2026-1006 | Application Rejected | REJECTED |
| 9876543216 | FL-2026-1007 | Application Rejected | REJECTED |

---

## 🎨 Features Deep Dive

### 1. Smart Progress Bar

**Location**: Sidebar
**Functionality**:
- 5-stage pipeline visualization
- Real-time progress percentage (0-100%)
- Stage-specific time estimates
- Completed/Current/Upcoming indicators
- Auto-updates based on application state

**Stages**:
1. Not Started (0%)
2. Eligibility Check (20%)
3. Documents Upload (50%)
4. Verification (75%)
5. Approved (100%)

### 2. Document Quality Checker

**Validation Rules**:
- ✅ PDF format: Passes validation
- ⚠️ Other formats (JPG, PNG): Warning shown
- Instant feedback before submission
- Visual indicators in chat messages

**User Experience**:
- Upload file → See validation result immediately
- Green success for PDF
- Yellow warning for other formats
- Documents still accepted but with quality note

### 3. EMI Calculator Widget

**Inputs**:
- Loan Amount: ₹50,000 - ₹1 Crore
- Tenure: 1-5 years
- Interest Rate: 8-18% p.a.

**Outputs**:
- Monthly EMI amount
- Total interest payable
- Total payment amount
- Principal vs Interest breakdown (visual)
- Percentage split

**Actions**:
- Calculate EMI button
- Apply with These Terms button (sends to chat)

### 4. Financial Guidance Suite

#### Credit Score Improvement
- Score range: 300-900
- Color-coded assessment
- Improvement tips with impact percentages
- Timeline estimates
- Direct chat integration

#### EMI Management
- Income vs EMI ratio calculator
- Visual burden indicator
- Health thresholds (40%, 50%)
- Best practice recommendations

#### Loan Comparison
- Side-by-side comparison
- Interest savings calculation
- Smart recommendations

#### Financial Health Check
- 4-metric assessment
- Overall health score (0-100)
- Personalized recommendations
- Savings rate analysis
- Debt-to-income ratio

### 5. PDF Generation System

**Application Form PDF**:
- Applicant details table
- Document status checklist
- Application ID and date
- Professional formatting

**Submission Confirmation PDF**:
- Confirmation message
- Complete applicant information
- Document submission status
- What happens next (4-step guide)
- Important notes and contact info

**Offer Letter PDF**:
- Loan offer details
- EMI breakdown
- Terms and conditions
- Acceptance instructions
- 15-day validity period

**Sanction Letter PDF**:
- Approval confirmation
- Sanctioned amount
- Disbursement details
- Next steps guide

---

## 📁 Project Structure

```
flexiloans-onboarding/
│
├── app.py                      # Main application file
├── dummy_data.py               # Sample data and eligibility rules
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── dashboard_components.py     # Dashboard visualization components
├── strategy_comparison.py      # Analytics and comparison tools
│
└── .gitignore                  # Git ignore rules
```

### Key Files Description

**app.py** (Main Application)
- Streamlit UI components
- Business logic
- AI integration
- PDF generation functions
- Session state management

**dummy_data.py** (Data Layer)
- Eligibility rules configuration
- Sample applicant profiles
- Customer type definitions

**config.py** (Configuration)
- Application settings
- Scoring weights
- Stage configurations
- Risk thresholds

**requirements.txt** (Dependencies)
```
streamlit>=1.28.0
google-genai>=0.2.0
python-dotenv>=1.0.0
reportlab>=4.0.0
```

---

## 🔌 API Integration

### Google Gemini API

**Configuration**:
```python
client = genai.Client(api_key=GEMINI_API_KEY)

chat_session = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.3
    ),
    history=chat_history
)
```

**Features Used**:
- Chat completion with history
- System instructions for context
- Temperature control for consistency
- Streaming responses

**Rate Limits**:
- Requests per minute: As per API tier
- Token limits: Automatic context management

### PDF Generation API

**ReportLab Integration**:
```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph

# Generate PDF in memory
buffer = BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4)
doc.build(elements)
```

**Features**:
- Custom styling with colors
- Table layouts
- Professional formatting
- In-memory generation

---

## 🎯 Use Cases

### 1. Loan Application Processing
- Automated eligibility screening
- Document collection and validation
- Real-time status tracking
- Approval workflow management

### 2. Customer Support
- 24/7 AI-powered assistance
- Context-aware responses
- Document guidance
- Query resolution

### 3. Financial Advisory
- Credit score improvement planning
- EMI burden assessment
- Loan comparison and selection
- Financial health monitoring

### 4. Conversion Optimization
- Progress visualization
- Proactive guidance
- Save and resume functionality
- Multi-channel document upload

---

## 🔒 Security Considerations

- **API Key Management**: Environment variables for sensitive data
- **Phone Verification**: 10-digit validation
- **Application ID**: Unique identifier for each application
- **Session Isolation**: Separate state for each user session
- **Data Privacy**: No persistent storage of sensitive information

---

## 🚧 Future Enhancements

- [ ] Multi-language support (Hindi, Tamil, Telugu)
- [ ] SMS/Email notifications
- [ ] Payment gateway integration
- [ ] Video KYC integration
- [ ] Advanced analytics dashboard
- [ ] Mobile app version
- [ ] Database integration for persistence
- [ ] Role-based access control
- [ ] Audit trail and logging
- [ ] A/B testing framework

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Development Team** - FlexiLoans Hackathon 2026

---

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- Streamlit for the amazing framework
- ReportLab for PDF generation
- FlexiLoans for the opportunity

---

## 📞 Support

For questions or support:
- Email: support@flexiloans.com
- Documentation: [Link to docs]
- Issues: [GitHub Issues](https://github.com/yourusername/flexiloans-onboarding/issues)

---

## 📊 Project Stats

- **Lines of Code**: ~2,500+
- **Components**: 15+ interactive features
- **PDF Templates**: 4 professional documents
- **Test Cases**: 7 sample profiles
- **API Integrations**: 2 (Gemini, ReportLab)

---

**Built with ❤️ for FlexiLoans Hackathon 2026**
