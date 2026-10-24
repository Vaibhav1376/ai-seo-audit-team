"""
Domain Authority & Page Authority
Get Moz metrics for URLs
"""
from features.moz_client import MozAPI
from typing import Dict
from urllib.parse import urlparse

def get_domain_authority(url: str) -> Dict:
    """
    Get Domain Authority for a URL
    
    Args:
        url: URL to check (can be full URL or just domain)
        
    Returns:
        Dict with DA/PA scores
    """
    print(f"📊 Fetching Domain Authority for {url}...")
    
    try:
        moz = MozAPI()
        result = moz.get_url_metrics(url)
        
        if result.get("success"):
            da = result["domain_authority"]
            pa = result["page_authority"]
            spam_score = result["spam_score"]
            
            # Interpret scores
            da_rating = _get_da_rating(da)
            spam_rating = _get_spam_rating(spam_score)
            
            print(f"   ✅ DA: {da}/100 ({da_rating})")
            print(f"   ✅ PA: {pa}/100")
            print(f"   ✅ Spam Score: {spam_score}% ({spam_rating})")
            
            return {
                **result,
                "da_rating": da_rating,
                "spam_rating": spam_rating
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


def compare_domain_authority(url1: str, url2: str) -> Dict:
    """
    Compare DA/PA between two domains
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        Dict with comparison
    """
    print(f"⚖️ Comparing domain authority...")
    
    result1 = get_domain_authority(url1)
    result2 = get_domain_authority(url2)
    
    if result1.get("success") and result2.get("success"):
        da_diff = result1["domain_authority"] - result2["domain_authority"]
        pa_diff = result1["page_authority"] - result2["page_authority"]
        
        winner = "url1" if da_diff > 0 else "url2" if da_diff < 0 else "tie"
        
        return {
            "success": True,
            "url1": {
                "url": url1,
                "da": result1["domain_authority"],
                "pa": result1["page_authority"],
                "spam_score": result1["spam_score"]
            },
            "url2": {
                "url": url2,
                "da": result2["domain_authority"],
                "pa": result2["page_authority"],
                "spam_score": result2["spam_score"]
            },
            "comparison": {
                "da_difference": da_diff,
                "pa_difference": pa_diff,
                "winner": winner
            }
        }
    else:
        return {
            "success": False,
            "error": "Failed to fetch metrics for one or both URLs"
        }


def _get_da_rating(da: int) -> str:
    """Get human-readable DA rating"""
    if da >= 70:
        return "Excellent"
    elif da >= 50:
        return "Good"
    elif da >= 30:
        return "Average"
    elif da >= 15:
        return "Below Average"
    else:
        return "Poor"


def _get_spam_rating(spam_score: int) -> str:
    """Get human-readable spam rating"""
    if spam_score <= 10:
        return "Very Low Risk"
    elif spam_score <= 30:
        return "Low Risk"
    elif spam_score <= 60:
        return "Medium Risk"
    else:
        return "High Risk"
