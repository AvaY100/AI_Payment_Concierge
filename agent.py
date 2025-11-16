import os
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model configuration - Claude Sonnet 4.5
MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 4096

# Initialize the Claude client
client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Data storage paths
DATA_DIR = "data"
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
USER_PROFILE_FILE = os.path.join(DATA_DIR, "user_profile.json")
BUDGET_FILE = os.path.join(DATA_DIR, "budget.json")


class DataStore:
    """Simple JSON-based data storage for MVP"""
    
    @staticmethod
    def ensure_data_dir():
        """Create data directory if it doesn't exist"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
    
    @staticmethod
    def load_transactions() -> List[Dict]:
        """Load all transactions"""
        DataStore.ensure_data_dir()
        if os.path.exists(TRANSACTIONS_FILE):
            with open(TRANSACTIONS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    @staticmethod
    def save_transaction(transaction: Dict):
        """Save a new transaction"""
        transactions = DataStore.load_transactions()
        transactions.append(transaction)
        DataStore.ensure_data_dir()
        with open(TRANSACTIONS_FILE, 'w') as f:
            json.dump(transactions, f, indent=2)
    
    @staticmethod
    def load_user_profile() -> Dict:
        """Load user financial profile"""
        DataStore.ensure_data_dir()
        if os.path.exists(USER_PROFILE_FILE):
            with open(USER_PROFILE_FILE, 'r') as f:
                return json.load(f)
        # Default profile
        return {
            "monthly_income": 5000,
            "current_savings": 10000,
            "monthly_expenses": 3000,
            "target_retirement_age": 65,
            "current_age": 30,
            "target_retirement_savings": 1000000
        }
    
    @staticmethod
    def save_user_profile(profile: Dict):
        """Save user profile"""
        DataStore.ensure_data_dir()
        with open(USER_PROFILE_FILE, 'w') as f:
            json.dump(profile, f, indent=2)
    
    @staticmethod
    def load_budget() -> Dict:
        """Load category budgets"""
        DataStore.ensure_data_dir()
        if os.path.exists(BUDGET_FILE):
            with open(BUDGET_FILE, 'r') as f:
                return json.load(f)
        # Default budgets
        return {
            "food": 500,
            "transportation": 300,
            "entertainment": 200,
            "shopping": 400,
            "bills": 800,
            "other": 300
        }
    
    @staticmethod
    def get_category_spending(category: str, year: int = None) -> float:
        """Get total spending for a category in a given year"""
        if year is None:
            year = datetime.now().year
        transactions = DataStore.load_transactions()
        total = 0
        for t in transactions:
            t_date = datetime.fromisoformat(t['timestamp'])
            if t['category'].lower() == category.lower() and t_date.year == year:
                total += t['amount']
        return total
    
    @staticmethod
    def initialize_sample_data():
        """Initialize sample transaction data for testing"""
        transactions = DataStore.load_transactions()
        
        # Only initialize if no transactions exist
        if len(transactions) == 0:
            sample_transactions = [
                {"amount": 45.50, "category": "food", "timestamp": (datetime.now() - timedelta(days=5)).isoformat()},
                {"amount": 32.00, "category": "food", "timestamp": (datetime.now() - timedelta(days=3)).isoformat()},
                {"amount": 120.00, "category": "shopping", "timestamp": (datetime.now() - timedelta(days=10)).isoformat()},
                {"amount": 25.00, "category": "entertainment", "timestamp": (datetime.now() - timedelta(days=7)).isoformat()},
                {"amount": 15.00, "category": "entertainment", "timestamp": (datetime.now() - timedelta(days=2)).isoformat()},
                {"amount": 80.00, "category": "transportation", "timestamp": (datetime.now() - timedelta(days=5)).isoformat()},
            ]
            
            DataStore.ensure_data_dir()
            with open(TRANSACTIONS_FILE, 'w') as f:
                json.dump(sample_transactions, f, indent=2)


class LongevityAgent:
    """Evaluates whether user's savings rate and burn rate keep them on track long-term"""
    
    def __init__(self):
        self.name = "Longevity Agent"
    
    def analyze(self, user_profile: Dict, current_transaction: Dict) -> Dict:
        """Analyze long-term financial health"""
        monthly_income = user_profile.get('monthly_income', 5000)
        current_savings = user_profile.get('current_savings', 10000)
        monthly_expenses = user_profile.get('monthly_expenses', 3000)
        current_age = user_profile.get('current_age', 30)
        target_age = user_profile.get('target_retirement_age', 65)
        target_savings = user_profile.get('target_retirement_savings', 1000000)
        
        # Calculate years to retirement
        years_to_retirement = target_age - current_age
        
        # Calculate current savings rate
        savings_rate = (monthly_income - monthly_expenses) / monthly_income if monthly_income > 0 else 0
        
        # Project future savings
        monthly_savings = monthly_income - monthly_expenses
        projected_savings = current_savings + (monthly_savings * 12 * years_to_retirement)
        
        # Calculate required savings rate
        required_savings = target_savings - current_savings
        required_monthly_savings = required_savings / (years_to_retirement * 12) if years_to_retirement > 0 else 0
        required_savings_rate = required_monthly_savings / monthly_income if monthly_income > 0 else 0
        
        # Use Claude to generate analysis
        prompt = f"""You are a Longevity Agent evaluating long-term financial health.

User Profile:
- Monthly Income: ${monthly_income:,.2f}
- Current Savings: ${current_savings:,.2f}
- Monthly Expenses: ${monthly_expenses:,.2f}
- Current Age: {current_age}
- Target Retirement Age: {target_age}
- Target Retirement Savings: ${target_savings:,.2f}

Calculations:
- Current Savings Rate: {savings_rate:.1%}
- Years to Retirement: {years_to_retirement}
- Projected Savings at Retirement: ${projected_savings:,.2f}
- Required Monthly Savings: ${required_monthly_savings:,.2f}
- Required Savings Rate: {required_savings_rate:.1%}

Current Transaction:
- Amount: ${current_transaction['amount']:,.2f}
- Category: {current_transaction['category']}

Provide a concise analysis (2-3 sentences) evaluating:
1. Whether the user is on track for retirement
2. How this transaction impacts their long-term goals
3. A status: "OK", "BORDERLINE", or "RISKY"

Format your response as JSON:
{{
    "status": "OK|BORDERLINE|RISKY",
    "analysis": "brief analysis text",
    "score": 0.0-1.0
}}
"""
        
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text
            
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback
                result = {
                    "status": "BORDERLINE" if savings_rate < required_savings_rate else "OK",
                    "analysis": response_text[:200],
                    "score": min(1.0, savings_rate / required_savings_rate) if required_savings_rate > 0 else 0.5
                }
            
            return result
        except Exception as e:
            # Fallback calculation
            status = "OK" if savings_rate >= required_savings_rate * 0.9 else "BORDERLINE" if savings_rate >= required_savings_rate * 0.7 else "RISKY"
            return {
                "status": status,
                "analysis": f"Current savings rate {savings_rate:.1%} vs required {required_savings_rate:.1%}",
                "score": min(1.0, savings_rate / required_savings_rate) if required_savings_rate > 0 else 0.5
            }


