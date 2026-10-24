"""
Local SEO Rank Tracking
Track rankings in specific cities/regions with robust matching logic.
"""
from serpapi.google_search import GoogleSearch
import os
from typing import Dict, List

# Popular US cities for local tracking
US_CITIES = {
    "New York": "New York,New York,United States",
    "Los Angeles": "Los Angeles,California,United States",
    "Chicago": "Chicago,Illinois,United States",
    "Houston": "Houston,Texas,United States",
    "Phoenix": "Phoenix,Arizona,United States",
    "Philadelphia": "Philadelphia,Pennsylvania,United States",
    "San Antonio": "San Antonio,Texas,United States",
    "San Diego": "San Diego,California,United States",
    "Dallas": "Dallas,Texas,United States",
    "San Jose": "San Jose,California,United States"
}

def clean_url_for_matching(url: str) -> str:
    """Helper to clean URLs for comparison (removes protocol, www, trailing slashes)"""
    if not url: return ""
    return url.lower().replace("https://", "").replace("http://", "").replace("www.", "").strip("/")

def check_local_rank(url: str, keyword: str, city: str = "New York") -> Dict:
    """
    Check ranking for a keyword in specific city
    """
    print(f"📍 Checking local rank in {city} for '{keyword}'...")
    
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return {"success": False, "error": "SERPAPI_KEY not configured"}
    
    location = US_CITIES.get(city, US_CITIES["New York"])
    
    try:
        params = {
            "api_key": api_key,
            "engine": "google",
            "q": keyword,
            "location": location,
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "num": 100 
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # --- 1. Check Organic Results ---
        position = None
        organic_results = results.get("organic_results", [])
        clean_target = clean_url_for_matching(url)
        
        for i, result in enumerate(organic_results, start=1):
            link = result.get("link", "")
            clean_link = clean_url_for_matching(link)
            
            # Robust Match: Exact or Sub-path (e.g., tesla.com/model3 matches tesla.com)
            if clean_target == clean_link or clean_link.startswith(clean_target + "/"):
                position = i
                print(f"   ✅ Found Organic Rank #{i} in {city}")
                break
        
        # --- 2. Check Local Pack (Map Results) ---
        in_local_pack = False
        local_results = results.get("local_results", {})
        places = local_results.get("places", [])
        
        for place in places:
            # Check website link
            place_link = place.get("links", {}).get("website", "")
            clean_place_link = clean_url_for_matching(place_link)
            
            # Check title (sometimes they don't have a website link)
            title = place.get("title", "").lower()
            
            if clean_target in clean_place_link or keyword.lower() in title:
                in_local_pack = True
                print(f"   🎯 Found in Local Map Pack in {city}!")
                break
        
        if not position and not in_local_pack:
            print(f"   📭 Not found in top 100 for {city}")

        return {
            "success": True,
            "url": url,
            "keyword": keyword,
            "city": city,
            "position": position,
            "in_local_pack": in_local_pack,
            "local_pack_visible": len(places) > 0
        }
        
    except Exception as e:
        print(f"   ❌ Error in {city}: {e}")
        return {"success": False, "error": str(e)}


def check_multi_city_rank(url: str, keyword: str, cities: List[str] = None) -> Dict:
    """
    Check ranking across multiple cities
    """
    if cities is None:
        cities = list(US_CITIES.keys())[:5]  # Default to Top 5
    
    print(f"🗺️ Checking '{keyword}' across {len(cities)} cities...")
    
    results = []
    for city in cities:
        result = check_local_rank(url, keyword, city)
        results.append({
            "city": city,
            "success": result.get("success", False),
            "position": result.get("position"),
            "in_local_pack": result.get("in_local_pack", False),
            "local_pack_visible": result.get("local_pack_visible", False)
        })
    
    # Analysis
    ranked_cities = [r for r in results if r.get("position") is not None]
    local_pack_cities = [r for r in results if r.get("in_local_pack")]
    
    if ranked_cities:
        best_city = min(ranked_cities, key=lambda x: x["position"])
        worst_city = max(ranked_cities, key=lambda x: x["position"])
    else:
        best_city = None
        worst_city = None
    
    return {
        "success": True,
        "url": url,
        "keyword": keyword,
        "cities_checked": len(cities),
        "ranked_in": len(ranked_cities),
        "in_local_pack": len(local_pack_cities),
        "best_city": best_city["city"] if best_city else None,
        "best_position": best_city["position"] if best_city else None,
        "worst_city": worst_city["city"] if worst_city else None,
        "worst_position": worst_city["position"] if worst_city else None,
        "results": results
    }


def get_local_competitors(keyword: str, city: str = "New York", count: int = 10) -> Dict:
    """
    Find who ranks locally for a keyword
    """
    print(f"👥 Finding local competitors for '{keyword}' in {city}...")
    
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return {"success": False, "error": "SERPAPI_KEY not configured"}
    
    location = US_CITIES.get(city, US_CITIES["New York"])
    
    try:
        params = {
            "api_key": api_key,
            "engine": "google",
            "q": keyword,
            "location": location,
            "gl": "us",
            "hl": "en"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        competitors = []
        
        # 1. Get from Local Pack
        local_results = results.get("local_results", {})
        for place in local_results.get("places", [])[:5]:
            competitors.append({
                "name": place.get("title", ""),
                "url": place.get("links", {}).get("website", ""), # Better path to URL
                "position": "Local Pack",
                "rating": place.get("rating"),
                "reviews": place.get("reviews"),
                "type": "local"
            })
        
        # 2. Get from Organic Results
        for i, result in enumerate(results.get("organic_results", [])[:count], start=1):
            competitors.append({
                "name": result.get("title", ""),
                "url": result.get("link", ""),
                "position": i,
                "snippet": result.get("snippet", ""),
                "type": "organic"
            })
        
        return {
            "success": True,
            "keyword": keyword,
            "city": city,
            "total_competitors": len(competitors),
            "local_pack_count": len([c for c in competitors if c["type"] == "local"]),
            "competitors": competitors
        }
        
    except Exception as e:
        print(f"❌ Error finding competitors: {e}")
        return {"success": False, "error": str(e)}