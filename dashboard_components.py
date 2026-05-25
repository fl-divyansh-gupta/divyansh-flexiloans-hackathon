# dashboard_components.py
# Advanced visualization components for conversion analytics

import streamlit as st
from datetime import datetime

def render_conversion_funnel_visual(stage, outcome_logged):
    """Render a visual conversion funnel with stages"""
    
    stages = [
        {"name": "Initial Contact", "icon": "📞", "active": True},
        {"name": "Objection Handling", "icon": "💬", "active": stage != "EMPATHY_GREETING"},
        {"name": "Package Presentation", "icon": "📦", "active": stage == "RESTRUCTURING_PROPOSAL"},
        {"name": "Commitment Secured", "icon": "✅", "active": outcome_logged}
    ]
    
    cols = st.columns(len(stages))
    for idx, (col, stage_info) in enumerate(zip(cols, stages)):
        with col:
            if stage_info["active"]:
                st.markdown(f"### {stage_info['icon']}")
                st.success(stage_info["name"])
            else:
                st.markdown(f"### ⚪")
                st.text(stage_info["name"])


def render_conversion_heatmap(objection_count, urgency_used, total_turns):
    """Render a heatmap showing conversion factors"""
    
    st.markdown("### 🔥 Conversion Factor Heatmap")
    
    # Calculate intensity scores
    objection_intensity = min(100, (objection_count / 5) * 100)
    urgency_intensity = min(100, (urgency_used / 5) * 100)
    engagement_intensity = min(100, (total_turns / 10) * 100)
    
    factors = [
        ("Objections", objection_intensity, "🚫"),
        ("Urgency Tactics", urgency_intensity, "⚡"),
        ("Engagement", engagement_intensity, "💬")
    ]
    
    for factor_name, intensity, icon in factors:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(intensity / 100)
        with col2:
            st.metric(icon, f"{intensity:.0f}%")
        st.caption(factor_name)


def render_psychological_triggers_used(messages):
    """Analyze and display psychological triggers used in conversation"""
    
    triggers_detected = {
        "Urgency": 0,
        "Scarcity": 0,
        "Social Proof": 0,
        "Loss Aversion": 0,
        "Reciprocity": 0
    }
    
    urgency_words = ["now", "today", "immediately", "limited", "expires"]
    scarcity_words = ["only", "few", "limited", "rare", "exclusive"]
    social_words = ["others", "customers", "borrowers", "popular", "hundreds"]
    loss_words = ["lose", "miss", "penalty", "impact", "drop", "risk"]
    reciprocity_words = ["waive", "bonus", "free", "gift", "courtesy"]
    
    for msg in messages:
        if msg["role"] == "model":
            content_lower = msg["content"].lower()
            
            if any(word in content_lower for word in urgency_words):
                triggers_detected["Urgency"] += 1
            if any(word in content_lower for word in scarcity_words):
                triggers_detected["Scarcity"] += 1
            if any(word in content_lower for word in social_words):
                triggers_detected["Social Proof"] += 1
            if any(word in content_lower for word in loss_words):
                triggers_detected["Loss Aversion"] += 1
            if any(word in content_lower for word in reciprocity_words):
                triggers_detected["Reciprocity"] += 1
    
    st.markdown("### 🧠 Psychological Triggers Deployed")
    
    for trigger, count in triggers_detected.items():
        if count > 0:
            st.markdown(f"**{trigger}**: {'🔵' * count} ({count}x)")


