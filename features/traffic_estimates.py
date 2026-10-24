"""
Traffic Estimation
Estimate organic traffic based on rankings and search volume
"""
from serpapi.google_search import GoogleSearch
import os
from typing import Dict, List
import json

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# CTR (Click-Through Rate) by position - industry averages
CTR_BY_POSITION = {
    1: 0.316,   # 31.6%
    2: 0.157,   # 15.7%
    3: 0.105,   # 10.5%
    4: 0.074,   # 7.4%
    5: 0.055,   # 5.5%
    6: 0.043,   # 4.3%
    7: 0.034,   # 3.4%
    8: 0.028,   # 2.8%
    9: 0.024,   # 2.4%
    10: 0.021,  # 2.1%
    11: 0.015,  # 1.5%
    12: 0.013,
    13: 0.011,
    14: 0.010,
    15: 0.009,
    16: 0.008,
    17: 0.007,
    18: 0.007,
    19: 0.006,
    20: 0.006
}

def estimate_traffic(url: str, keywords: List[str]) -> Dict:
    """
    Estimate monthly organic traffic
    
    Args:
        url: URL to analyze
        keywords: List of keywords to check
        
    Returns:
        Dict with traffic estimates
    """
    print(f"📊 Estimating traffic for {url}...")
    
    if not SERPAPI_KEY:
        return {"success": False, "error": "SERPAPI_KEY not configured"}
    
    keyword_traffic = []
    total_estimated_traffic = 0
    
    for keyword in keywords[:20]:  # Limit to 20 keywords
        try:
            # Get search volume
            volume = _get_search_volume(keyword)
            
            if volume == 0:
                continue
            
            # Get ranking position
            position = _get_ranking_position(url, keyword)
            
            if position and position <= 20:
                # Calculate estimated clicks
                ctr = CTR_BY_POSITION.get(position, 0.005)
                estimated_clicks = int(volume * ctr)
                
                keyword_traffic.append({
                    "keyword": keyword,
                    "search_volume": volume,
                    "position": position,
                    "ctr": round(ctr * 100, 1),
                    "estimated_monthly_clicks": estimated_clicks
                })
                
                total_estimated_traffic += estimated_clicks
                
                print(f"   ✅ {keyword}: Pos #{position}, Est. {estimated_clicks} clicks/month")
        
        except Exception as e:
            print(f"   ⚠️ Error for '{keyword}': {e}")
    
    # Sort by traffic potential
    keyword_traffic.sort(key=lambda x: x["estimated_monthly_clicks"], reverse=True)
    
    # Calculate traffic value (assuming $2 CPC average)
    traffic_value = total_estimated_traffic * 2
    
    print(f"   📊 Total Estimated Monthly Traffic: {total_estimated_traffic:,} visits")
    print(f"   💰 Estimated Monthly Value: ${traffic_value:,}")
    
    return {
        "success": True,
        "url": url,
        "total_keywords_analyzed": len(keywords),
        "ranking_keywords": len(keyword_traffic),
        "estimated_monthly_traffic": total_estimated_traffic,
        "estimated_monthly_value": traffic_value,
        "keyword_breakdown": keyword_traffic,
        "top_traffic_keywords": keyword_traffic[:10]
    }


def compare_traffic(my_url: str, competitor_url: str, keywords: List[str]) -> Dict:
    """
    Compare traffic estimates between two sites
    
    Args:
        my_url: Your URL
        competitor_url: Competitor URL
        keywords: Keywords to analyze
        
    Returns:
        Dict with traffic comparison
    """
    print(f"⚖️ Comparing traffic estimates...")
    
    my_traffic = estimate_traffic(my_url, keywords)
    comp_traffic = estimate_traffic(competitor_url, keywords)
    
    if not my_traffic.get("success") or not comp_traffic.get("success"):
        return {
            "success": False,
            "error": "Failed to estimate traffic for one or both URLs"
        }
    
    my_total = my_traffic["estimated_monthly_traffic"]
    comp_total = comp_traffic["estimated_monthly_traffic"]
    
    difference = my_total - comp_total
    percentage_diff = (difference / comp_total * 100) if comp_total > 0 else 0
    
    return {
        "success": True,
        "my_url": my_url,
        "competitor_url": competitor_url,
        "comparison": {
            "my_traffic": my_total,
            "competitor_traffic": comp_total,
            "difference": difference,
            "percentage_difference": round(percentage_diff, 1),
            "winner": "you" if difference > 0 else "competitor" if difference < 0 else "tie"
        },
        "my_details": my_traffic,
        "competitor_details": comp_traffic
    }


