"""
Referring Domains Analysis
Find which domains are linking to you
"""
from features.moz_client import MozAPI
from typing import Dict, List

def get_referring_domains(url: str, limit: int = 50) -> Dict:
    """
    Get domains that link to this URL
    
    Args:
        url: Target URL
        limit: Max domains to fetch
        
    Returns:
        Dict with referring domain data
    """
    print(f"🔗 Fetching referring domains for {url}...")
    
    try:
        moz = MozAPI()
        result = moz.get_linking_domains(url, limit=limit)
        
        if result.get("success"):
            domains = result["linking_domains"]
            
            # Analyze referring domains
            analyzed = []
            for domain in domains:
                domain_url = domain.get("source_domain", "")
                analyzed.append({
                    "domain": domain_url,
                    "domain_authority": domain.get("domain_authority", 0),
                    "spam_score": domain.get("spam_score", 0),
                    "links_to_target": domain.get("external_pages_to_target", 0)
                })
            
            # Sort by DA
            analyzed.sort(key=lambda x: x["domain_authority"], reverse=True)
            
            # Statistics
            avg_da = sum(d["domain_authority"] for d in analyzed) / len(analyzed) if analyzed else 0
            high_authority = len([d for d in analyzed if d["domain_authority"] >= 50])
            low_spam = len([d for d in analyzed if d["spam_score"] <= 10])
            
            print(f"   ✅ Found {len(analyzed)} referring domains")
            print(f"   📊 Avg DA: {avg_da:.1f}")
            print(f"   ⭐ High Authority: {high_authority}")
            
            return {
                "success": True,
                "url": url,
                "total_domains": len(analyzed),
                "domains": analyzed,
                "statistics": {
                    "average_da": round(avg_da, 1),
                    "high_authority_count": high_authority,
                    "low_spam_count": low_spam,
                    "median_da": _calculate_median([d["domain_authority"] for d in analyzed])
                }
            }
        else:
            print(f"   ❌ Failed: {result.get('error')}")
            return result
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def compare_referring_domains(url1: str, url2: str) -> Dict:
    """
    Compare referring domains between two URLs
    
    Args:
        url1: Your URL
        url2: Competitor URL
        
    Returns:
        Dict with comparison
    """
    print(f"⚖️ Comparing referring domains...")
    
    result1 = get_referring_domains(url1, limit=100)
    result2 = get_referring_domains(url2, limit=100)
    
    if result1.get("success") and result2.get("success"):
        domains1 = set(d["domain"] for d in result1["domains"])
        domains2 = set(d["domain"] for d in result2["domains"])
        
        # Find unique and shared
        unique_to_url1 = domains1 - domains2
        unique_to_url2 = domains2 - domains1
        shared = domains1 & domains2
        
        return {
            "success": True,
            "url1_total": len(domains1),
            "url2_total": len(domains2),
            "unique_to_url1": len(unique_to_url1),
            "unique_to_url2": len(unique_to_url2),
            "shared_domains": len(shared),
            "url1_advantage": len(unique_to_url1) - len(unique_to_url2),
            "shared_domain_list": list(shared)[:20]  # First 20
        }
    else:
        return {
            "success": False,
            "error": "Failed to fetch referring domains"
        }


def _calculate_median(numbers: List[float]) -> float:
    """Calculate median of a list"""
    if not numbers:
        return 0
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
    return sorted_nums[mid]