class BudgetAgent:
    """Checks whether user is overspending in the category for the year"""
    
    def __init__(self):
        self.name = "Budget Agent"
    
    def analyze(self, category: str, amount: float) -> Dict:
        """Analyze budget status for category"""
        budget = DataStore.load_budget()
        category_budget = budget.get(category.lower(), budget.get('other', 300))
        
        # Get spending for this year
        current_year = datetime.now().year
        year_spending = DataStore.get_category_spending(category, current_year)
        
        # Calculate remaining budget
        remaining_budget = category_budget * 12 - year_spending  # Annual budget
        projected_spending = year_spending + amount
        
        # Calculate percentage used
        annual_budget = category_budget * 12
        percentage_used = (projected_spending / annual_budget * 100) if annual_budget > 0 else 0
        
        # Use Claude to generate analysis
        prompt = f"""You are a Budget Agent checking category spending limits.

Category: {category}
Annual Budget: ${annual_budget:,.2f}
Spent This Year (before this transaction): ${year_spending:,.2f}
Current Transaction: ${amount:,.2f}
Projected Annual Spending: ${projected_spending:,.2f}
Remaining Budget: ${remaining_budget:,.2f}
Percentage of Budget Used: {percentage_used:.1f}%

Provide a concise analysis (2-3 sentences) evaluating:
1. Whether this purchase fits within the budget
2. How it impacts the annual spending plan
3. A status: "OK", "BORDERLINE", or "RISKY"

Format your response as JSON:
{{
    "status": "OK|BORDERLINE|RISKY",
    "analysis": "brief analysis text",
    "score": 0.0-1.0
}}
"""
        
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text
            
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback
                if percentage_used <= 80:
                    status = "OK"
                elif percentage_used <= 100:
                    status = "BORDERLINE"
                else:
                    status = "RISKY"
                
                result = {
                    "status": status,
                    "analysis": f"Using {percentage_used:.1f}% of annual {category} budget",
                    "score": max(0, 1.0 - (percentage_used / 100))
                }
            
            return result
        except Exception as e:
            # Fallback calculation
            if percentage_used <= 80:
                status = "OK"
            elif percentage_used <= 100:
                status = "BORDERLINE"
            else:
                status = "RISKY"
            
            return {
                "status": status,
                "analysis": f"Using {percentage_used:.1f}% of annual {category} budget",
                "score": max(0, 1.0 - (percentage_used / 100))
            }


