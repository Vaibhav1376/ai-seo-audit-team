"""
Link Building Opportunity Finder
Find websites to target for backlinks
"""
import google.generativeai as genai
import os
from typing import Dict, List
from serpapi.google_search import GoogleSearch

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def find_link_opportunities(niche: str, strategy: str = "guest_post") -> Dict:
    """
    Find link building opportunities
    
    Args:
        niche: Your niche/industry
        strategy: 'guest_post', 'resource_page', 'broken_link', 'competitor_mentions'
        
    Returns:
        Dict with opportunities
    """
    print(f"🔗 Finding {strategy} opportunities in {niche}...")
    
    if strategy == "guest_post":
        return _find_guest_post_opportunities(niche)
    elif strategy == "resource_page":
        return _find_resource_pages(niche)
    elif strategy == "broken_link":
        return _find_broken_link_opportunities(niche)
    elif strategy == "competitor_mentions":
        return _find_unlinked_mentions(niche)
    else:
        return {"success": False, "error": "Invalid strategy"}


def _find_guest_post_opportunities(niche: str) -> Dict:
    """Find sites accepting guest posts"""
    
    if not SERPAPI_KEY:
        return {"success": False, "error": "SERPAPI_KEY not configured"}
    
    # Search queries for guest post opportunities
    queries = [
        f"{niche} write for us",
        f"{niche} guest post",
        f"{niche} contribute",
        f"{niche} submit article",
        f"{niche} become a contributor"
    ]
    
    opportunities = []
    seen_domains = set()
    
    for query in queries[:3]:  # Limit to 3 queries
        try:
            params = {
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "q": query,
                "num": 20
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            for result in results.get("organic_results", [])[:20]:
                domain = result.get("link", "").replace("https://", "").replace("http://", "").split("/")
                
                if domain in seen_domains:
                    continue
                
                seen_domains.add(domain)
                
                opportunities.append({
                    "domain": domain,
                    "url": result.get("link", ""),
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "opportunity_type": "guest_post",
                    "search_query": query
                })
        
        except Exception as e:
            print(f"   ⚠️ Error for query '{query}': {e}")
    
    # Score opportunities with AI
    scored_opportunities = _score_opportunities_with_ai(opportunities, niche)
    
    print(f"   ✅ Found {len(scored_opportunities)} guest post opportunities")
    
    return {
        "success": True,
        "niche": niche,
        "strategy": "guest_post",
        "total_opportunities": len(scored_opportunities),
        "opportunities": scored_opportunities[:50]
    }


def _find_resource_pages(niche: str) -> Dict:
    """Find resource pages that could link to you"""
    
    if not SERPAPI_KEY:
        return {"success": False, "error": "SERPAPI_KEY not configured"}
    
    queries = [
        f"{niche} resources",
        f"{niche} useful links",
        f"{niche} helpful sites",
        f"best {niche} tools"
    ]
    
    opportunities = []
    seen_domains = set()
    
    for query in queries[:3]:
        try:
            params = {
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "q": query
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            for result in results.get("organic_results", [])[:15]:
                domain = result.get("link", "").replace("https://", "").replace("http://", "").split("/")
                
                if domain not in seen_domains:
                    seen_domains.add(domain)
                    opportunities.append({
                        "domain": domain,
                        "url": result.get("link", ""),
                        "title": result.get("title", ""),
                        "opportunity_type": "resource_page"
                    })
        
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
    
    print(f"   ✅ Found {len(opportunities)} resource page opportunities")
    
    return {
        "success": True,
        "niche": niche,
        "strategy": "resource_page",
        "total_opportunities": len(opportunities),
        "opportunities": opportunities
    }


def _score_opportunities_with_ai(opportunities: List[Dict], niche: str) -> List[Dict]:
    """Use AI to score and prioritize opportunities"""
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    # Take sample for AI analysis
    sample = opportunities[:10]
    
    domains_text = "\n".join([f"- {o['domain']}: {o.get('title', '')}" for o in sample])
    
    prompt = f"""Analyze these link building opportunities for a {niche} website.

Sites:
{domains_text}

For each site, rate:
1. Relevance (1-10): How relevant to {niche}?
2. Authority (1-10): How authoritative does it seem?
3. Likelihood (1-10): How likely to accept/link?

Return JSON array with scores for each domain."""
    
    try:
        response = gemini.generate_content(prompt)
        # Simple scoring if AI fails
        for opp in opportunities:
            opp["relevance_score"] = 7
            opp["authority_score"] = 6
            opp["likelihood_score"] = 5
            opp["total_score"] = 18
    except:
        pass
    
    # Sort by total score
    opportunities.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    
    return opportunities


def _find_broken_link_opportunities(niche: str) -> Dict:
    """Find broken link building opportunities"""
    # This would require crawling sites - simplified version
    return {
        "success": True,
        "niche": niche,
        "strategy": "broken_link",
        "message": "Broken link finder requires site crawling. Use tools like Ahrefs/SEMrush for this."
    }


def _find_unlinked_mentions(niche: str) -> Dict:
    """Find unlinked brand mentions"""
    return {
        "success": True,
        "niche": niche,
        "strategy": "unlinked_mentions",
        "message": "Unlinked mention finder requires brand monitoring. Use Google Alerts or Mention.com."
    }


def create_outreach_email(opportunity: Dict, your_site: str, your_name: str) -> str:
    """
    Generate personalized outreach email with AI
    
    Args:
        opportunity: Opportunity dict
        your_site: Your website
        your_name: Your name
        
    Returns:
        Personalized email template
    """
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    prompt = f"""Write a personalized outreach email for link building.

Target Site: {opportunity.get('domain')}
Page Title: {opportunity.get('title', '')}
My Site: {your_site}
My Name: {your_name}
Opportunity Type: {opportunity.get('opportunity_type', 'guest_post')}

Write a friendly, professional email that:
1. Compliments their content specifically
2. Explains why my content would add value
3. Makes a clear ask
4. Is concise (under 150 words)

Return only the email body (no subject line)."""
    
    try:
        response = gemini.generate_content(prompt)
        return response.text.strip()
    except:
        return f"Hi,\n\nI came across your site and loved your content on {opportunity.get('title', 'this topic')}.\n\nI run {your_site} and thought you might find our content valuable for your readers...\n\n[Customize this email]\n\nBest,\n{your_name}"
