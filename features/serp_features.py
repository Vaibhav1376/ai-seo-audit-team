"""
SERP Features Tracking
Monitor Featured Snippets, People Also Ask, Knowledge Panels, etc.
"""
from serpapi.google_search import GoogleSearch
import os
from typing import Dict, List
from datetime import datetime

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def analyze_serp_features(keyword: str, location: str = "United States") -> Dict:
    """
    Identify all SERP features present for a keyword
    
    Args:
        keyword: Keyword to analyze
        location: Geographic location
        
    Returns:
        Dict with all SERP features found
    """
    print(f"🎯 Analyzing SERP features for '{keyword}'...")
    
    if not SERPAPI_KEY:
        return {"success": False, "error": "SERPAPI_KEY not configured"}
    
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
        results = search.get_dict()
        
        features = {
            "featured_snippet": False,
            "people_also_ask": False,
            "knowledge_panel": False,
            "local_pack": False,
            "image_pack": False,
            "video_results": False,
            "top_stories": False,
            "related_searches": False,
            "shopping_results": False,
            "twitter_results": False
        }
        
        feature_details = {}
        
        # Featured Snippet
        if "answer_box" in results:
            features["featured_snippet"] = True
            answer_box = results["answer_box"]
            feature_details["featured_snippet"] = {
                "type": answer_box.get("type", ""),
                "snippet": answer_box.get("snippet", ""),
                "title": answer_box.get("title", ""),
                "link": answer_box.get("link", "")
            }
            print("   ✅ Featured Snippet detected")
        
        # People Also Ask
        if "related_questions" in results:
            features["people_also_ask"] = True
            questions = results["related_questions"]
            feature_details["people_also_ask"] = {
                "count": len(questions),
                "questions": [q.get("question", "") for q in questions[:5]]
            }
            print(f"   ✅ People Also Ask detected ({len(questions)} questions)")
        
        # Knowledge Panel
        if "knowledge_graph" in results:
            features["knowledge_panel"] = True
            kg = results["knowledge_graph"]
            feature_details["knowledge_panel"] = {
                "title": kg.get("title", ""),
                "type": kg.get("type", ""),
                "description": kg.get("description", "")
            }
            print("   ✅ Knowledge Panel detected")
        
        # Local Pack
        if "local_results" in results:
            features["local_pack"] = True
            local = results["local_results"]
            feature_details["local_pack"] = {
                "count": len(local.get("places", [])),
                "places": [p.get("title", "") for p in local.get("places", [])[:3]]
            }
            print("   ✅ Local Pack detected")
        
        # Image Pack
        if "inline_images" in results:
            features["image_pack"] = True
            feature_details["image_pack"] = {
                "count": len(results["inline_images"])
            }
            print("   ✅ Image Pack detected")
        
        # Video Results
        if "inline_videos" in results:
            features["video_results"] = True
            videos = results["inline_videos"]
            feature_details["video_results"] = {
                "count": len(videos),
                "sources": list(set([v.get("source", "") for v in videos]))
            }
            print("   ✅ Video Results detected")
        
        # Top Stories
        if "top_stories" in results:
            features["top_stories"] = True
            stories = results["top_stories"]
            feature_details["top_stories"] = {
                "count": len(stories)
            }
            print("   ✅ Top Stories detected")
        
        # Related Searches
        if "related_searches" in results:
            features["related_searches"] = True
            related = results["related_searches"]
            feature_details["related_searches"] = {
                "count": len(related),
                "searches": [r.get("query", "") for r in related[:5]]
            }
        
        # Shopping Results
        if "shopping_results" in results:
            features["shopping_results"] = True
            feature_details["shopping_results"] = {
                "count": len(results["shopping_results"])
            }
        
        # Calculate total features
        total_features = sum(features.values())
        
        print(f"   📊 Total SERP features: {total_features}")
        
        return {
            "success": True,
            "keyword": keyword,
            "total_features": total_features,
            "features": features,
            "feature_details": feature_details,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def find_featured_snippet_opportunity(keyword: str, your_url: str = None) -> Dict:
    """
    Check if there's a featured snippet and if you can capture it
    
    Args:
        keyword: Keyword to check
        your_url: Your URL (to check if you already have it)
        
    Returns:
        Dict with opportunity analysis
    """
    print(f"🎯 Checking featured snippet opportunity for '{keyword}'...")
    
    analysis = analyze_serp_features(keyword)
    
    if not analysis.get("success"):
        return analysis
    
    has_snippet = analysis["features"]["featured_snippet"]
    
    if not has_snippet:
        return {
            "success": True,
            "has_snippet": False,
            "opportunity": "No featured snippet currently - opportunity to be first!",
            "recommendation": "Create comprehensive content answering this query directly"
        }
    
    snippet_details = analysis["feature_details"].get("featured_snippet", {})
    snippet_url = snippet_details.get("link", "")
    
    # Check if you own it
    if your_url and your_url in snippet_url:
        return {
            "success": True,
            "has_snippet": True,
            "you_own_it": True,
            "snippet_type": snippet_details.get("type", ""),
            "recommendation": "Maintain current content quality and structure"
        }
    else:
        return {
            "success": True,
            "has_snippet": True,
            "you_own_it": False,
            "current_owner": snippet_url,
            "snippet_type": snippet_details.get("type", ""),
            "snippet_text": snippet_details.get("snippet", "")[:200],
            "opportunity": "High - Featured snippet exists but owned by competitor",
            "recommendation": f"Optimize for {snippet_details.get('type', 'paragraph')} format and answer the query more comprehensively"
        }


def track_serp_changes(keyword: str, days: int = 30) -> Dict:
    """
    Track SERP feature changes over time
    
    Args:
        keyword: Keyword to track
        days: Number of days of history
        
    Returns:
        Dict with change analysis
    """
    # This would query historical data from database
    # For now, just return current state
    return analyze_serp_features(keyword)
