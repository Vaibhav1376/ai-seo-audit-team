"""
Search Volume & Keyword Research
Uses SERPApi to get real search volume data
"""
import os
from serpapi.google_search import GoogleSearch
from typing import List, Dict

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def get_search_volume(keywords: List[str], location: str = "United States") -> Dict:
    """
    Get search volume for keywords
    
    Args:
        keywords: List of keywords to check
        location: Geographic location
        
    Returns:
        Dict with search volumes
    """
    print(f"🔍 Fetching search volume for {len(keywords)} keywords...")
    
    if not SERPAPI_KEY:
        return {
            "success": False,
            "error": "SERPAPI_KEY not configured"
        }
    
    results = []
    
    for keyword in keywords[:10]:  # Limit to 10 to save API credits
        try:
            params = {
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "q": keyword,
                "location": location,
                "gl": "us",
                "hl": "en"
            }
            
            search = GoogleSearch(params)
            data = search.get_dict()
            
            # Extract search results count (approximate volume)
            search_info = data.get("search_information", {})
            total_results = search_info.get("total_results", 0)
            
            # Get related searches for keyword ideas
            related = data.get("related_searches", [])
            related_keywords = [r.get("query", "") for r in related[:5]]
            
            results.append({
                "keyword": keyword,
                "estimated_results": total_results,
                "difficulty": _calculate_difficulty(total_results),
                "related_keywords": related_keywords,
                "success": True
            })
            
            print(f"   ✅ {keyword}: {total_results:,} results")
            
        except Exception as e:
            print(f"   ❌ Failed for '{keyword}': {e}")
            results.append({
                "keyword": keyword,
                "error": str(e),
                "success": False
            })
    
    return {
        "success": True,
        "keywords": results,
        "total_checked": len(results)
    }


def get_keyword_suggestions(seed_keyword: str, count: int = 20) -> Dict:
    """
    Get keyword suggestions based on a seed keyword
    
    Args:
        seed_keyword: Main keyword to expand
        count: Number of suggestions to return
        
    Returns:
        Dict with keyword suggestions
    """
    print(f"💡 Getting keyword suggestions for '{seed_keyword}'...")
    
    if not SERPAPI_KEY:
        return {"success": False, "error": "SERPAPI_KEY not configured"}
    
    try:
        params = {
            "api_key": SERPAPI_KEY,
            "engine": "google_autocomplete",
            "q": seed_keyword
        }
        
        search = GoogleSearch(params)
        data = search.get_dict()
        
        suggestions = data.get("suggestions", [])
        keyword_list = [s.get("value", "") for s in suggestions[:count]]
        
        print(f"   ✅ Found {len(keyword_list)} suggestions")
        
        return {
            "success": True,
            "seed_keyword": seed_keyword,
            "suggestions": keyword_list,
            "count": len(keyword_list)
        }
        
    except Exception as e:
        print(f"   ❌ Keyword suggestions failed: {e}")
        return {"success": False, "error": str(e)}


def _calculate_difficulty(total_results: int) -> str:
    """
    Estimate keyword difficulty based on result count
    
    Args:
        total_results: Number of search results
        
    Returns:
        Difficulty level string
    """
    if total_results < 100000:
        return "Easy"
    elif total_results < 1000000:
        return "Medium"
    elif total_results < 10000000:
        return "Hard"
    else:
        return "Very Hard"