class AnomalyAgent:
    """Detects unusually large or unusual purchases"""
    
    def __init__(self):
        self.name = "Anomaly Agent"
    
    def analyze(self, category: str, amount: float) -> Dict:
        """Detect anomalies in purchase"""
        transactions = DataStore.load_transactions()
        
        # Calculate statistics
        if transactions:
            amounts = [t['amount'] for t in transactions]
            avg_amount = sum(amounts) / len(amounts)
            max_amount = max(amounts)
            
            # Category-specific stats
            category_transactions = [t for t in transactions if t['category'].lower() == category.lower()]
            if category_transactions:
                category_amounts = [t['amount'] for t in category_transactions]
                category_avg = sum(category_amounts) / len(category_amounts)
                category_max = max(category_amounts)
            else:
                category_avg = avg_amount
                category_max = max_amount
        else:
            avg_amount = amount
            max_amount = amount
            category_avg = amount
            category_max = amount
        
        # Calculate anomaly score
        is_large = amount > category_avg * 3
        is_very_large = amount > category_max * 1.5
        
        # Use Claude to generate analysis
        prompt = f"""You are an Anomaly Agent detecting unusual purchases.

Transaction:
- Amount: ${amount:,.2f}
- Category: {category}

Historical Context:
- Average Transaction: ${avg_amount:,.2f}
- Max Transaction: ${max_amount:,.2f}
- Category Average: ${category_avg:,.2f}
- Category Max: ${category_max:,.2f}

This transaction is:
- {amount / category_avg:.1f}x the category average
- {amount / category_max:.1f}x the category maximum

Provide a concise analysis (2-3 sentences) evaluating:
1. Whether this is an unusual purchase
2. If it's unusually large for this category
3. A status: "OK", "BORDERLINE", or "RISKY"

Format your response as JSON:
{{
    "status": "OK|BORDERLINE|RISKY",
    "analysis": "brief analysis text",
    "score": 0.0-1.0
}}
"""
        
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text
            
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback
                if is_very_large:
                    status = "RISKY"
                elif is_large:
                    status = "BORDERLINE"
                else:
                    status = "OK"
                
                result = {
                    "status": status,
                    "analysis": f"This is {amount / category_avg:.1f}x your average {category} purchase",
                    "score": 1.0 if not is_large else (0.5 if not is_very_large else 0.2)
                }
            
            return result
        except Exception as e:
            # Fallback calculation
            if is_very_large:
                status = "RISKY"
            elif is_large:
                status = "BORDERLINE"
            else:
                status = "OK"
            
            return {
                "status": status,
                "analysis": f"This is {amount / category_avg:.1f}x your average {category} purchase",
                "score": 1.0 if not is_large else (0.5 if not is_very_large else 0.2)
            }