def find_traffic_opportunities(url: str, keywords: List[str]) -> Dict:
    """
    Find keywords with high traffic potential where you could improve
    
    Args:
        url: Your URL
        keywords: Keywords to analyze
        
    Returns:
        Dict with opportunity analysis
    """
    print(f"🎯 Finding traffic opportunities...")
    
    opportunities = []
    
    for keyword in keywords[:20]:
        try:
            volume = _get_search_volume(keyword)
            position = _get_ranking_position(url, keyword)
            
            if not position:
                # Not ranking - check if high volume
                if volume >= 1000:
                    opportunities.append({
                        "keyword": keyword,
                        "search_volume": volume,
                        "current_position": None,
                        "opportunity_type": "not_ranking",
                        "potential_traffic": int(volume * 0.05),  # Assume we could get position 5
                        "difficulty": "high",
                        "priority": "high" if volume >= 5000 else "medium"
                    })
            elif position > 10:
                # Ranking poorly - could improve
                current_ctr = CTR_BY_POSITION.get(position, 0.005)
                target_ctr = CTR_BY_POSITION.get(5, 0.055)  # Target position 5
                
                current_traffic = int(volume * current_ctr)
                potential_traffic = int(volume * target_ctr)
                traffic_gain = potential_traffic - current_traffic
                
                if traffic_gain >= 50:  # Worth pursuing
                    opportunities.append({
                        "keyword": keyword,
                        "search_volume": volume,
                        "current_position": position,
                        "current_traffic": current_traffic,
                        "potential_traffic": potential_traffic,
                        "traffic_gain": traffic_gain,
                        "opportunity_type": "improve_ranking",
                        "difficulty": "medium",
                        "priority": "high" if traffic_gain >= 500 else "medium"
                    })
            elif position <= 10:
                # Top 10 - could move to #1
                current_ctr = CTR_BY_POSITION.get(position, 0.02)
                target_ctr = CTR_BY_POSITION.get(1, 0.316)
                
                current_traffic = int(volume * current_ctr)
                potential_traffic = int(volume * target_ctr)
                traffic_gain = potential_traffic - current_traffic
                
                if traffic_gain >= 100:
                    opportunities.append({
                        "keyword": keyword,
                        "search_volume": volume,
                        "current_position": position,
                        "current_traffic": current_traffic,
                        "potential_traffic": potential_traffic,
                        "traffic_gain": traffic_gain,
                        "opportunity_type": "reach_position_1",
                        "difficulty": "low",
                        "priority": "high"
                    })
        
        except Exception as e:
            print(f"   ⚠️ Error analyzing '{keyword}': {e}")
    
    # Sort by traffic gain potential
    opportunities.sort(key=lambda x: x.get("traffic_gain", x.get("potential_traffic", 0)), reverse=True)
    
    total_opportunity = sum(o.get("traffic_gain", o.get("potential_traffic", 0)) for o in opportunities)
    
    print(f"   ✅ Found {len(opportunities)} opportunities")
    print(f"   📈 Total Potential Traffic Gain: {total_opportunity:,} visits/month")
    
    return {
        "success": True,
        "url": url,
        "total_opportunities": len(opportunities),
        "total_potential_gain": total_opportunity,
        "high_priority": [o for o in opportunities if o["priority"] == "high"],
        "medium_priority": [o for o in opportunities if o["priority"] == "medium"],
        "all_opportunities": opportunities
    }


def _get_search_volume(keyword: str) -> int:
    """Get estimated search volume for a keyword"""
    try:
        params = {
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "q": keyword
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Estimate from total results (rough estimate)
        total_results = results.get("search_information", {}).get("total_results", 0)
        
        # Very rough estimation formula
        if total_results > 1000000000:
            volume = 100000
        elif total_results > 100000000:
            volume = 50000
        elif total_results > 10000000:
            volume = 10000
        elif total_results > 1000000:
            volume = 5000
        elif total_results > 100000:
            volume = 1000
        else:
            volume = 500
        
        return volume
        
    except:
        return 0


def _get_ranking_position(url: str, keyword: str) -> int:
    """Get current ranking position for keyword"""
    try:
        params = {
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "q": keyword,
            "num": 100
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        clean_url = url.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
        
        for i, result in enumerate(results.get("organic_results", []), start=1):
            result_link = result.get("link", "")
            if clean_url in result_link:
                return i
        
        return None
        
    except:
        return None
