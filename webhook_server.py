import hmac
import hashlib
import json
from flask import Flask, request, jsonify
from utils.billing import add_credits_to_user

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    event = None

    try:
        event = json.loads(payload)
    except Exception as e:
        return "Invalid payload", 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get data from metadata we set in Step 2
        user_id = session['metadata']['user_id']
        plan = session['metadata']['plan_type']
        
        # Add credits based on plan
        amount = 10 if plan == "starter" else 100
        add_credits_to_user(user_id, amount)
        print(f"💰 Payment Received! Added {amount} credits to User {user_id}")

    return "Success", 200

if __name__ == '__main__':
    app.run(port=5000)