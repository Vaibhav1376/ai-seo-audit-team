from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env file")
    print("\n📝 Create a .env file with:")
    print("GOOGLE_API_KEY=your_key_here")
    exit(1)

print(f"✅ API Key found: {api_key[:20]}...")

# Test the key
try:
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    
    response = model.generate_content("Say 'API key works!'")
    print(f"\n✅ API KEY WORKS!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"\n❌ API KEY FAILED: {e}")
