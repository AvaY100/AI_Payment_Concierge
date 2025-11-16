from flask import Flask, render_template, request, jsonify
import os
import subprocess
import json as json_lib
from agent import MultiAgentSystem, DataStore

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Add min function to Jinja2 environment
app.jinja_env.globals.update(min=min)

# Initialize multi-agent system
system = MultiAgentSystem()

# Categories
CATEGORIES = [
    "food", "transportation", "entertainment", 
    "shopping", "bills", "other"
]


@app.route('/')
def index():
    """Main dashboard"""
    dashboard_data = system.get_dashboard_data()
    return render_template('dashboard.html', **dashboard_data)


@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    """Purchase interface"""
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            category = request.form.get('category', 'other')
            
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400
            
            if category not in CATEGORIES:
                category = 'other'
            
            # Analyze purchase
            result = system.analyze_purchase(amount, category)
            
            return jsonify({
                "success": True,
                "decision": result['decision'],
                "transaction": {
                    "amount": amount,
                    "category": category,
                    "timestamp": result['transaction']['timestamp']
                }
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return render_template('purchase.html', categories=CATEGORIES)


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for purchase analysis"""
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        category = data.get('category', 'other')
        
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
        
        if category not in CATEGORIES:
            category = 'other'
        
        result = system.analyze_purchase(amount, category)
        
        return jsonify({
            "success": True,
            "decision": result['decision'],
            "transaction": result['transaction']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint for dashboard data"""
    try:
        dashboard_data = system.get_dashboard_data()
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/profile', methods=['GET', 'POST'])
def api_profile():
    """API endpoint for user profile"""
    if request.method == 'POST':
        try:
            profile = request.get_json()
            DataStore.save_user_profile(profile)
            return jsonify({"success": True, "profile": profile})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    profile = DataStore.load_user_profile()
    return jsonify(profile)


@app.route('/locus-transaction', methods=['GET'])
def locus_transaction_page():
    """Locus transaction interface with agent analysis"""
    return render_template('locus_transaction.html', categories=CATEGORIES)


@app.route('/api/locus/analyze-with-steps', methods=['POST'])
def api_locus_analyze_with_steps():
    """API endpoint for purchase analysis with detailed steps"""
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        category = data.get('category', 'other')
        
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
        
        if category not in CATEGORIES:
            category = 'other'
        
        # Analyze with steps
        result = system.analyze_purchase(amount, category, include_steps=True)
        
        return jsonify({
            "success": True,
            "decision": result['decision'],
            "transaction": result['transaction'],
            "steps": result.get('steps', [])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/locus/send-payment', methods=['POST'])
def api_locus_send_payment():
    """API endpoint to send payment via Locus MCP"""
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        category = data.get('category', 'other')
        recipient = data.get('recipient', '')  # email or address
        recipient_type = data.get('recipient_type', 'email')  # 'email' or 'address'
        memo = data.get('memo', f'Payment for {category}')
        
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
        
        if not recipient:
            return jsonify({"error": "Recipient is required"}), 400
        
        # First analyze the purchase
        analysis_result = system.analyze_purchase(amount, category, include_steps=True)
        decision_color = analysis_result['decision']['color']
        
        # Block transaction if RED, allow GREEN and WHITE
        if decision_color == "RED":
            return jsonify({
                "success": False,
                "blocked": True,
                "reason": "Transaction blocked due to financial risk",
                "decision": analysis_result['decision'],
                "analysis": analysis_result
            }), 403
        
        # Proceed with transaction for GREEN and WHITE
        # Call Locus MCP via Node.js script
        locus_script_path = os.path.join(os.path.dirname(__file__), 'my-locus-app', 'send_payment.js')
        
        # Create a temporary script to send payment
        script_content = f"""
import 'dotenv/config';
import {{ query }} from '@anthropic-ai/claude-agent-sdk';

const mcpServers = {{
  'locus': {{
    type: 'http',
    url: 'https://mcp.paywithlocus.com/mcp',
    headers: {{
      'Authorization': `Bearer ${{process.env.LOCUS_API_KEY}}`
    }}
  }}
}};

const options = {{
  mcpServers,
  allowedTools: ['mcp__locus__*'],
  apiKey: process.env.ANTHROPIC_API_KEY,
  canUseTool: async (toolName, input) => {{
    if (toolName.startsWith('mcp__locus__')) {{
      return {{ behavior: 'allow', updatedInput: input }};
    }}
    return {{ behavior: 'deny' }};
  }}
}};

const recipient = '{recipient}';
const amount = {amount};
const memo = '{memo}';
const recipientType = '{recipient_type}';

let result = null;
let error = null;

for await (const message of query({{
  prompt: recipientType === 'email' 
    ? `请使用 send_to_email 工具向邮箱 ${{recipient}} 发送 ${{amount}} USDC，备注为"${{memo}}"` 
    : `请使用 send_to_address 工具向地址 ${{recipient}} 发送 ${{amount}} USDC，备注为"${{memo}}"`,
  options
}})) {{
  if (message.type === 'result' && message.subtype === 'success') {{
    result = message.result;
  }} else if (message.type === 'error_during_execution') {{
    error = message.error;
  }}
}}

if (error) {{
  console.error(JSON.stringify({{ error: error }}));
  process.exit(1);
}} else {{
  console.log(JSON.stringify({{ success: true, result }}));
}}
"""
        
        # Write temporary script
        temp_script = os.path.join(os.path.dirname(__file__), 'my-locus-app', 'temp_send_payment.js')
        with open(temp_script, 'w') as f:
            f.write(script_content)
        
        try:
            # Run Node.js script
            env = os.environ.copy()
            result = subprocess.run(
                ['node', temp_script],
                cwd=os.path.join(os.path.dirname(__file__), 'my-locus-app'),
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )
            
            if result.returncode != 0:
                return jsonify({
                    "success": False,
                    "error": result.stderr or "Payment failed",
                    "analysis": analysis_result
                }), 500
            
            # Parse result
            locus_result = json_lib.loads(result.stdout)
            
            return jsonify({
                "success": True,
                "payment": locus_result,
                "analysis": analysis_result
            })
        finally:
            # Clean up temp script
            if os.path.exists(temp_script):
                os.remove(temp_script)
        
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Payment request timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key:")
        print("  ANTHROPIC_API_KEY=your_api_key_here")
        exit(1)
    
    print("🚀 Starting MakeThemPay MVP Server...")
    print("📊 Dashboard: http://localhost:5001/")
    print("💳 Purchase Interface: http://localhost:5001/purchase")
    print("🌐 Locus Transaction: http://localhost:5001/locus-transaction")
    app.run(debug=True, port=5001)

