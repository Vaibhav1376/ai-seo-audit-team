"""
Enhanced Keyword Research with Real Search Volumes - Feature #3
"""
import os
import requests
import google.generativeai as genai
from typing import Dict, List
import base64

def get_real_search_volumes(keywords: List[str], location: str = "us") -> Dict:
    """
    Get real Google search volumes via DataForSEO API
    
    Args:
        keywords: List of keywords
        location: Location code (us, uk, in, etc.)
        
    Returns:
        Dict with keyword data
    """
    
    username = os.getenv("DATAFORSEO_LOGIN")
    password = os.getenv("DATAFORSEO_PASSWORD")
    
    if not username or not password:
        return {
            "success": False,
            "error": "DataForSEO credentials not configured",
            "note": "Add DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD to .env"
        }
    
    try:
        print(f"Fetching real search volumes for {len(keywords)} keywords...")
        
        # DataForSEO endpoint
        endpoint = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
        
        # Location codes
        location_codes = {
            "us": 2840,
            "uk": 2826,
            "in": 2356,
            "au": 2036,
            "ca": 2124
        }
        
        location_code = location_codes.get(location.lower(), 2840)
        
        # Prepare request
        post_data = [{
            "keywords": keywords[:1000],  # Max 1000 per request
            "location_code": location_code,
            "language_code": "en"
        }]
        
        # Authentication
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(endpoint, json=post_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data["status_code"] == 20000:
                results = data["tasks"][0]["result"]
                
                keyword_data = []
                for item in results:
                    keyword_data.append({
                        "keyword": item["keyword"],
                        "search_volume": item.get("search_volume", 0),
                        "competition": item.get("competition", 0),
                        "competition_level": item.get("competition_level", "unknown"),
                        "cpc": round(item.get("cpc", 0), 2),
                        "monthly_searches": item.get("monthly_searches", [])
                    })
                
                return {
                    "success": True,
                    "keywords": keyword_data,
                    "total": len(keyword_data),
                    "source": "DataForSEO",
                    "cost": len(keywords) * 0.00312  # Cost per keyword
                }
        
        return {
            "success": False,
            "error": f"DataForSEO API error: {response.status_code}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def research_keywords_enhanced(seed_keyword: str, location: str = "us", use_real_data: bool = True) -> Dict:
    """
    Enhanced keyword research (combines AI + real data)
    This replaces the existing research_keywords function
    """
    
    print(f"Researching keywords for: {seed_keyword}")
    
    # Step 1: Generate AI suggestions
    ai_keywords = generate_ai_keywords(seed_keyword)
    
    if not ai_keywords.get("success"):
        return ai_keywords
    
    keyword_list = [kw["keyword"] for kw in ai_keywords["keywords"]]
    
    # Step 2: Get real search volumes (if enabled)
    if use_real_data and os.getenv("DATAFORSEO_LOGIN"):
        real_data = get_real_search_volumes(keyword_list, location)
        
        if real_data.get("success"):
            # Merge AI insights with real data
            merged = []
            
            for real_kw in real_data["keywords"]:
                # Find matching AI keyword
                ai_match = next((k for k in ai_keywords["keywords"] if k["keyword"] == real_kw["keyword"]), None)
                
                if ai_match:
                    merged.append({
                        **real_kw,
                        "intent": ai_match.get("intent"),
                        "content_type": ai_match.get("content_type"),
                        "opportunity_score": calculate_opportunity_score(
                            real_kw["search_volume"],
                            real_kw["competition"]
                        )
                    })
            
            return {
                "success": True,
                "keywords": merged,
                "source": "AI + DataForSEO",
                "cost": real_data.get("cost", 0)
            }
    
    # Fallback: AI-only
    return ai_keywords

def calculate_opportunity_score(volume: int, competition: float) -> int:
    """Calculate keyword opportunity score (0-100)"""
    
    if volume == 0:
        return 0
    
    # Higher volume + lower competition = higher score
    volume_score = min(volume / 100, 50)  # Max 50 points
    competition_score = (1 - competition) * 50  # Max 50 points
    
    return int(volume_score + competition_score)

def generate_ai_keywords(seed_keyword: str) -> Dict:
    """Generate keyword ideas using AI (existing function - keep as is)"""
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name="gemini-2.5-flash-exp")
    
    prompt = f"""Generate 20 related keyword ideas for: "{seed_keyword}"

For each keyword provide:
- The keyword phrase
- Estimated monthly search volume (realistic numbers)
- Keyword difficulty (0-100)
- Search intent (informational/commercial/transactional)
- Content type suggestion (blog/landing page/tool)

Return as JSON array:
[
  {{
    "keyword": "best {seed_keyword}",
    "volume": 5000,
    "difficulty": 45,
    "intent": "commercial",
    "content_type": "comparison page",
    "opportunity_score": 75
  }}
]"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        
        import json
        keywords = json.loads(text)
        
        return {
            "success": True,
            "keywords": keywords[:20],
            "source": "AI Generated"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
