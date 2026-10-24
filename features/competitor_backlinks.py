"""
Competitor Backlink Analysis
Compare backlink profiles and find gaps
"""
from features.moz_client import MozAPI
from features.domain_authority import get_domain_authority
from typing import Dict, List

def analyze_competitor_backlinks(my_url: str, competitor_url: str) -> Dict:
    """
    Full competitor backlink comparison
    
    Args:
        my_url: Your URL
        competitor_url: Competitor URL
        
    Returns:
        Dict with comparison
    """
    print(f"⚔️ Comparing backlinks: You vs Competitor...")
    
    try:
        moz = MozAPI()
        
        # Get both backlink profiles
        print("   📊 Fetching your backlinks...")
        my_backlinks = moz.get_backlinks(my_url, limit=200)
        
        print("   📊 Fetching competitor backlinks...")
        comp_backlinks = moz.get_backlinks(competitor_url, limit=200)
        
        if not my_backlinks.get("success") or not comp_backlinks.get("success"):
            return {
                "success": False,
                "error": "Failed to fetch one or both backlink profiles"
            }
        
        my_links = my_backlinks["backlinks"]
        comp_links = comp_backlinks["backlinks"]
        
        # Get domains
        my_domains = set(link.get("source_domain", "") for link in my_links)
        comp_domains = set(link.get("source_domain", "") for link in comp_links)
        
        # Find gaps
        exclusive_to_competitor = comp_domains - my_domains
        exclusive_to_me = my_domains - comp_domains
        shared = my_domains & comp_domains
        
        # Analyze competitor's exclusive domains
        gap_opportunities = []
        for domain in exclusive_to_competitor:
            # Find links from this domain
            domain_links = [l for l in comp_links if l.get("source_domain") == domain]
            if domain_links:
                best_link = max(domain_links, key=lambda x: x.get("source_domain_authority", 0))
                gap_opportunities.append({
                    "domain": domain,
                    "domain_authority": best_link.get("source_domain_authority", 0),
                    "spam_score": best_link.get("source_spam_score", 0),
                    "example_url": best_link.get("source_url", ""),
                    "opportunity_score": _calculate_opportunity_score(best_link)
                })
        
        # Sort by opportunity score
        gap_opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        print(f"   ✅ Competitor has {len(exclusive_to_competitor)} unique domains")
        print(f"   💎 Found {len([g for g in gap_opportunities if g['opportunity_score'] >= 7])} high-value opportunities")
        
        return {
            "success": True,
            "my_url": my_url,
            "competitor_url": competitor_url,
            "summary": {
                "my_total_domains": len(my_domains),
                "competitor_total_domains": len(comp_domains),
                "shared_domains": len(shared),
                "exclusive_to_competitor": len(exclusive_to_competitor),
                "exclusive_to_me": len(exclusive_to_me),
                "backlink_gap": len(exclusive_to_competitor) - len(exclusive_to_me)
            },
            "gap_opportunities": gap_opportunities[:50],  # Top 50
            "link_building_targets": [g for g in gap_opportunities if g["opportunity_score"] >= 7]
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def find_link_building_opportunities(url: str, competitors: List[str]) -> Dict:
    """
    Analyze multiple competitors to find best link building targets
    
    Args:
        url: Your URL
        competitors: List of competitor URLs
        
    Returns:
        Dict with prioritized opportunities
    """
    print(f"🎯 Finding link building opportunities from {len(competitors)} competitors...")
    
    all_opportunities = {}
    
    for comp_url in competitors[:5]:  # Max 5 competitors
        print(f"   Analyzing {comp_url}...")
        result = analyze_competitor_backlinks(url, comp_url)
        
        if result.get("success"):
            for opp in result.get("gap_opportunities", []):
                domain = opp["domain"]
                if domain in all_opportunities:
                    all_opportunities[domain]["competitor_count"] += 1
                else:
                    all_opportunities[domain] = {
                        **opp,
                        "competitor_count": 1
                    }
    
    # Sort by how many competitors use this domain
    opportunities = list(all_opportunities.values())
    opportunities.sort(key=lambda x: (x["competitor_count"], x["opportunity_score"]), reverse=True)
    
    # Categorize
    high_priority = [o for o in opportunities if o["competitor_count"] >= 3 and o["opportunity_score"] >= 7]
    medium_priority = [o for o in opportunities if o["competitor_count"] >= 2 and o["opportunity_score"] >= 5]
    
    print(f"   ✅ Found {len(high_priority)} high-priority targets")
    
    return {
        "success": True,
        "total_opportunities": len(opportunities),
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "all_opportunities": opportunities[:100]
    }


def _calculate_opportunity_score(link: Dict) -> int:
    """
    Calculate opportunity score (1-10) for a backlink opportunity
    
    Based on:
    - Domain Authority
    - Spam Score (inverted)
    - Link type (dofollow better)
    """
    da = link.get("source_domain_authority", 0)
    spam = link.get("source_spam_score", 0)
    is_dofollow = link.get("link_type", "") == "follow"
    
    score = 0
    
    # DA contribution (0-6 points)
    if da >= 70:
        score += 6
    elif da >= 50:
        score += 5
    elif da >= 30:
        score += 3
    elif da >= 20:
        score += 2
    
    # Spam score contribution (0-3 points, inverted)
    if spam <= 10:
        score += 3
    elif spam <= 30:
        score += 2
    elif spam <= 50:
        score += 1
    
    # Dofollow bonus
    if is_dofollow:
        score += 1
    
    return min(10, score)
