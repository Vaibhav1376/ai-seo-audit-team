"""
Backlink Database
Complete backlink profile analysis
"""
from features.moz_client import MozAPI
from typing import Dict, List
from datetime import datetime

def get_backlink_profile(url: str, limit: int = 100) -> Dict:
    """
    Get complete backlink profile
    
    Args:
        url: Target URL
        limit: Max backlinks to fetch
        
    Returns:
        Dict with full backlink data
    """
    print(f"🔗 Building backlink profile for {url}...")
    
    try:
        moz = MozAPI()
        
        # Get backlinks
        backlinks_result = moz.get_backlinks(url, limit=limit)
        
        if not backlinks_result.get("success"):
            return backlinks_result
        
        backlinks = backlinks_result["backlinks"]
        
        # Analyze backlinks
        analyzed_backlinks = []
        for link in backlinks:
            analyzed_backlinks.append({
                "source_url": link.get("source_url", ""),
                "source_domain": link.get("source_domain", ""),
                "target_url": link.get("target_url", ""),
                "anchor_text": link.get("anchor_text", ""),
                "link_type": link.get("link_type", "follow"),
                "source_page_authority": link.get("source_page_authority", 0),
                "source_domain_authority": link.get("source_domain_authority", 0),
                "source_spam_score": link.get("source_spam_score", 0),
                "first_seen": link.get("first_seen"),
                "last_seen": link.get("last_seen")
            })
        
        # Calculate statistics
        total_backlinks = len(analyzed_backlinks)
        dofollow = len([l for l in analyzed_backlinks if l["link_type"] == "follow"])
        nofollow = total_backlinks - dofollow
        
        avg_da = sum(l["source_domain_authority"] for l in analyzed_backlinks) / total_backlinks if total_backlinks else 0
        avg_pa = sum(l["source_page_authority"] for l in analyzed_backlinks) / total_backlinks if total_backlinks else 0
        
        high_quality = len([l for l in analyzed_backlinks if l["source_domain_authority"] >= 50])
        low_quality = len([l for l in analyzed_backlinks if l["source_domain_authority"] < 20])
        toxic = len([l for l in analyzed_backlinks if l["source_spam_score"] > 60])
        
        # Top anchor texts
        anchor_texts = {}
        for link in analyzed_backlinks:
            anchor = link["anchor_text"] or "[No anchor]"
            anchor_texts[anchor] = anchor_texts.get(anchor, 0) + 1
        
        top_anchors = sorted(anchor_texts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"   ✅ Found {total_backlinks} backlinks")
        print(f"   📊 Dofollow: {dofollow} | Nofollow: {nofollow}")
        print(f"   ⭐ High Quality: {high_quality}")
        print(f"   ⚠️ Toxic: {toxic}")
        
        return {
            "success": True,
            "url": url,
            "total_backlinks": total_backlinks,
            "backlinks": analyzed_backlinks,
            "statistics": {
                "dofollow_count": dofollow,
                "nofollow_count": nofollow,
                "dofollow_ratio": round(dofollow / total_backlinks * 100, 1) if total_backlinks else 0,
                "average_da": round(avg_da, 1),
                "average_pa": round(avg_pa, 1),
                "high_quality_count": high_quality,
                "low_quality_count": low_quality,
                "toxic_count": toxic,
                "top_anchor_texts": top_anchors
            },
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def export_backlink_report(url: str, output_format: str = "csv") -> str:
    """
    Export backlink profile to file
    
    Args:
        url: Target URL
        output_format: 'csv' or 'json'
        
    Returns:
        File content as string
    """
    profile = get_backlink_profile(url, limit=500)
    
    if not profile.get("success"):
        return f"Error: {profile.get('error')}"
    
    if output_format == "csv":
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            "source_url", "source_domain", "anchor_text", "link_type",
            "source_domain_authority", "source_spam_score"
        ])
        
        writer.writeheader()
        for link in profile["backlinks"]:
            writer.writerow({
                "source_url": link["source_url"],
                "source_domain": link["source_domain"],
                "anchor_text": link["anchor_text"],
                "link_type": link["link_type"],
                "source_domain_authority": link["source_domain_authority"],
                "source_spam_score": link["source_spam_score"]
            })
        
        return output.getvalue()
    
    else:  # JSON
        import json
        return json.dumps(profile, indent=2)
