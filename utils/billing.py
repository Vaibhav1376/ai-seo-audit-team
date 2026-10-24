import stripe
import os
import streamlit as st
from utils.db import get_db_connection

# Use your Stripe Secret Key from .env
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Replace these with the Price IDs you got from Stripe Dashboard
PRICE_MODELS = {
    "starter": "price_your_starter_id",
    "agency": "price_your_agency_id"
}

def create_checkout_session(user_id, email, plan_type):
    """Generate a Stripe Checkout Link"""
    price_id = PRICE_MODELS.get(plan_type)
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=email,
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            # Success/Cancel URLs (Change these when you deploy)
            success_url="http://localhost:8501/?payment=success",
            cancel_url="http://localhost:8501/?payment=cancel",
            metadata={
                "user_id": user_id,
                "plan_type": plan_type
            }
        )
        return session.url
    except Exception as e:
        return f"Error: {str(e)}"

def add_credits_to_user(user_id, amount):
    """Add credits to DB after payment success"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET credits = credits + %s WHERE id = %s",
        (amount, user_id)
    )
    conn.commit()
    conn.close()