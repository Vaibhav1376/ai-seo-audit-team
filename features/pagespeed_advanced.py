"""
Advanced PageSpeed Insights Integration
Mobile vs Desktop Performance Analysis
"""
import requests
import os
from typing import Dict

PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY")

def analyze_mobile_desktop(url: str) -> Dict:
    """
    Get performance scores for both mobile and desktop
    
    Args:
        url: URL to analyze
        
    Returns:
        Dict with mobile and desktop scores
    """
    print(f"📱 Analyzing mobile performance for {url}...")
    
    results = {
        "mobile": _get_pagespeed_score(url, "mobile"),
        "desktop": _get_pagespeed_score(url, "desktop"),
        "success": True
    }
    
    # Calculate difference
    if results["mobile"]["score"] and results["desktop"]["score"]:
        results["score_difference"] = results["desktop"]["score"] - results["mobile"]["score"]
        results["mobile_optimized"] = results["mobile"]["score"] >= 90
        results["desktop_optimized"] = results["desktop"]["score"] >= 90
    
    return results


def _get_pagespeed_score(url: str, strategy: str = "mobile") -> Dict:
    """
    Call PageSpeed Insights API
    
    Args:
        url: URL to test
        strategy: 'mobile' or 'desktop'
        
    Returns:
        Dict with performance data
    """
    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    params = {
        "url": url,
        "strategy": strategy,
        "category": ["performance", "accessibility", "best-practices", "seo"]
    }
    
    if PAGESPEED_API_KEY:
        params["key"] = PAGESPEED_API_KEY
    
    try:
        response = requests.get(api_url, params=params, timeout=60)
        data = response.json()
        
        if response.status_code != 200:
            return {"error": data.get("error", {}).get("message", "API error"), "score": None}
        
        # Extract scores
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        
        performance = categories.get("performance", {}).get("score", 0) * 100
        accessibility = categories.get("accessibility", {}).get("score", 0) * 100
        best_practices = categories.get("best-practices", {}).get("score", 0) * 100
        seo = categories.get("seo", {}).get("score", 0) * 100
        
        # Core Web Vitals
        audits = lighthouse.get("audits", {})
        
        lcp = audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000
        fid = audits.get("max-potential-fid", {}).get("numericValue", 0)
        cls = audits.get("cumulative-layout-shift", {}).get("numericValue", 0)
        
        return {
            "score": int(performance),
            "accessibility": int(accessibility),
            "best_practices": int(best_practices),
            "seo": int(seo),
            "core_web_vitals": {
                "lcp": round(lcp, 2),  # Largest Contentful Paint (seconds)
                "fid": round(fid, 2),  # First Input Delay (ms)
                "cls": round(cls, 3)   # Cumulative Layout Shift
            },
            "strategy": strategy,
            "success": True
        }
        
    except Exception as e:
        print(f"❌ PageSpeed API error ({strategy}): {e}")
        return {"error": str(e), "score": None, "strategy": strategy}
