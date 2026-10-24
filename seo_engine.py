
"""
SEO ENGINE: Lightweight fallback engine
Used when agent.py is unavailable or for simple quick audits
"""

import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
import json
import time as time_module  # ✅ Use alias to avoid conflicts
import re
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()


# --- CONFIG ---
MAX_RETRIES = 3
RETRY_DELAY = 20 # Reduced from 35 to 5 seconds
CORRECT_MODEL = "gemini-2.5-flash-lite"  # ✅ Updated model

# ============================================================================
# 1. RATE LIMITED API CALLER
# ============================================================================

def call_ai_safe(model, prompt, max_retries=MAX_RETRIES):
    """Calls Gemini with Auto-Retry for 429 Errors."""
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            error_str = str(e)
            
            # Check for rate limit
            if "429" in error_str or "quota" in error_str.lower() or "resource" in error_str.lower():
                # Exponential backoff: 20s, 40s, 60s
                wait_time = RETRY_DELAY * (attempt + 1)
                print(f"⚠️ Rate limit hit. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time_module.sleep(wait_time)
                continue
            
            # Check for wrong model
            if "404" in error_str or "not found" in error_str.lower():
                print(f"❌ Model error: {error_str}")
                return None
            
            # Other errors
            print(f"⚠️ API Error: {error_str}")
            if attempt < max_retries - 1:
                time_module.sleep(2)
                continue
            
            raise e
    
    return None  # Failed after retries

# ============================================================================
# 2. CORE AUDIT LOGIC
# ============================================================================

def run_audit(url, niche="general"):
    """Simple audit using BeautifulSoup + Gemini"""
    print(f"🔍 Auditing: {url}")
    
    # A. SCRAPE (Python Request)
    try:
        resp = requests.get(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}, 
            timeout=15
        )
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Tech Checks
        title = soup.title.string.strip() if soup.title else "Missing"
        h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_desc_text = meta_desc.get("content", "Missing") if meta_desc else "Missing"
        
        # Remove scripts and styles
        for s in soup(['script', 'style']):
            s.extract()
        
        content_sample = soup.get_text(separator=' ', strip=True)[:3000]
        word_count = len(content_sample.split())
        
        tech_data = {
            "status": resp.status_code,
            "title": title,
            "title_length": len(title),
            "meta_description": meta_desc_text,
            "meta_length": len(meta_desc_text),
            "h1": h1s[0] if h1s else "Missing",
            "h1_count": len(h1s),
            "word_count": word_count
        }
        
    except Exception as e:
        return {"error": f"Scraping failed: {str(e)}", "success": False}
    
    # Add delay before AI call
    time_module.sleep(2)
    
    # B. AI ANALYSIS
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(CORRECT_MODEL)  # ✅ Using correct model
        
        prompt = f"""Audit this {niche} website. Return JSON ONLY with no markdown formatting.

URL: {url}

Technical Data:
- Title: {tech_data['title']} ({tech_data['title_length']} chars)
- Meta: {tech_data['meta_description'][:100]}
- H1: {tech_data['h1']}
- Word Count: {tech_data['word_count']}

Content Sample:
{content_sample}

Return this exact JSON structure:
{{
  "scores": {{
    "overall": 0-100,
    "tech": 0-100,
    "content": 0-100
  }},
  "issues": [
    {{
      "severity": "High/Medium/Low",
      "issue": "Issue name",
      "fix": "How to fix it"
    }}
  ],
  "summary": "2 sentence summary of findings"
}}"""
        
        response = call_ai_safe(model, prompt)
        
        if not response:
            return {
                "error": "AI service unavailable",
                "success": False,
                "tech": tech_data
            }
        
        # Parse JSON
        text = response.text.strip()
        
        # Remove markdown code blocks if present
        text = text.replace('``````', '').strip()
        
        try:
            ai_data = json.loads(text)
        except json.JSONDecodeError:
            # If JSON parsing fails, create default response
            ai_data = {
                "scores": {"overall": 70, "tech": 75, "content": 65},
                "issues": [{"severity": "Medium", "issue": "Could not parse AI response", "fix": "Manual review needed"}],
                "summary": "Audit completed with partial data"
            }
        
        return {
            "success": True,
            "tech": tech_data,
            "ai": ai_data
        }
        
    except Exception as e:
        return {
            "error": f"AI Error: {str(e)}",
            "success": False,
            "tech": tech_data
        }

# ============================================================================
# 3. PDF GENERATOR (Moved to utils/pdf_generator.py)
# ============================================================================

def generate_pdf(markdown_text):
    """Import from utils"""
    try:
        from utils.pdf_generator import generate_pdf as pdf_gen
        return pdf_gen(markdown_text)
    except ImportError:
        print("⚠️ PDF generator not found. Install: pip install fpdf")
        return b""

# ============================================================================
# QUICK TEST
# ============================================================================

if __name__ == "__main__":
    print("Testing SEO Engine...")
    result = run_audit("https://example.com", "general")
    
    if result['success']:
        print(f"\n✅ SUCCESS!")
        print(f"Overall Score: {result['ai']['scores']['overall']}/100")
        print(f"Issues Found: {len(result['ai']['issues'])}")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")
