"""
External API Integrations (Moz & PageSpeed)
"""
import requests
import base64
import os

# --- MOZ API (Domain Authority) ---
def get_moz_metrics(domain):
    moz_user = os.getenv("MOZ_ACCESS_ID")
    moz_key = os.getenv("MOZ_SECRET_KEY")
    
    if not moz_user or not moz_key:
        return {"da": "N/A", "pa": "N/A", "links": "N/A"}

    # Basic Auth for Moz
    token = base64.b64encode(f"{moz_user}:{moz_key}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}
    
    # Moz V2 API Endpoint (URL Metrics)
    url = "https://lsapi.seomoz.com/v2/url_metrics"
    payload = {"targets": [domain]}
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        data = resp.json()
        metrics = data['results'][0]
        return {
            "da": metrics.get('domain_authority', 0),
            "pa": metrics.get('page_authority', 0),
            "links": metrics.get('external_equity_links', 0)
        }
    except Exception as e:
        print(f"Moz Error: {e}")
        return {"da": "Err", "pa": "Err", "links": "Err"}

# --- GOOGLE PAGESPEED API ---
def get_pagespeed(url, strategy="mobile"):
    key = os.getenv("GOOGLE_PAGESPEED_KEY") # Get this from Google Cloud Console
    if not key:
        return {"score": 0, "lcp": "N/A", "cls": "N/A"}
        
    endpoint = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}&key={key}"
    
    try:
        resp = requests.get(endpoint)
        data = resp.json()
        
        # Extract Core Vitals
        lighthouse = data['lighthouseResult']
        score = int(lighthouse['categories']['performance']['score'] * 100)
        lcp = lighthouse['audits']['largest-contentful-paint']['displayValue']
        cls = lighthouse['audits']['cumulative-layout-shift']['displayValue']
        
        return {
            "score": score,
            "lcp": lcp,
            "cls": cls
        }
    except Exception as e:
        print(f"PageSpeed Error: {e}")
        return {"score": 0, "lcp": "Err", "cls": "Err"}