# dummy_data.py

ELIGIBILITY_RULES = {
    "min_age": 21,
    "max_age": 65,
    "min_annual_turnover": 12000000,
    "min_monthly_income": 50000
}

EXISTING_APPLICANTS = {
    # Type 1: Application Process Done (Approved/Disbursed)
    "9876543210": {
        "application_id": "FL-2026-1001",
        "name": "Rajesh Kumar",
        "customer_type": "APPROVED",
        "stage": "Approved - Loan Disbursed",
        "submitted_date": "2026-05-10",
        "approved_date": "2026-05-18",
        "loan_amount": 500000,
        "disbursement_date": "2026-05-20"
    },
    "9876543211": {
        "application_id": "FL-2026-1002",
        "name": "Priya Sharma",
        "customer_type": "APPROVED",
        "stage": "Approved - Disbursement Pending",
        "submitted_date": "2026-05-15",
        "approved_date": "2026-05-23",
        "loan_amount": 750000,
        "disbursement_date": "Expected: 2026-05-27"
    },
    
    # Type 2: In Progress (Under Review/Verification)
    "9876543212": {
        "application_id": "FL-2026-1003",
        "name": "Amit Patel",
        "customer_type": "IN_PROGRESS",
        "stage": "Document Verification",
        "submitted_date": "2026-05-22",
        "pending_documents": [],
        "estimated_completion": "2026-05-28"
    },
    "9876543213": {
        "application_id": "FL-2026-1004",
        "name": "Sunita Reddy",
        "customer_type": "IN_PROGRESS",
        "stage": "Additional Documents Required",
        "submitted_date": "2026-05-20",
        "pending_documents": ["Income Tax Returns", "Business Registration Certificate"],
        "estimated_completion": "Pending document submission"
    },
    "9876543214": {
        "application_id": "FL-2026-1005",
        "name": "Vikram Singh",
        "customer_type": "IN_PROGRESS",
        "stage": "Credit Assessment",
        "submitted_date": "2026-05-23",
        "pending_documents": [],
        "estimated_completion": "2026-05-29"
    },
    
    # Type 3: Rejected (Application Declined)
    "9876543215": {
        "application_id": "FL-2026-1006",
        "name": "Karthik Menon",
        "customer_type": "REJECTED",
        "stage": "Application Rejected",
        "submitted_date": "2026-05-12",
        "rejected_date": "2026-05-19",
        "rejection_reason": "Credit score below minimum threshold (580)",
        "reapply_eligible": True,
        "reapply_after_date": "2026-08-19"
    },
    "9876543216": {
        "application_id": "FL-2026-1007",
        "name": "Meera Nair",
        "customer_type": "REJECTED",
        "stage": "Application Rejected",
        "submitted_date": "2026-05-08",
        "rejected_date": "2026-05-14",
        "rejection_reason": "Insufficient business turnover documentation",
        "reapply_eligible": True,
        "reapply_after_date": "2026-06-14"
    }
}