class DecisionAgent:
    """Aggregates all signals into Green/Red/White + explanation"""
    
    def __init__(self):
        self.name = "Decision Agent"
    
    def aggregate(self, longevity_result: Dict, budget_result: Dict, anomaly_result: Dict, amount: float) -> Dict:
        """Aggregate all agent signals into final decision"""
        
        # Calculate weighted score
        weights = {
            "longevity": 0.4,
            "budget": 0.35,
            "anomaly": 0.25
        }
        
        overall_score = (
            longevity_result.get('score', 0.5) * weights['longevity'] +
            budget_result.get('score', 0.5) * weights['budget'] +
            anomaly_result.get('score', 0.5) * weights['anomaly']
        )
        
        # Determine color
        if overall_score >= 0.7:
            color = "GREEN"
        elif overall_score >= 0.4:
            color = "WHITE"
        else:
            color = "RED"
        
        # Calculate auto-investment amount
        # Green: round up + 5%, White: round up, Red: round up + 10% (penalty)
        if color == "GREEN":
            round_up = max(1, round(amount) - amount)
            auto_invest = round_up + (amount * 0.05)
        elif color == "WHITE":
            round_up = max(1, round(amount) - amount)
            auto_invest = round_up
        else:  # RED
            round_up = max(1, round(amount) - amount)
            auto_invest = round_up + (amount * 0.10)
        
        # Use Claude to generate explanation
        prompt = f"""You are a Decision Agent providing final purchase guidance.

Agent Analysis:
- Longevity Agent: {longevity_result.get('status')} - {longevity_result.get('analysis', '')}
- Budget Agent: {budget_result.get('status')} - {budget_result.get('analysis', '')}
- Anomaly Agent: {anomaly_result.get('status')} - {anomaly_result.get('analysis', '')}

Overall Score: {overall_score:.2f}
Decision: {color}

Transaction Amount: ${amount:,.2f}
Auto-Investment Amount: ${auto_invest:,.2f}

Provide a natural, friendly explanation (2-3 sentences) that:
1. Summarizes the key factors
2. Explains why this is {color}:
   - GREEN: Purchase is healthy and within budget
   - WHITE: Purchase is acceptable but could be optimized (may be too small or slightly over)
   - RED: Purchase exceeds budget or poses financial risk
3. Mentions the auto-investment amount

Be conversational and helpful, not judgmental.
"""
        
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            explanation = message.content[0].text
        except Exception as e:
            explanation = f"Based on your financial profile, this purchase is {color}. Auto-invest ${auto_invest:,.2f}."
        
        return {
            "color": color,
            "explanation": explanation,
            "auto_invest": round(auto_invest, 2),
            "score": overall_score,
            "agent_results": {
                "longevity": longevity_result,
                "budget": budget_result,
                "anomaly": anomaly_result
            }
        }


