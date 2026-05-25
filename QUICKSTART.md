# 🚀 FlexiLoans AI Agent - Quick Start Guide

## Installation (30 seconds)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## 🎯 Quick Demo Flow (2 minutes)

### Step 1: Select a Borrower Profile
In the left sidebar, choose from 6 different borrower personas:
- **Case_001_Cooperative** - Easy mode (good for first test)
- **Case_002_Hostile_Adversarial** - Hard mode (test compliance)
- **Case_003_Indecisive_Procrastinator** - Medium difficulty
- **Case_004_Financial_Distress** - Requires empathy
- **Case_005_Negotiation_Expert** - Strategic challenge
- **Case_006_Silent_Avoider** - Engagement challenge

### Step 2: Choose a Conversion Strategy
Select one of three AI strategies:
- **Aggressive Conversion** - Fast, high-pressure
- **Empathetic Persuasion** - Slow, trust-building
- **Data-Driven Logic** - Fact-based approach

### Step 3: Start Chatting
Type responses as the borrower. Try these scenarios:

**Scenario A - Quick Conversion:**
```
You: I'm having cash flow issues
Bot: [Presents packages]
You: Package A sounds good, I can pay tomorrow
Bot: [COMMITMENT_LOGGED]
```

**Scenario B - Adversarial Test:**
```
You: This is harassment! Leave me alone!
Bot: [De-escalates professionally]
You: I'm not paying anything
Bot: [Continues with empathy and options]
```

**Scenario C - Negotiation:**
```
You: Can you waive more fees?
Bot: [Offers sweeteners]
You: What if I pay 30% instead of 50%?
Bot: [Negotiates within boundaries]
```

### Step 4: Watch the Metrics
Monitor in real-time:
- **Conversion Funnel Progress** (33% → 66% → 100%)
- **Conversion Probability Gauge** (updates live)
- **Objection Counter** (tracks resistance)
- **Urgency Triggers** (psychological tactics used)

### Step 5: Export Analytics
After conversation ends:
1. Click "📊 Export Analytics Report"
2. Click "💾 Download Report"
3. Review detailed transcript and metrics

## 🎪 Advanced Features to Explore

### A/B Testing
1. Run same borrower with different strategies
2. Compare conversion rates
3. Identify best approach per persona

### Psychological Triggers
Watch for these in bot responses:
- ⚡ **Urgency**: "right now", "today", "limited time"
- 🎯 **Scarcity**: "only 3 slots left"
- 👥 **Social Proof**: "500 borrowers chose this"
- 💰 **Loss Aversion**: "credit score will drop"
- 🎁 **Reciprocity**: "we're waiving fees for you"

### Live Recommendations
The AI provides real-time coaching:
- "Deploy sweetener offer"
- "Increase urgency tactics"
- "Switch to empathetic approach"

## 🏆 Hackathon Judging Points

### Test These Features:
1. **Compliance Testing** - Try to make bot violate RBI rules
2. **Conversion Speed** - How fast can you get commitment?
3. **Strategy Comparison** - Which works best per persona?
4. **Analytics Depth** - Export and review detailed reports
5. **Edge Cases** - Silent customer, abusive language, unreasonable demands

## 📊 Success Metrics to Highlight

- **Conversion Rate**: % of conversations ending in commitment
- **Time to Conversion**: Seconds from start to [COMMITMENT_LOGGED]
- **Efficiency Score**: 100 - (turns × 10) - (objections × 15)
- **Strategy Effectiveness**: Compare across all 3 approaches

## 🐛 Troubleshooting

**Issue**: API key error
**Fix**: Set environment variable or use included fallback key

**Issue**: Slow responses
**Fix**: Check internet connection (calls Google Gemini API)

**Issue**: Metrics not updating
**Fix**: Click "🔄 Reset Chat Journey" to reinitialize

## 💡 Pro Tips

1. **For Judges**: Test adversarial scenarios to see compliance boundaries
2. **For Demo**: Start with Case_001 + Aggressive strategy for quick win
3. **For Analysis**: Run all 6 personas with same strategy, compare results
4. **For Impact**: Show conversion probability gauge updating in real-time

## 🎯 Key Differentiators

✅ Real-time conversion probability calculation
✅ 3-stage visual funnel tracking
✅ A/B testing framework built-in
✅ Psychological trigger detection
✅ Live AI recommendations
✅ Comprehensive analytics export
✅ 6 diverse borrower personas
✅ RBI compliance maintained

## 📞 Next Steps

After testing:
1. Review exported analytics reports
2. Compare strategy effectiveness
3. Identify best persona-strategy combinations
4. Present conversion rate improvements

---

**Ready to start?** Run `streamlit run app.py` and begin testing! 🚀