def render_conversation_timeline(messages):
    """Render a timeline of the conversation flow"""
    
    st.markdown("### ⏱️ Conversation Timeline")
    
    for idx, msg in enumerate(messages):
        role = "Agent" if msg["role"] == "model" else "Customer"
        icon = "🤝" if msg["role"] == "model" else "👤"
        
        with st.expander(f"{icon} Turn {idx + 1}: {role}", expanded=False):
            st.write(msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"])


def render_strategy_effectiveness_chart(strategy, outcome_logged, total_turns):
    """Show effectiveness metrics for the current strategy"""
    
    st.markdown(f"### 📊 {strategy} Effectiveness")
    
    # Calculate effectiveness score
    base_score = 50
    if outcome_logged:
        base_score += 30
    
    turn_penalty = min(20, total_turns * 2)
    effectiveness = max(0, base_score - turn_penalty)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Strategy Score", f"{effectiveness}%")
    
    with col2:
        status = "✅ Success" if outcome_logged else "⏳ In Progress"
        st.metric("Status", status)
    
    with col3:
        efficiency = "High" if total_turns < 5 else "Medium" if total_turns < 8 else "Low"
        st.metric("Efficiency", efficiency)


def render_real_time_recommendations(stage, objection_count, urgency_used, conversion_probability):
    """Provide real-time AI recommendations for the agent"""
    
    st.markdown("### 💡 AI Recommendations")
    
    recommendations = []
    
    if conversion_probability < 40:
        recommendations.append("🎯 Deploy sweetener offer (additional fee waiver)")
    
    if objection_count > 2 and urgency_used < 2:
        recommendations.append("⚡ Increase urgency tactics - mention time-limited waiver")
    
    if stage == "RESTRUCTURING_PROPOSAL" and objection_count < 2:
        recommendations.append("🎪 Customer is receptive - move to assumptive close")
    
    if objection_count > 3:
        recommendations.append("🤝 Switch to empathetic approach - rebuild rapport")
    
    if urgency_used > 3 and not objection_count:
        recommendations.append("✅ Strong position - ask for commitment now")
    
    if not recommendations:
        recommendations.append("✓ Continue current approach - metrics are balanced")
    
    for rec in recommendations:
        st.info(rec)


def render_borrower_risk_profile(profile):
    """Render detailed risk profile visualization"""
    
    st.markdown("### 🎯 Risk Profile Analysis")
    
    # Calculate risk score
    risk_score = 0
    
    dpd = profile.get('days_past_due', 0)
    if dpd > 60:
        risk_score += 40
    elif dpd > 30:
        risk_score += 25
    elif dpd > 15:
        risk_score += 10
    
    defaults = profile.get('previous_defaults', 0)
    risk_score += defaults * 20
    
    credit_score = profile.get('credit_score', 700)
    if credit_score < 600:
        risk_score += 30
    elif credit_score < 650:
        risk_score += 20
    elif credit_score < 700:
        risk_score += 10
    
    risk_score = min(100, risk_score)
    
    # Display risk gauge
    if risk_score > 70:
        st.error(f"🚨 HIGH RISK: {risk_score}/100")
    elif risk_score > 40:
        st.warning(f"⚠️ MEDIUM RISK: {risk_score}/100")
    else:
        st.success(f"✅ LOW RISK: {risk_score}/100")
    
    st.progress(risk_score / 100)
    
    # Risk factors breakdown
    st.markdown("**Risk Factors:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Days Past Due", dpd)
        st.metric("Credit Score", credit_score)
    
    with col2:
        st.metric("Previous Defaults", defaults)
        st.metric("Pending Amount", f"₹{profile.get('pending_emi', 0)}")


def render_conversion_success_celebration(conversion_time, package_chosen="Unknown"):
    """Render success animation and summary"""
    
    st.balloons()
    
    st.success("🎉 CONVERSION SUCCESSFUL!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Time to Convert", f"{conversion_time:.1f}s")
    
    with col2:
        st.metric("Package Selected", package_chosen)
    
    with col3:
        st.metric("Status", "✅ Committed")
    
    st.info("📋 Next Steps: Send payment link, schedule follow-up, update CRM")


def export_detailed_analytics(session_state, profile, strategy):
    """Generate comprehensive analytics export"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║         FLEXILOANS ADVANCED CONVERSION ANALYTICS             ║
╚══════════════════════════════════════════════════════════════╝

REPORT GENERATED: {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BORROWER INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:                {profile['customer_name']}
Loan ID:             {profile['loan_id']}
Business Type:       {profile['business_type']}
Days Past Due:       {profile['days_past_due']} days
Pending EMI:         ₹{profile['pending_emi']}
Credit Score:        {profile.get('credit_score', 'N/A')}
Previous Defaults:   {profile.get('previous_defaults', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONVERSION STRATEGY & PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Strategy Used:       {strategy}
Total Turns:         {session_state.get('total_turns', 0)}
Objections:          {session_state.get('objection_count', 0)}
Urgency Triggers:    {session_state.get('urgency_triggers_used', 0)}
Packages Mentioned:  {', '.join(session_state.get('package_mentions', [])) or 'None'}

Conversion Probability: {session_state.get('conversion_probability', 0)}%
Final Outcome:       {'✅ CONVERTED' if session_state.get('outcome_logged') else '❌ NOT CONVERTED'}
"""
    
    if session_state.get('outcome_logged') and 'conversion_time' in session_state:
        report += f"Time to Conversion: {session_state['conversion_time']:.1f} seconds\n"
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONVERSATION TRANSCRIPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    for idx, msg in enumerate(session_state.get('messages', [])):
        role = "AGENT" if msg["role"] == "model" else "CUSTOMER"
        report += f"\n[Turn {idx + 1}] {role}:\n{msg['content']}\n"
        report += "-" * 60 + "\n"
    
    report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
END OF REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return report
