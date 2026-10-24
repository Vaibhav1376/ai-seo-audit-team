import os
import json
from serpapi.google_search import GoogleSearch
import google.generativeai as genai
from typing import Dict
from config import AGENT_CONFIG  # Assuming AGENT_CONFIG based on previous snippets

def serpanalyst(keyword: str, model: str = None) -> Dict:
    """Agent 2: SERP Analyst
    
    Args:
        keyword: Keyword to analyze
        model: Gemini model to use
        
    Returns:
        Dict with SERP analysis
    """

    print("\n" + "="*70)
    print("🤖 AGENT 2: SERP Analyst")
    print("="*70)
    print(f"📱 Keyword: {keyword}")
    
    # Fetch real SERP data
    serpdata = fetch_serpapi_data(keyword)
    
    # Analyze with AI
    analysis = analyze_serp_with_ai(keyword, serpdata, model)
    
    print("✅ Agent 2 Complete!")
    return {
        "keyword": keyword,
        "serpdata": serpdata,
        "analysis": analysis,
        "success": True
    }

def fetch_serpapi_data(keyword: str) -> Dict:
    """Fetch real SERP data from SerpAPI"""
    api_key = os.getenv("SERPAPI_KEY")
    
    if not api_key:
        print("⚠️  No SerpAPI key found in environment - using placeholder data")
        return {
            "top10_results": [],
            "has_featured_snippet": False,
            "people_also_ask": [],
            "related_searches": []
        }
    
    try:
        print("🔍 Fetching SERP data from Google via SerpAPI...")
        params = {
            "q": keyword,
            "api_key": api_key,
            "num": 10,
            "hl": "en",
            "gl": "us"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Extract top 10 organic results
        top10 = []
        for result in results.get("organic_results", [])[:10]:
            top10.append({
                "position": result.get("position", 0),
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "domain": result.get("displayed_link", "")
            })
        
        # Extract People Also Ask (PAA)
        paa = [q.get("question", "") for q in results.get("related_questions", [])[:5]]
        
        # Extract related searches
        related = [r.get("query", "") for r in results.get("related_searches", [])[:8]]
        
        # Check for featured snippet (answer box)
        featured = results.get("answer_box") is not None
        
        print(f"✅ Found {len(top10)} organic results and {len(paa)} PAA questions")
        
        return {
            "top10_results": top10,
            "has_featured_snippet": featured,
            "people_also_ask": paa,
            "related_searches": related
        }
        
    except Exception as e:
        print(f"❌ SerpAPI error: {e}")
        return {
            "top10_results": [],
            "has_featured_snippet": False,
            "people_also_ask": [],
            "related_searches": []
        }



def analyze_serp_with_ai(keyword: str, serpdata: Dict, model: str = None) -> Dict:
    """Analyze SERP data with AI to determine intent and strategy"""
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Use selected model or fallback to config
    model_name = model or os.getenv("SELECTED_MODEL", AGENT_CONFIG.get("model", "gemini-2.0-flash-exp"))
    gemini_model = genai.GenerativeModel(model_name=model_name)
    
    top10 = serpdata.get("top10_results", [])
    paa = serpdata.get("people_also_ask", [])
    
    prompt = f"""Analyze this SERP (Search Engine Results Page) data for keyword: "{keyword}"

TOP 5 COMPETITORS:
{json.dumps(top10[:5], indent=2)}

PEOPLE ALSO ASK QUESTIONS:
{json.dumps(paa, indent=2)}

Provide a strategic analysis as a valid JSON object:
{{
  "search_intent": "informational/commercial/transactional/navigational",
  "difficulty": 0-100,
  "dominant_content_type": "blog/landing page/tool/directory/forum",
  "avg_title_length": 60,
  "common_title_words": ["word1", "word2"],
  "content_recommendations": ["recommendation1", "recommendation2", "recommendation3"],
  "featured_snippet_opportunity": true/false
}}"""
    
    try:
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()
        
        # Repairing JSON extraction logic
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0].strip()
        else:
            json_str = text
        
        analysis = json.loads(json_str)
        return analysis
        
    except Exception as e:
        print(f"⚠️ AI analysis error: {e}")
        # Return fallback analysis data
        return {
            "search_intent": "informational",
            "difficulty": 50,
            "dominant_content_type": "blog",
            "avg_title_length": 60,
            "common_title_words": [],
            "content_recommendations": ["Focus on comprehensive content coverage"],
            "featured_snippet_opportunity": False
        }
