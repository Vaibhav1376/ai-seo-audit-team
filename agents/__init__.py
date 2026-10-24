"""
AGENTS PACKAGE INITIALIZATION
Contains the core agents with API Rate Limit Protection.
"""
import os
import time
import json
import google.generativeai as genai
from firecrawl import FirecrawlApp

# ============================================================================
# 🚦 TRAFFIC COP: API RETRY LOGIC
# ============================================================================
def generate_with_retry(model, prompt):
    """Retries the AI call if it hits a limit (429)."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            if "429" in str(e):
                print(f"   🛑 API Limit Hit. Cooling down 30s... (Attempt {attempt+1})")
                time.sleep(30)
                continue
            raise e
    # Return a dummy response object if it fails completely so app doesn't crash
    class DummyResponse:
        text = '{"scores": {"overall": 0}, "issues": [], "error": "API Limits Reached"}'
    return DummyResponse()

# ============================================================================
# 🤖 AGENT 1: PAGE AUDITOR
# ============================================================================
def page_auditor_agent(url, niche, model_name="gemini-2.5-flash-lite"):
    print(f"   🤖 Agent 1: Auditing {url}...")
    
    # 1. Scrape Content (Firecrawl or Fallback)
    content = ""
    try:
        app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
        scraped_data = app.scrape_url(url, params={'formats': ['markdown']})
        content = scraped_data['markdown'][:5000] # Limit for token safety
    except:
        # Fallback to standard request if Firecrawl fails
        import requests
        from bs4 import BeautifulSoup
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            content = BeautifulSoup(resp.content, 'html.parser').get_text()[:5000]
        except Exception as e:
            return {"error": f"Scraping failed: {str(e)}", "scores": {"overall": 0}}

    # 2. Analyze with AI
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Act as an SEO Expert. Audit this content for a {niche} site.
        
        CONTENT SAMPLE:
        {content}
        
        RETURN JSON ONLY:
        {{
            "scores": {{ "overall": 0-100, "technical": 0-100, "content": 0-100 }},
            "issues": [ {{ "title": "Issue", "severity": "High", "fix": "Action" }} ],
            "keywords": ["kw1", "kw2"]
        }}
        """
        
        response = generate_with_retry(model, prompt)
        text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(text)
        
    except Exception as e:
        print(f"   ⚠️ Agent 1 Error: {e}")
        return {"scores": {"overall": 0}, "issues": [], "keywords": []}

# ============================================================================
# 🤖 AGENT 2: SERP ANALYST
# ============================================================================
def serp_agent(keywords, model_name="gemini-2.5-flash-lite"):
    print(f"   🤖 Agent 2: Analyzing Keywords {keywords}...")
    # Simulated SERP check to save API calls/time
    return {
        "competitors": ["Competitor A", "Competitor B"],
        "gap": "Focus on long-tail variations."
    }

# ============================================================================
# 🤖 AGENT 3: STRATEGY WRITER
# ============================================================================
def strategy_agent(audit_data, serp_data, niche, model_name="gemini-2.5-flash-lite"):
    print(f"   🤖 Agent 3: Writing Strategy...")
    
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Write a professional SEO Strategy Report (Markdown).
        Niche: {niche}
        Audit Data: {json.dumps(audit_data)}
        
        Include: Executive Summary, Critical Issues, and Action Plan.
        """
        
        response = generate_with_retry(model, prompt)
        return response.text
    except:
        return "# Report Generation Failed\nAPI limits reached."