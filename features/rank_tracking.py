"""
Daily Rank Tracking
Monitor keyword positions over time
"""
from serpapi.google_search import GoogleSearch
import os
from typing import Dict, List
from utils.database import save_rank_check, get_rank_history, add_tracked_keyword, get_tracked_keywords
from datetime import datetime

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def check_keyword_rank(url: str, keyword: str, location: str = "United States", device: str = "desktop") -> Dict:
    """
    Check current ranking position for a keyword with Debugging enabled
    """
    print(f"🔍 Checking rank for '{keyword}' ({device})...")
    
    if not SERPAPI_KEY:
        return {"success": False, "error": "SERPAPI_KEY not configured"}
    
    try:
        params = {
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "q": keyword,
            "location": location,
            "gl": "us",
            "hl": "en",
            "num": 100  # Check first 100 results
        }
        
        if device == "mobile":
            params["device"] = "mobile"
        
        search = GoogleSearch(params)
        results = search.get_dict()

        # --- DEBUG: CHECK FOR API ERRORS ---
        if "error" in results:
            print(f"❌ API Error: {results['error']}")
            return {"success": False, "error": results['error']}
        
        organic_results = results.get("organic_results", [])

        # --- DEBUG: IF NO RESULTS ---
        if not organic_results:
            print(f"⚠️ Warning: API returned 0 organic results for '{keyword}'.")
            # This helps debug if we are getting Knowledge Graphs instead of results
            print(f"   Available Keys in Response: {list(results.keys())}")
        
        # Find position
        position = None
        
        # Robust URL Cleaning (Lower case, remove protocol, remove www)
        # Example: "https://www.Tesla.com/" -> "tesla.com"
        clean_target = url.lower().replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
        
        for i, result in enumerate(organic_results, start=1):
            raw_link = result.get("link", "")
            
            # Clean Result URL
            clean_result = raw_link.lower().replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
            
            # --- DEBUG: PRINT TOP 3 RESULTS ---
            # This lets you see in the terminal what Google is actually returning
            if i <= 3:
                print(f"   #{i}: {raw_link} (Cleaned: {clean_result})")
            
            # Check Match (Exact or Sub-path)
            # 1. Exact match: tesla.com == tesla.com
            # 2. Sub-path match: tesla.com/models startswith tesla.com
            if clean_target == clean_result or clean_result.startswith(clean_target + "/"):
                position = i
                print(f"   ✅ MATCH FOUND at #{position}")
                break
        
        # Save to database
        if position:
            save_rank_check(url, keyword, position, location, device)
        else:
            print(f"   📭 Not found in top 100")
        
        return {
            "success": True,
            "url": url,
            "keyword": keyword,
            "position": position,
            "location": location,
            "device": device,
            "checked_at": datetime.now().isoformat(),
            "in_top_10": position is not None and position <= 10,
            "in_top_100": position is not None
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def check_multiple_keywords(url: str, keywords: List[str], device: str = "desktop") -> Dict:
    """
    Check rankings for multiple keywords
    """
    print(f"📊 Checking {len(keywords)} keywords...")
    
    results = []
    for keyword in keywords:
        result = check_keyword_rank(url, keyword, device=device)
        results.append(result)
    
    # Calculate statistics
    successful_checks = [r for r in results if r.get("success")]
    ranked_keywords = [r for r in successful_checks if r.get("position") is not None]
    
    top_10_count = len([r for r in ranked_keywords if r["position"] <= 10])
    top_50_count = len([r for r in ranked_keywords if r["position"] <= 50])
    
    # Safe Average Calculation
    if ranked_keywords:
        avg_position = sum(r["position"] for r in ranked_keywords) / len(ranked_keywords)
    else:
        avg_position = None # This triggers the need for the fix in web_app.py
    
    return {
        "success": True,
        "url": url,
        "total_keywords": len(keywords),
        "ranked_keywords": len(ranked_keywords),
        "not_ranked": len(successful_checks) - len(ranked_keywords),
        "top_10_count": top_10_count,
        "top_50_count": top_50_count,
        "average_position": round(avg_position, 1) if avg_position else None,
        "results": results
    }


def get_rank_change_report(url: str, keyword: str, days: int = 7) -> Dict:
    """
    Get rank change over time
    """
    print(f"📈 Analyzing rank changes for '{keyword}'...")
    
    history = get_rank_history(url, keyword, days=days)
    
    if len(history) < 2:
        return {
            "success": False,
            "error": "Insufficient historical data (need at least 2 data points)"
        }
    
    first_position = history[0]["position"]
    last_position = history[-1]["position"]
    
    change = first_position - last_position  # Positive = improvement
    
    # Best and worst positions
    positions = [h["position"] for h in history]
    best_position = min(positions)
    worst_position = max(positions)
    
    # Trend analysis
    if change > 5:
        trend = "Strong Improvement ⬆️"
    elif change > 0:
        trend = "Slight Improvement ↗️"
    elif change == 0:
        trend = "Stable →"
    elif change > -5:
        trend = "Slight Decline ↘️"
    else:
        trend = "Strong Decline ⬇️"
    
    return {
        "success": True,
        "url": url,
        "keyword": keyword,
        "period_days": days,
        "starting_position": first_position,
        "current_position": last_position,
        "change": change,
        "best_position": best_position,
        "worst_position": worst_position,
        "trend": trend,
        "history": history
    }


def track_keyword_daily(url: str, keyword: str, priority: str = "high"):
    """
    Add keyword to daily tracking
    """
    add_tracked_keyword(url, keyword, priority=priority)
    
    # Run initial check
    return check_keyword_rank(url, keyword)