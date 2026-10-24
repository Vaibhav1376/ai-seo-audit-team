"""
Competitor Keyword Analysis
Find keywords competitors rank for that you don't
"""
import google.generativeai as genai
import os
from typing import List, Dict
from utils.scraper import scrape_url

def analyze_competitor_keywords(my_url: str, competitor_url: str, model: str = "gemini-1.5-flash") -> Dict:
    """
    Deep keyword analysis comparing two sites
    
    Args:
        my_url: Your website URL
        competitor_url: Competitor URL
        model: Gemini model to use
        
    Returns:
        Dict with keyword gap analysis
    """
    print(f"🎯 Analyzing keyword gap between sites...")
    
    # Scrape both sites
    print("   📄 Scraping your site...")
    my_data = scrape_url(my_url)
    
    print("   📄 Scraping competitor...")
    comp_data = scrape_url(competitor_url)
    
    if not my_data.get('success') or not comp_data.get('success'):
        return {
            "success": False,
            "error": "Failed to scrape one or both URLs"
        }
    
    # Use AI to extract and compare keywords
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini = genai.GenerativeModel(model_name=model)
    
    prompt = f"""Perform detailed keyword analysis comparing these two pages.

# YOUR PAGE:
URL: {my_url}
Title: {my_data.get('title', 'N/A')}
Content Sample: {my_data.get('text', '')[:2000]}

# COMPETITOR PAGE:
URL: {competitor_url}
Title: {comp_data.get('title', 'N/A')}
Content Sample: {comp_data.get('text', '')[:2000]}

Analyze and return JSON:
{{
    "your_keywords": [
        {{"keyword": "keyword1", "frequency": 5, "relevance": 9}},
        {{"keyword": "keyword2", "frequency": 3, "relevance": 7}}
    ],
    "competitor_keywords": [
        {{"keyword": "keyword1", "frequency": 8, "relevance": 10}},
        {{"keyword": "keyword3", "frequency": 6, "relevance": 8}}
    ],
    "keyword_gap": [
        {{"keyword": "missing_keyword1", "opportunity_score": 9, "reason": "Why you should target this"}},
        {{"keyword": "missing_keyword2", "opportunity_score": 7, "reason": "Another opportunity"}}
    ],
    "shared_keywords": [
        {{"keyword": "shared1", "your_usage": 3, "their_usage": 8, "advantage": "competitor"}}
    ],
    "recommendations": [
        "Specific action 1",
        "Specific action 2",
        "Specific action 3"
    ]
}}

Focus on:
1. Commercial intent keywords (buying signals)
2. Long-tail opportunities
3. Semantic variations
"""
    
    try:
        response = gemini.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean JSON
        if "```json" in response_text:
            json_str = response_text.split("```json").split("```").strip()[1]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text
        
        import json
        result = json.loads(json_str)
        
        result["success"] = True
        result["my_url"] = my_url
        result["competitor_url"] = competitor_url
        
        print(f"   ✅ Found {len(result.get('keyword_gap', []))} keyword opportunities")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Keyword analysis failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_keyword_recommendations(url: str, niche: str = "general", model: str = "gemini-1.5-flash") -> Dict:
    """
    Get AI-powered keyword recommendations for a page
    
    Args:
        url: Page to analyze
        niche: Business niche
        model: Gemini model
        
    Returns:
        Dict with keyword recommendations
    """
    print(f"💡 Getting keyword recommendations for {url}...")
    
    data = scrape_url(url)
    
    if not data.get('success'):
        return {"success": False, "error": "Failed to scrape URL"}
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini = genai.GenerativeModel(model_name=model)
    
    prompt = f"""You are an expert SEO keyword strategist. Analyze this {niche} page and recommend keywords.

URL: {url}
Title: {data.get('title', 'N/A')}
Content: {data.get('text', '')[:2500]}

Provide keyword recommendations in JSON:
{{
    "primary_keywords": [
        {{"keyword": "main keyword", "priority": "high", "difficulty": "medium", "reason": "why target this"}},
        {{"keyword": "keyword 2", "priority": "high", "difficulty": "low", "reason": "explanation"}}
    ],
    "secondary_keywords": [
        {{"keyword": "supporting keyword", "priority": "medium", "difficulty": "low"}}
    ],
    "long_tail_opportunities": [
        {{"keyword": "specific long tail phrase", "search_intent": "informational", "conversion_potential": "high"}}
    ],
    "semantic_variations": [
        "variation 1",
        "variation 2"
    ],
    "content_gaps": [
        "Topic you should add to target more keywords"
    ]
}}
"""
    
    try:
        response = gemini.generate_content(prompt)
        response_text = response.text.strip()
        
        if "```json" in response_text:
            json_str = response_text.split("```json").split("```").strip()[1]
        else:
            json_str = response_text
        
        import json
        result = json.loads(json_str)
        result["success"] = True
        
        return result
        
    except Exception as e:
        return {"success": False, "error": str(e)}
