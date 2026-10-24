"""
Enhanced Backlink Analysis with Moz API - Feature #2
"""
import os
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict
import hashlib
import hmac
import time
import base64

def get_moz_domain_authority(url: str) -> Dict:
    """
    Get accurate Moz Domain Authority and metrics
    
    Args:
        url: URL to analyze
        
    Returns:
        Dict with Moz metrics
    """
    
    moz_id = os.getenv("MOZ_ACCESS_ID")
    moz_secret = os.getenv("MOZ_SECRET_KEY")
    
    if not moz_id or not moz_secret:
        return {
            "success": False,
            "error": "Moz API credentials not configured",
            "note": "Add MOZ_ACCESS_ID and MOZ_SECRET_KEY to .env"
        }
    
    try:
        print("Fetching Moz metrics...")
        
        # Moz API v2 endpoint
        endpoint = "https://lsapi.seomoz.com/v2/url_metrics"
        
        # Authentication
        auth = HTTPBasicAuth(moz_id, moz_secret)
        
        # Request payload
        payload = {
            "targets": [url]
        }
        
        # Make request
        response = requests.post(
            endpoint,
            json=payload,
            auth=auth,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                
                return {
                    "success": True,
                    "domain_authority": result.get("domain_authority", 0),
                    "page_authority": result.get("page_authority", 0),
                    "spam_score": result.get("spam_score", 0),
                    "root_domains_to_root": result.get("root_domains_to_root", 0),
                    "external_links": result.get("external_links_to_root", 0),
                    "ranking_keywords": result.get("pages", 0),
                    "source": "Moz API v2",
                    "quality_rating": get_da_quality_rating(result.get("domain_authority", 0))
                }
        
        return {
            "success": False,
            "error": f"Moz API error: {response.status_code}",
            "response": response.text[:200]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_da_quality_rating(da_score: int) -> str:
    """Rate domain based on DA score"""
    
    if da_score >= 70:
        return "🟢 Excellent - Authoritative domain"
    elif da_score >= 50:
        return "🟡 Good - Established domain"
    elif da_score >= 30:
        return "🟠 Fair - Growing domain"
    elif da_score >= 10:
        return "🔴 Poor - New or low-quality domain"
    else:
        return "⚫ Very Poor - Minimal authority"

def analyze_backlinks_comprehensive(url: str, csv_data: str = None) -> Dict:
    """
    Enhanced backlink analysis (combines CSV + Moz)
    This replaces the existing analyze_backlinks function
    """
    
    print("Analyzing backlink profile...")
    
    # Get Moz metrics
    moz_data = get_moz_domain_authority(url)
    
    # If CSV provided, parse it
    if csv_data:
        csv_metrics = parse_backlink_csv(csv_data)
    else:
        csv_metrics = {
            "total_backlinks": 0,
            "referring_domains": 0,
            "dofollow_links": 0,
            "nofollow_links": 0
        }
    
    # Combine data
    result = {
        "success": True,
        "url": url,
        "domain_authority": moz_data.get("domain_authority", 0) if moz_data.get("success") else "N/A",
        "page_authority": moz_data.get("page_authority", 0) if moz_data.get("success") else "N/A",
        "spam_score": moz_data.get("spam_score", 0) if moz_data.get("success") else "N/A",
        "total_backlinks": csv_metrics.get("total_backlinks", 0) or moz_data.get("external_links", 0),
        "referring_domains": csv_metrics.get("referring_domains", 0) or moz_data.get("root_domains_to_root", 0),
        "dofollow_links": csv_metrics.get("dofollow_links", 0),
        "nofollow_links": csv_metrics.get("nofollow_links", 0),
        "quality_rating": moz_data.get("quality_rating", "Unknown"),
        "data_source": "Moz API" if moz_data.get("success") else "CSV Import" if csv_data else "Estimated"
    }
    
    # Calculate quality score
    if moz_data.get("success"):
        da = moz_data.get("domain_authority", 0)
        spam = moz_data.get("spam_score", 0)
        
        quality_score = max(0, min(100, da - spam))
        result["quality_score"] = quality_score
    else:
        result["quality_score"] = 50  # Default
    
    return result

def parse_backlink_csv(csv_data: str) -> Dict:
    """Parse CSV from Ahrefs/Semrush (existing function - keep as is)"""
    import csv
    from io import StringIO
    
    reader = csv.DictReader(StringIO(csv_data))
    
    total_backlinks = 0
    referring_domains = set()
    dofollow_count = 0
    
    for row in reader:
        total_backlinks += 1
        
        domain = row.get("Domain", row.get("Referring domain", ""))
        if domain:
            referring_domains.add(domain)
        
        if row.get("Dofollow", "").lower() == "yes":
            dofollow_count += 1
    
    return {
        "total_backlinks": total_backlinks,
        "referring_domains": len(referring_domains),
        "dofollow_links": dofollow_count,
        "nofollow_links": total_backlinks - dofollow_count
    }
