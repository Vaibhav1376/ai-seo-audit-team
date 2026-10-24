"""
Commercial API Integrations
Handles Moz (DA/PA), PageSpeed (Core Vitals), and ScraperAPI.
"""
import os
import requests
import base64
import json

# --- 1. GOOGLE PAGESPEED INSIGHTS ---
def get_pagespeed_metrics(url, strategy="mobile"):
    """Fetches Core Web Vitals from Google."""
    key = os.getenv("PAGESPEED_API_KEY")
    if not key:
        return {"score": 0, "lcp": "N/A", "cls": "N/A", "error": "Missing API Key"}

    print(f"   ⚡ Checking PageSpeed ({strategy})...")
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}&key={key}"

    try:
        response = requests.get(api_url, timeout=60)
        data = response.json()
        
        # Parse Lighthouse Data
        lighthouse = data.get('lighthouseResult', {})
        audits = lighthouse.get('audits', {})
        categories = lighthouse.get('categories', {})
        
        return {
            "score": int(categories.get('performance', {}).get('score', 0) * 100),
            "lcp": audits.get('largest-contentful-paint', {}).get('displayValue', "N/A"),
            "cls": audits.get('cumulative-layout-shift', {}).get('displayValue', "N/A"),
            "fcp": audits.get('first-contentful-paint', {}).get('displayValue', "N/A"),
            "speed_index": audits.get('speed-index', {}).get('displayValue', "N/A")
        }
    except Exception as e:
        print(f"   ❌ PageSpeed Error: {e}")
        return {"score": 0, "lcp": "Error", "cls": "Error"}

# --- 2. MOZ DOMAIN AUTHORITY ---
def get_domain_authority(url):
    """Fetches DA/PA from Moz V2 API."""
    moz_id = os.getenv("MOZ_ACCESS_ID")
    moz_secret = os.getenv("MOZ_SECRET_KEY")
    
    if not moz_id or not moz_secret:
        return {"da": 0, "pa": 0, "links": 0}

    print("   🦅 Checking Moz Authority...")
    
    # Moz Authentication
    token = base64.b64encode(f"{moz_id}:{moz_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}
    
    # Clean URL to Domain
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.replace("www.", "")
    
    endpoint = "https://lsapi.seomoz.com/v2/url_metrics"
    payload = {
        "targets": [domain],
        "metrics": ["domain_authority", "page_authority", "external_equity_links"]
    }

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            res = data['results'][0]
            return {
                "da": res.get('domain_authority', 0),
                "pa": res.get('page_authority', 0),
                "links": res.get('external_equity_links', 0)
            }
    except Exception as e:
        print(f"   ❌ Moz Error: {e}")
    
    return {"da": "N/A", "pa": "N/A", "links": "N/A"}

# --- 3. SCRAPERAPI PROXY WRAPPER ---
def scrape_via_proxy(url):
    """
    Routes request through ScraperAPI to bypass strict firewalls.
    """
    scraper_key = os.getenv("SCRAPERAPI_KEY")
    if not scraper_key:
        return requests.get(url, timeout=15) # Fallback to normal request

    payload = {
        'api_key': scraper_key, 
        'url': url, 
        'render': 'true' # Renders JS (React/Angular sites)
    }
    return requests.get('http://api.scraperapi.com', params=payload, timeout=60)