"""
Google PageSpeed Insights Integration
Gets Core Web Vitals and performance scores
"""
import requests
import os
from typing import Dict, Optional


def get_pagespeed_insights(url: str, strategy: str = 'mobile') -> Dict:
    """
    Get Google PageSpeed Insights data
    
    Args:
        url: URL to analyze
        strategy: 'mobile' or 'desktop'
        
    Returns:
        Dict with performance scores and metrics
    """
    print(f"  🚀 Checking PageSpeed for {url}...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return {
            "success": False,
            "error": "Google API key required for PageSpeed Insights"
        }
    
    try:
        endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        
        params = {
            'url': url,
            'key': api_key,
            'strategy': strategy,
            'category': ['performance', 'accessibility', 'best-practices', 'seo']
        }
        
        response = requests.get(endpoint, params=params, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        lighthouse = data.get('lighthouseResult', {})
        
        # Extract scores
        categories = lighthouse.get('categories', {})
        audits = lighthouse.get('audits', {})
        
        result = {
            "success": True,
            "url": url,
            "strategy": strategy,
            "scores": {
                "performance": int(categories.get('performance', {}).get('score', 0) * 100),
                "accessibility": int(categories.get('accessibility', {}).get('score', 0) * 100),
                "best_practices": int(categories.get('best-practices', {}).get('score', 0) * 100),
                "seo": int(categories.get('seo', {}).get('score', 0) * 100),
            },
            "core_web_vitals": {
                "lcp": audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                "fid": audits.get('max-potential-fid', {}).get('displayValue', 'N/A'),
                "cls": audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A'),
                "fcp": audits.get('first-contentful-paint', {}).get('displayValue', 'N/A'),
                "ttfb": audits.get('server-response-time', {}).get('displayValue', 'N/A'),
            },
            "opportunities": extract_opportunities(audits),
            "diagnostics": extract_diagnostics(audits),
        }
        
        print(f"  ✅ PageSpeed: {result['scores']['performance']}/100")
        return result
        
    except requests.exceptions.Timeout:
        return {"success": False, "error": "PageSpeed API timeout"}
    except Exception as e:
        return {"success": False, "error": f"PageSpeed error: {str(e)}"}


def extract_opportunities(audits: Dict) -> list:
    """Extract top optimization opportunities"""
    opportunities = []
    
    opportunity_audits = [
        'render-blocking-resources',
        'unused-css-rules',
        'unused-javascript',
        'modern-image-formats',
        'offscreen-images',
        'unminified-css',
        'unminified-javascript',
    ]
    
    for audit_key in opportunity_audits:
        audit = audits.get(audit_key, {})
        if audit.get('score', 1) < 0.9:  # If not passing
            opportunities.append({
                'title': audit.get('title', ''),
                'description': audit.get('description', ''),
                'savings': audit.get('displayValue', ''),
                'score': audit.get('score', 0)
            })
    
    return opportunities[:5]  # Top 5


def extract_diagnostics(audits: Dict) -> list:
    """Extract diagnostic information"""
    diagnostics = []
    
    diagnostic_audits = [
        'dom-size',
        'total-byte-weight',
        'uses-long-cache-ttl',
        'network-requests',
    ]
    
    for audit_key in diagnostic_audits:
        audit = audits.get(audit_key, {})
        if audit.get('displayValue'):
            diagnostics.append({
                'title': audit.get('title', ''),
                'value': audit.get('displayValue', ''),
                'description': audit.get('description', '')
            })
    
    return diagnostics


def analyze_speed_for_multiple_pages(urls: list) -> Dict:
    """
    Analyze speed for multiple pages
    Returns site-wide speed analysis
    """
    print(f"\n🚀 Analyzing page speed for {len(urls)} pages...")
    
    results = []
    total_performance = 0
    
    for url in urls[:10]:  # Limit to 10 pages (API quota)
        result = get_pagespeed_insights(url)
        if result.get('success'):
            results.append(result)
            total_performance += result['scores']['performance']
    
    if not results:
        return {"success": False, "error": "No successful speed tests"}
    
    avg_performance = int(total_performance / len(results))
    
    return {
        "success": True,
        "avg_performance_score": avg_performance,
        "pages_tested": len(results),
        "individual_results": results,
        "slowest_pages": sorted(results, key=lambda x: x['scores']['performance'])[:5],
        "fastest_pages": sorted(results, key=lambda x: x['scores']['performance'], reverse=True)[:5],
    }
