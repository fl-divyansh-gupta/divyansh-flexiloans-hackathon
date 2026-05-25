# config.py
# Configuration file for FlexiLoans AI Collections Agent

# API Configuration
GEMINI_MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.2

# Pricing Configuration (per 1M tokens)
INPUT_TOKEN_COST = 0.30  # USD
OUTPUT_TOKEN_COST = 2.50  # USD

# Conversion Package Configuration
PACKAGES = {
    "A": {
        "name": "Frictionless Partial Pay",
        "percentage": 0.50,
        "description": "Pay 50% today, balance next month",
        "bonus": "Late fees waived if committed in this call"
    },
    "B": {
        "name": "Tenure Extension Drop",
        "extension_months": 3,
        "description": "Extend loan by 3 months, reduce monthly EMI",
        "bonus": "Processing fee waived for immediate acceptance"
    },
    "C": {
        "name": "Micro-Payment Bridge",
        "percentage": 0.25,
        "extension_days": 15,
        "description": "Pay 25% now, get 15-day extension",
        "bonus": "Zero penalties on remaining balance"
    }
}

# Conversion Scoring Configuration
SCORING_WEIGHTS = {
    "turn_penalty": 10,  # Points deducted per conversation turn
    "objection_penalty": 15,  # Points deducted per objection
    "urgency_bonus": 5,  # Points added per urgency trigger
    "base_probability": 30  # Starting conversion probability
}

# Stage Configuration
STAGES = {
    "EMPATHY_GREETING": {
        "name": "Customer Engaged",
        "progress": 0.33,
        "icon": "⏳"
    },
    "RESTRUCTURING_PROPOSAL": {
        "name": "Negotiation Pitch Active",
        "progress": 0.66,
        "icon": "⚡"
    },
    "CONVERSION_SUCCESS": {
        "name": "Successful Conversion",
        "progress": 1.0,
        "icon": "🔥"
    }
}

# Risk Thresholds
RISK_LEVELS = {
    "HIGH": {
        "dpd_threshold": 60,
        "default_threshold": 1,
        "color": "error",
        "icon": "🚨"
    },
    "MEDIUM": {
        "dpd_threshold": 30,
        "default_threshold": 0,
        "color": "warning",
        "icon": "⚠️"
    },
    "LOW": {
        "dpd_threshold": 0,
        "default_threshold": 0,
        "color": "info",
        "icon": "✓"
    }
}

# Conversion Probability Thresholds
PROBABILITY_THRESHOLDS = {
    "HIGH": 70,
    "MEDIUM": 40,
    "LOW": 0
}

# Keyword Detection
OBJECTION_KEYWORDS = [
    "cannot", "no", "later", "busy", "not now", 
    "difficult", "impossible", "won't", "can't"
]

POSITIVE_SIGNALS = [
    "yes", "okay", "fine", "agree", "accept", 
    "will pay", "can do", "sure", "alright"
]

NEGATIVE_SIGNALS = [
    "no", "cannot", "won't", "impossible", "later", 
    "busy", "never", "refuse"
]

URGENCY_KEYWORDS = [
    "right now", "today", "immediately", "limited time", 
    "waived", "freeze", "expires", "urgent"
]

# Strategy Configurations
STRATEGIES = {
    "Aggressive Conversion": {
        "description": "High-pressure tactics with strong urgency",
        "temperature": 0.15,
        "focus": "speed"
    },
    "Empathetic Persuasion": {
        "description": "Rapport-building with soft closing",
        "temperature": 0.25,
        "focus": "trust"
    },
    "Data-Driven Logic": {
        "description": "Fact-based rational persuasion",
        "temperature": 0.20,
        "focus": "logic"
    }
}

# UI Configuration
UI_CONFIG = {
    "page_title": "FlexiLoans Agentic Chat MVP",
    "layout": "wide",
    "sidebar_width": 350,
    "chat_avatar_agent": "🤝",
    "chat_avatar_user": "👤"
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    "export_format": "txt",
    "include_transcript": True,
    "include_metrics": True,
    "timestamp_format": "%Y-%m-%d %H:%M:%S"
}

# Compliance Configuration
COMPLIANCE_RULES = {
    "max_conversation_turns": 20,  # Alert if conversation exceeds this
    "max_objections_before_escalation": 5,
    "require_empathy_acknowledgment": True,
    "forbidden_words": ["threaten", "sue", "legal action", "destroy credit"],
    "mandatory_disclosures": [
        "All packages subject to final approval",
        "Terms and conditions apply"
    ]
}
