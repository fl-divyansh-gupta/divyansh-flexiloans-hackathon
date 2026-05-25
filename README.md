# FlexiLoans Smart Onboarding Engine

> **Sapne Tere Ye** — AI-powered loan onboarding platform for India's small businesses.

A production-grade agentic onboarding system built for FlexiLoans, featuring an intelligent conversational AI (FlexiBot) that guides customers end-to-end through the loan lifecycle — from eligibility to disbursement.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  FlexiLoans Smart Onboarding Engine          │
│                   (Streamlit + Gemini 2.5 Flash)             │
├───────────────┬───────────────────┬─────────────────────────┤
│  Stream A     │  Stream B         │  Stream C               │
│  New          │  Existing         │  FlexiBot               │
│  Applicant    │  Applicant        │  (Primary Interface)     │
│               │                   │                         │
│ Eligibility   │ Status lookup     │ Full AI agent           │
│ Doc upload    │ Document upload   │ Guided onboarding       │
│ 5s demo       │ Top-up loan       │ Auto-navigation         │
│   approval    │ Offer letters     │ App lookup by ID/phone  │
│ Offer PDF     │                   │ EMI calculator          │
│ Sanction PDF  │                   │ Smart recommendations   │
│ Top-up loan   │                   │ Profile collection      │
└───────────────┴───────────────────┴─────────────────────────┘
```

---

## Features

### FlexiBot — Intelligent Loan Agent (Stream C)
- **Full conversational onboarding** — collects name, age, phone, income, turnover one question at a time
- **Instant eligibility check** — validates against criteria as soon as all 5 fields are collected
- **Auto-navigation** — detects intent and shows a green action banner that switches the user to the correct stream with data pre-populated
- **Application lookup** — searches by Application ID (FL-2026-XXXX) or 10-digit phone number
- **Status awareness** — tells exact stage, pending documents, and next steps
- **Live EMI calculation** — computes EMI, total interest, total payment from natural language
- **Smart recommendations** — optimal loan amount based on 40% EMI rule, tenure based on age
- **Top-up eligibility** — detects approved customers and offers instant top-up
- **Chat persistence** — FlexiBot history is preserved when navigating between streams

### Stream A — New Applicant
- Eligibility form with FlexiBot pre-fill support
- Document upload: PAN Card + Bank Statement (PDF/JPG/PNG) with validation
- 5-second demo instant approval after both documents uploaded
- Smart loan amount computed using AI recommendations engine
- Auto-generated PDF: Application Form, Submission Confirmation, Offer Letter, Sanction Letter

### Stream B — Existing Applicant
- Application lookup by ID + phone verification
- Status display for APPROVED / IN_PROGRESS / REJECTED customers
- Pending document tracking with upload support
- Top-Up Loan flow: 3-second demo approval, configurable amount/tenure, PDF offer letter

### Top-Up Loan
- Eligibility: min(75% of original loan, 3x monthly income)
- Rate: original rate + 0.5% | Tenure: 6-24 months | Fee: 1%
- 3-second demo approval
- Downloadable Top-Up Offer Letter PDF

### Sidebar Tools
- **EMI Calculator** — loan amount / tenure / rate sliders
- **Financial Guidance** — credit score improvement, EMI management, loan comparison, health check
- **Smart Recommendations** — AI-powered optimal loan sizing and cross-sell products
- **Progress Bar** — real-time application stage tracker

---

## Brand

Built to FlexiLoans brand guidelines:
- **Navy** `#1B365D` — headers, sidebar, structural elements
- **Cyan** `#00B4D8` — CTAs, active states, accents
- **Inter** — primary font | **DM Mono** — numerical data
- 60-30-5-5 colour proportion rule applied throughout

---

## Setup

### Prerequisites
- Python 3.10+
- Gemini API key (get one free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey))

### Installation

```bash
git clone https://github.com/fl-divyansh-gupta/divyansh-flexiloans-hackathon.git
cd divyansh-flexiloans-hackathon
pip install streamlit google-genai reportlab python-dotenv
```

### API Key Configuration

Create a `.env` file (never commit this):
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Or enter it in the sidebar when the app starts.

### Run

```bash
streamlit run app.py
```

---

## Test Credentials

### Existing Applicants (Stream B / FlexiBot phone lookup)

| Phone | Name | Status | Application ID |
|-------|------|--------|----------------|
| 9876543210 | Rajesh Kumar | APPROVED — Disbursed | FL-2026-1001 |
| 9876543211 | Priya Sharma | APPROVED — Disbursement Pending | FL-2026-1002 |
| 9876543212 | Amit Patel | IN_PROGRESS — Document Verification | FL-2026-1003 |
| 9876543213 | Sunita Reddy | IN_PROGRESS — Docs Required | FL-2026-1004 |
| 9876543214 | Vikram Singh | IN_PROGRESS — Credit Assessment | FL-2026-1005 |
| 9876543215 | Karthik Menon | REJECTED — Credit Score | FL-2026-1006 |
| 9876543216 | Meera Nair | REJECTED — Turnover Docs | FL-2026-1007 |

### Eligibility Criteria
- Age: 21-65 years
- Annual Turnover: >= Rs.12,00,000
- Monthly Income: >= Rs.50,000

---

## Project Structure

```
app.py                  # Main application (Streamlit)
config.py               # Configuration constants
dummy_data.py           # Test applicant data and eligibility rules
strategy_comparison.py  # Collections strategy module
.env                    # API key (git-ignored)
.gitignore
README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| AI / LLM | Google Gemini 2.5 Flash |
| PDF Generation | ReportLab |
| Environment | python-dotenv |
| Language | Python 3.10+ |

---

*Built for FlexiLoans Hackathon 2026 — Divyansh Gupta*