class MultiAgentSystem:
    """Main multi-agent system orchestrator"""
    
    def __init__(self):
        self.longevity_agent = LongevityAgent()
        self.budget_agent = BudgetAgent()
        self.anomaly_agent = AnomalyAgent()
        self.decision_agent = DecisionAgent()
        # Initialize sample data if needed
        DataStore.initialize_sample_data()
    
    def analyze_purchase(self, amount: float, category: str, include_steps: bool = False) -> Dict:
        """Analyze a purchase using all agents"""
        
        # Create transaction object
        transaction = {
            "amount": amount,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get user profile
        user_profile = DataStore.load_user_profile()
        
        steps = [] if include_steps else None
        
        # Run all agents with step tracking
        if include_steps:
            steps.append({
                "agent": "Longevity Agent",
                "status": "analyzing",
                "description": "Evaluating long-term financial health..."
            })
        longevity_result = self.longevity_agent.analyze(user_profile, transaction)
        if include_steps:
            steps.append({
                "agent": "Longevity Agent",
                "status": "completed",
                "result": longevity_result
            })
        
        if include_steps:
            steps.append({
                "agent": "Budget Agent",
                "status": "analyzing",
                "description": "Checking category budget limits..."
            })
        budget_result = self.budget_agent.analyze(category, amount)
        if include_steps:
            steps.append({
                "agent": "Budget Agent",
                "status": "completed",
                "result": budget_result
            })
        
        if include_steps:
            steps.append({
                "agent": "Anomaly Agent",
                "status": "analyzing",
                "description": "Detecting unusual purchase patterns..."
            })
        anomaly_result = self.anomaly_agent.analyze(category, amount)
        if include_steps:
            steps.append({
                "agent": "Anomaly Agent",
                "status": "completed",
                "result": anomaly_result
            })
        
        if include_steps:
            steps.append({
                "agent": "Decision Agent",
                "status": "analyzing",
                "description": "Aggregating all signals into final decision..."
            })
        # Aggregate decision
        decision = self.decision_agent.aggregate(
            longevity_result, budget_result, anomaly_result, amount
        )
        if include_steps:
            steps.append({
                "agent": "Decision Agent",
                "status": "completed",
                "result": decision
            })
        
        # Add decision to transaction
        transaction['decision'] = decision
        transaction['color'] = decision['color']
        
        # Save transaction
        DataStore.save_transaction(transaction)
        
        result = {
            "transaction": transaction,
            "decision": decision
        }
        
        if include_steps:
            result["steps"] = steps
        
        return result
    
    def get_dashboard_data(self) -> Dict:
        """Get data for dashboard"""
        transactions = DataStore.load_transactions()
        user_profile = DataStore.load_user_profile()
        budget = DataStore.load_budget()
        
        # Recent transactions (last 10)
        recent = sorted(transactions, key=lambda x: x['timestamp'], reverse=True)[:10]
        
        # Category spending this year
        current_year = datetime.now().year
        category_spending = {}
        for cat in budget.keys():
            category_spending[cat] = {
                "budget": budget[cat] * 12,
                "spent": DataStore.get_category_spending(cat, current_year)
            }
        
        # Long-term status
        longevity_agent = LongevityAgent()
        dummy_transaction = {"amount": 0, "category": "other"}
        longevity_result = longevity_agent.analyze(user_profile, dummy_transaction)
        long_term_status = longevity_result.get('status', 'BORDERLINE')
        
        return {
            "recent_transactions": recent,
            "category_spending": category_spending,
            "long_term_status": long_term_status,
            "user_profile": user_profile
        }


if __name__ == "__main__":
    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key:")
        print("  ANTHROPIC_API_KEY=your_api_key_here")
        exit(1)
    
    # Initialize system
    system = MultiAgentSystem()
    
    # Test example
    print("🤖 Multi-Agent Financial Analysis System")
    print("=" * 50)
    result = system.analyze_purchase(150.00, "food")
    print(f"\nDecision: {result['decision']['color']}")
    print(f"Explanation: {result['decision']['explanation']}")
    print(f"Auto-Invest: ${result['decision']['auto_invest']:.2f}")
