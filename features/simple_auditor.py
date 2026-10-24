"""
Simple Auditor for Full Site Crawl
A standalone, unbreakable function to audit pages quickly.
"""
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
import json
import time
import random
import re

# Load API Key safely
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Stealth Headers
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
]

def get_headers():
    return {'User-Agent': random.choice(USER_AGENTS)}

def simple_page_audit(url, model=None, features=None):
    """
    A standalone function that takes a URL and returns a dictionary.
    No complex Agent objects. Just Input -> Output.
    """
    print(f"   🕵️‍♀️ Simple Audit: {url}")
    
    # 1. Fetch
    try:
        time.sleep(0.5)
        # Try HTTPS first, then HTTP
        try:
            resp = requests.get(url, headers=get_headers(), timeout=10)
        except:
            if url.startswith("https"):
                fallback = url.replace("https", "http")
                resp = requests.get(fallback, headers=get_headers(), timeout=10)
            else:
                raise

        if resp.status_code != 200:
            return {"success": False, "error": f"HTTP {resp.status_code}", "scores": {"overall_score": 0}}
            
    except Exception as e:
        return {"success": False, "error": str(e), "scores": {"overall_score": 0}}

    # 2. Parse
    try:
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Basic Metrics
        title = soup.title.string if soup.title else "No Title"
        text = soup.get_text(separator=' ', strip=True)[:3000]
        word_count = len(text.split())
        h1_count = len(soup.find_all('h1'))
        
        # 3. Quick AI Score
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        prompt = f"""
        Audit this SEO data. URL: {url}
        Title: {title}
        H1 Count: {h1_count}
        Word Count: {word_count}
        Content Sample: {text[:1000]}...
        
        Return JSON ONLY:
        {{
            "scores": {{ "overall_score": 0-100, "on_page_score": 0-100, "technical_score": 0-100, "content_score": 0-100 }},
            "technical_issues": ["issue1", "issue2"],
            "content_gaps": ["gap1"]
        }}
        """
        
        ai_resp = model.generate_content(prompt)
        clean_json = ai_resp.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        return {
            "success": True,
            "url": url,
            "scores": data.get("scores"),
            "technical_issues": data.get("technical_issues", []),
            "audit_data": data
        }
        
    except Exception as e:
        # Fallback if AI fails
        return {
            "success": True,
            "url": url,
            "scores": {"overall_score": 50, "technical_score": 50},
            "technical_issues": ["AI Analysis Failed"],
            "audit_data": {}
        }