# strategy_comparison.py
# Advanced Analytics Module for Strategy Comparison

class ConversionAnalytics:
    """Track and compare conversion performance across different strategies"""
    
    def __init__(self):
        self.strategy_performance = {
            "Aggressive Conversion": {
                "total_attempts": 0,
                "successful_conversions": 0,
                "avg_turns_to_conversion": 0,
                "avg_objections": 0,
                "avg_time_to_conversion": 0
            },
            "Empathetic Persuasion": {
                "total_attempts": 0,
                "successful_conversions": 0,
                "avg_turns_to_conversion": 0,
                "avg_objections": 0,
                "avg_time_to_conversion": 0
            },
            "Data-Driven Logic": {
                "total_attempts": 0,
                "successful_conversions": 0,
                "avg_turns_to_conversion": 0,
                "avg_objections": 0,
                "avg_time_to_conversion": 0
            }
        }
    
    def log_conversion_attempt(self, strategy, success, turns, objections, time_taken):
        """Log a conversion attempt with its metrics"""
        stats = self.strategy_performance[strategy]
        stats["total_attempts"] += 1
        
        if success:
            stats["successful_conversions"] += 1
            # Update running averages
            n = stats["successful_conversions"]
            stats["avg_turns_to_conversion"] = (
                (stats["avg_turns_to_conversion"] * (n-1) + turns) / n
            )
            stats["avg_objections"] = (
                (stats["avg_objections"] * (n-1) + objections) / n
            )
            stats["avg_time_to_conversion"] = (
                (stats["avg_time_to_conversion"] * (n-1) + time_taken) / n
            )
    
    def get_conversion_rate(self, strategy):
        """Calculate conversion rate for a strategy"""
        stats = self.strategy_performance[strategy]
        if stats["total_attempts"] == 0:
            return 0
        return (stats["successful_conversions"] / stats["total_attempts"]) * 100
    
    def get_best_strategy(self):
        """Determine which strategy has the highest conversion rate"""
        best_strategy = None
        best_rate = 0
        
        for strategy in self.strategy_performance:
            rate = self.get_conversion_rate(strategy)
            if rate > best_rate:
                best_rate = rate
                best_strategy = strategy
        
        return best_strategy, best_rate
    
    def generate_comparison_report(self):
        """Generate a detailed comparison report"""
        report = "STRATEGY PERFORMANCE COMPARISON\n"
        report += "=" * 50 + "\n\n"
        
        for strategy, stats in self.strategy_performance.items():
            conversion_rate = self.get_conversion_rate(strategy)
            report += f"{strategy}:\n"
            report += f"  Total Attempts: {stats['total_attempts']}\n"
            report += f"  Successful Conversions: {stats['successful_conversions']}\n"
            report += f"  Conversion Rate: {conversion_rate:.1f}%\n"
            
            if stats['successful_conversions'] > 0:
                report += f"  Avg Turns to Conversion: {stats['avg_turns_to_conversion']:.1f}\n"
                report += f"  Avg Objections: {stats['avg_objections']:.1f}\n"
                report += f"  Avg Time to Conversion: {stats['avg_time_to_conversion']:.1f}s\n"
            
            report += "\n"
        
        best_strategy, best_rate = self.get_best_strategy()
        if best_strategy:
            report += f"BEST PERFORMING STRATEGY: {best_strategy} ({best_rate:.1f}%)\n"
        
        return report


# Psychological trigger library
PSYCHOLOGICAL_TRIGGERS = {
    "urgency": [
        "This offer expires in the next hour",
        "I can only hold this waiver for a few more minutes",
        "The system updates tonight and these terms won't be available",
        "Late fees are accumulating as we speak"
    ],
    "scarcity": [
        "Only 3 waiver slots left for today",
        "This is a limited-time restructuring window",
        "We rarely offer such favorable terms",
        "Most borrowers don't get access to Package C"
    ],
    "social_proof": [
        "Over 500 borrowers chose this option this month",
        "Customers in similar situations found this most helpful",
        "This is our most popular resolution package",
        "Business owners like yourself typically prefer this option"
    ],
    "loss_aversion": [
        "Without action today, your credit score will drop further",
        "Delaying will result in additional penalty charges",
        "You'll lose access to future credit if this continues",
        "Your borrowing capacity is at risk"
    ],
    "authority": [
        "Our financial advisors recommend this approach",
        "Based on RBI guidelines, this is the optimal solution",
        "Our credit experts have designed this specifically for your situation",
        "This follows best practices in debt restructuring"
    ],
    "reciprocity": [
        "We're waiving the late fees as a gesture of goodwill",
        "I've personally secured this special approval for you",
        "We're extending this courtesy because of your history with us",
        "This is more than we typically offer"
    ]
}


def get_trigger_suggestion(objection_count, urgency_used, stage):
    """Suggest which psychological trigger to use next"""
    if objection_count > 2 and urgency_used < 2:
        return "urgency", PSYCHOLOGICAL_TRIGGERS["urgency"][0]
    elif stage == "RESTRUCTURING_PROPOSAL" and urgency_used < 1:
        return "scarcity", PSYCHOLOGICAL_TRIGGERS["scarcity"][0]
    elif objection_count > 1:
        return "social_proof", PSYCHOLOGICAL_TRIGGERS["social_proof"][0]
    else:
        return "reciprocity", PSYCHOLOGICAL_TRIGGERS["reciprocity"][0]
