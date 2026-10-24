"""
AI Manager: Handles Multi-Key Rotation and Auto-Retries.
This makes your app "invincible" to rate limits.
"""
import os
import time
import google.generativeai as genai
import random

# Load all keys from .env
AVAILABLE_KEYS = [
    os.getenv("GOOGLE_API_KEY"),
    os.getenv("GOOGLE_API_KEY_2"),
    os.getenv("GOOGLE_API_KEY_3")
]
# Filter out empty keys
VALID_KEYS = [k for k in AVAILABLE_KEYS if k]

if not VALID_KEYS:
    raise ValueError("❌ No Google API Keys found in .env!")

current_key_idx = 0

def get_active_model(model_name="gemini-1.5-flash"):
    """Configures the AI with the current active key."""
    global current_key_idx
    key = VALID_KEYS[current_key_idx]
    genai.configure(api_key=key)
    return genai.GenerativeModel(model_name)

def switch_key():
    """Switches to the next available API key."""
    global current_key_idx
    old_key = VALID_KEYS[current_key_idx]
    current_key_idx = (current_key_idx + 1) % len(VALID_KEYS)
    new_key = VALID_KEYS[current_key_idx]
    print(f"   🔄 Switching API Key: ...{old_key[-4:]} ➡️ ...{new_key[-4:]}")

def generate_with_retry(prompt, model_name="gemini-1.5-flash"):
    """
    Tries to generate content. 
    1. If 429 error -> Switches Key immediately.
    2. If all keys fail -> Waits and retries.
    """
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            model = get_active_model(model_name)
            response = model.generate_content(prompt)
            return response
            
        except Exception as e:
            error_msg = str(e)
            
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"   🛑 Quota Hit on Key {current_key_idx+1}. Rotating...")
                switch_key()
                # Slight pause to let the switch settle
                time.sleep(1)
                continue
            else:
                # If it's a real error (not quota), raise it
                raise e

    # If we ran out of retries (all keys exhausted)
    print("   ⚠️ All API keys are exhausted. Waiting 60s...")
    time.sleep(60)
    return generate_with_retry(prompt, model_name) # Recursive last effort