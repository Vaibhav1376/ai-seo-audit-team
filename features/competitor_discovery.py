"""
Competitor Discovery
Automatically find competitors based on keyword overlap
"""
from serpapi.google_search import GoogleSearch
import google.generativeai as genai
import os
import json
from typing import Dict, List
from collections import Counter

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def discover_competitors(url: str, keywords: List[str] = None, method: str = "serp") -> Dict:
    """
    Automatically discover competitors
    
    Args:
        url: Your URL
        keywords: List of keywords to check (if None, will extract from your site)
        method: 'serp' (SERP analysis) or 'content' (content similarity)
        
    Returns:
        Dict with discovered competitors
    """
    print(f"🔍 Discovering competitors for {url}...")
    
    if method == "serp":
        return _discover_via_serp(url, keywords)
    elif method == "content":
        return _discover_via_content(url)
    else:
        return {"success": False, "error": "Invalid method"}


def _discover_via_serp(url: str, keywords: List[str]) -> Dict:
    """
    Find competitors by analyzing who ranks for your keywords
    
    Args:
        url: Your URL
        keywords: Keywords to analyze
        
    Returns:
        Dict with competitors found in SERPs
    """
    if not SERPAPI_KEY:
        return {"success": False, "error": "SERPAPI_KEY not configured"}
    
    if not keywords:
        # Extract keywords from your site first
        print("   📄 Extracting keywords from your site...")
        try:
            from utils.scraper import scrape_url
            data = scrape_url(url)
            
            if not data.get('success', False):
                 return {"success": False, "error": "Failed to scrape site for keywords"}

            # Use AI to extract main keywords
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            gemini = genai.GenerativeModel(model_name="gemini-1.5-flash")
            
            prompt = f"""Extract 5-10 main SEO keywords from this content:

Title: {data.get('title', '')}
Content: {data.get('text', '')[:1500]}

Return only keywords as comma-separated list."""
            
            response = gemini.generate_content(prompt)
            keywords = [k.strip() for k in response.text.split(',')][:10]
            print(f"   ✅ Extracted {len(keywords)} keywords")
        except Exception as e:
            return {"success": False, "error": f"Keyword extraction failed: {str(e)}"}
    
    print(f"   🔍 Analyzing SERPs for {len(keywords)} keywords...")
    
    competitor_counts = Counter()
    competitor_data = {}
    
    clean_url = url.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
    
    for keyword in keywords[:10]:  # Limit to 10 keywords to save API credits
        try:
            params = {
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "q": keyword,
                "num": 20  # Top 20 results
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            for i, result in enumerate(results.get("organic_results", [])[:20], start=1):
                result_url = result.get("link", "")
                # Simple domain extraction
                if "//" in result_url:
                    result_domain = result_url.split("//")[1].replace("www.", "").split("/")[0]
                else:
                    result_domain = result_url.replace("www.", "").split("/")[0]
                
                # Skip your own domain
                if result_domain in clean_url or clean_url in result_domain:
                    continue
                
                # Count appearances
                competitor_counts[result_domain] += 1
                
                # Store data
                if result_domain not in competitor_data:
                    competitor_data[result_domain] = {
                        "domain": result_domain,
                        "first_seen_position": i,
                        "keywords_ranked": [keyword],
                        "best_position": i,
                        "example_title": result.get("title", ""),
                        "example_url": result_url
                    }
                else:
                    competitor_data[result_domain]["keywords_ranked"].append(keyword)
                    if i < competitor_data[result_domain]["best_position"]:
                        competitor_data[result_domain]["best_position"] = i
        
        except Exception as e:
            print(f"   ⚠️ Error checking '{keyword}': {e}")
    
    # Sort by keyword overlap
    top_competitors = sorted(
        competitor_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:20]
    
    # Build competitor list
    competitors = []
    for domain, count in top_competitors:
        comp_info = competitor_data[domain]
        
        # Calculate threat level
        threat_level = "High" if count >= 5 else "Medium" if count >= 3 else "Low"
        
        competitors.append({
            "domain": domain,
            "keyword_overlap": count,
            "keywords_ranked": comp_info["keywords_ranked"],
            "best_position": comp_info["best_position"],
            "threat_level": threat_level,
            "example_url": comp_info["example_url"],
            "example_title": comp_info["example_title"]
        })
    
    print(f"   ✅ Found {len(competitors)} competitors")
    
    return {
        "success": True,
        "url": url,
        "keywords_analyzed": len(keywords),
        "total_competitors": len(competitors),
        "top_competitors": competitors[:10],
        "all_competitors": competitors,
        "threat_breakdown": {
            "high": len([c for c in competitors if c["threat_level"] == "High"]),
            "medium": len([c for c in competitors if c["threat_level"] == "Medium"]),
            "low": len([c for c in competitors if c["threat_level"] == "Low"])
        }
    }


def _discover_via_content(url: str) -> Dict:
    """
    Find competitors using AI content similarity analysis
    
    Args:
        url: Your URL
        
    Returns:
        Dict with content-similar competitors
    """
    print("   🧠 Using AI to find content-similar competitors...")
    
    from utils.scraper import scrape_url
    
    # Scrape your site
    my_data = scrape_url(url)
    
    if not my_data.get("success"):
        return {"success": False, "error": "Failed to scrape your URL"}
    
    # Use AI to identify niche and find competitors
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    prompt = f"""Analyze this website and identify direct competitors.

URL: {url}
Title: {my_data.get('title', '')}
Content: {my_data.get('text', '')[:2000]}

Based on the content, identify:
1. The specific niche/industry
2. 10-15 well-known competitor domains in this niche
3. Why each is a competitor

Return as JSON:
{{
    "niche": "specific niche description",
    "sub_niche": "more specific category",
    "competitors": [
        {{
            "domain": "competitor1.com",
            "name": "Company Name",
            "similarity_score": 9,
            "reason": "why they compete"
        }}
    ]
}}
"""
    
    try:
        response = gemini.generate_content(prompt)
        response_text = response.text.strip()
        
        # CORRECTED JSON PARSING LOGIC
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]
        else:
            json_str = response_text
        
        result = json.loads(json_str)
        
        print(f"   ✅ Found {len(result.get('competitors', []))} competitors via AI")
        
        return {
            "success": True,
            "url": url,
            "niche": result.get("niche", ""),
            "sub_niche": result.get("sub_niche", ""),
            "competitors": result.get("competitors", []),
            "method": "ai_content_analysis"
        }
        
    except Exception as e:
        print(f"   ❌ AI analysis failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def analyze_competitor_strength(competitor_url: str) -> Dict:
    """
    Analyze a competitor's strength across multiple factors
    
    Args:
        competitor_url: Competitor URL to analyze
        
    Returns:
        Dict with strength analysis
    """
    print(f"💪 Analyzing competitor strength: {competitor_url}")
    
    # Lazy imports to match your structure
    try:
        from features.domain_authority import get_domain_authority
        from features.backlink_database import get_backlink_profile
        from utils.scraper import scrape_url
    except ImportError:
        return {"success": False, "error": "Required modules not found"}
    
    strength_score = 0
    factors = {}
    
    try:
        # Domain Authority
        da_result = get_domain_authority(competitor_url)
        if da_result.get("success"):
            da = da_result["domain_authority"]
            factors["domain_authority"] = da
            
            if da >= 70:
                strength_score += 30
            elif da >= 50:
                strength_score += 20
            elif da >= 30:
                strength_score += 10
        
        # Backlink Profile
        backlink_result = get_backlink_profile(competitor_url, limit=50)
        if backlink_result.get("success"):
            total_backlinks = backlink_result.get("total_backlinks", 0)
            factors["backlink_count"] = total_backlinks
            
            if total_backlinks >= 10000:
                strength_score += 30
            elif total_backlinks >= 1000:
                strength_score += 20
            elif total_backlinks >= 100:
                strength_score += 10
        
        # Content Analysis
        content = scrape_url(competitor_url)
        if content.get("success"):
            word_count = content.get("word_count", 0)
            factors["content_depth"] = word_count
            
            if word_count >= 2000:
                strength_score += 20
            elif word_count >= 1000:
                strength_score += 15
            elif word_count >= 500:
                strength_score += 10
        
        # Overall rating
        if strength_score >= 70:
            rating = "Very Strong 🔴"
        elif strength_score >= 50:
            rating = "Strong 🟠"
        elif strength_score >= 30:
            rating = "Moderate 🟡"
        else:
            rating = "Weak 🟢"
        
        print(f"   📊 Strength Score: {strength_score}/100 - {rating}")
        
        return {
            "success": True,
            "competitor_url": competitor_url,
            "strength_score": strength_score,
            "rating": rating,
            "factors": factors
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
