# MakeThemPay MVP

A real-time, color-coded spending feedback system powered by Claude multi-agent analysis. This MVP demonstrates the core insight: **"Help users maximize lifetime utility by guiding each micro-purchase with AI."**

## Features

### Multi-Agent System

1. **Longevity Agent**: Evaluates whether the user's overall savings rate and burn rate keep them "on track" long-term
2. **Budget Agent**: Checks whether the user is already overspending in the category for the year
3. **Anomaly Agent**: Detects unusually large or unusual purchases
4. **Decision Agent**: Aggregates all signals into Green / Red / White + a short natural-language explanation

### Dynamic Auto-Investment

The system automatically calculates an investment amount based on the decision:
- **Green**: Round-up + 5% bonus
- **White**: Round-up only
- **Red**: Round-up + 10% (penalty to encourage better decisions)

### Dashboard

- Recent color-coded transactions
- Category spending overviews with progress bars
- Long-term track status (OK / Borderline / Risky)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up your API key

Create a `.env` file in the project root:
```bash
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

Or manually create `.env` with:
```
ANTHROPIC_API_KEY=sk-ant-...
```

Get your API key from: https://console.anthropic.com/

### 3. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000/`

## Usage

1. **Dashboard** (`http://localhost:5000/`): View your financial overview, recent transactions, and category spending
2. **New Purchase** (`http://localhost:5000/purchase`): Enter a purchase amount and category to get real-time AI analysis

## Project Structure

```
makethempay/
├── agent.py              # Multi-agent system implementation
├── app.py                # Flask web application
├── templates/
│   ├── dashboard.html    # Main dashboard UI
│   └── purchase.html     # Purchase interface UI
├── data/                 # JSON data storage (auto-created)
│   ├── transactions.json
│   ├── user_profile.json
│   └── budget.json
├── requirements.txt      # Python dependencies
├── .env                 # API key (not in git)
└── README.md            # This file
```

## How It Works

1. **User enters purchase**: Amount and category
2. **Multi-agent analysis**:
   - Longevity Agent checks long-term financial health
   - Budget Agent verifies category spending limits
   - Anomaly Agent detects unusual patterns
3. **Decision Agent** aggregates all signals and provides:
   - Color-coded decision (Green/White/Red)
   - Natural language explanation
   - Auto-investment amount
4. **Transaction saved** and displayed on dashboard

## Default Settings

- **Monthly Income**: $5,000
- **Current Savings**: $10,000
- **Monthly Expenses**: $3,000
- **Target Retirement Age**: 65
- **Current Age**: 30
- **Target Retirement Savings**: $1,000,000

You can modify these in `data/user_profile.json` after running the app once.

## Categories

- Food
- Transportation
- Entertainment
- Shopping
- Bills
- Other

## API Endpoints

- `GET /` - Dashboard
- `GET /purchase` - Purchase interface
- `POST /api/analyze` - Analyze a purchase (JSON: `{"amount": 150.00, "category": "food"}`)
- `GET /api/dashboard` - Get dashboard data (JSON)
- `GET /api/profile` - Get user profile (JSON)
- `POST /api/profile` - Update user profile (JSON)

## Technology Stack

- **Python 3.8+**
- **Flask** - Web framework
- **Anthropic Claude Sonnet 4.5** - AI agent system
- **JSON** - Data storage (MVP)

## Future Enhancements

- Database integration
- User authentication
- Real payment processing
- Advanced analytics
- Mobile app
- Investment account integration
