"""
New & Lost Backlinks Tracking
Compare current backlinks with historical data
"""
from features.moz_client import MozAPI
from utils.database import save_backlinks, get_historical_backlinks, save_snapshot
from typing import Dict, List
from datetime import datetime, timedelta

def detect_new_backlinks(url: str) -> Dict:
    """
    Find new backlinks acquired since last check
    
    Args:
        url: Target URL
        
    Returns:
        Dict with new backlinks
    """
    print(f"🆕 Detecting new backlinks for {url}...")
    
    try:
        # Get current backlinks from Moz
        moz = MozAPI()
        current_result = moz.get_backlinks(url, limit=200)
        
        if not current_result.get("success"):
            return current_result
        
        current_backlinks = current_result["backlinks"]
        current_urls = set(link.get("source_url", "") for link in current_backlinks)
        
        # Get historical backlinks from database
        historical = get_historical_backlinks(url)
        historical_urls = set(link["source_url"] for link in historical if link["status"] == "active")
        
        # Find new ones
        new_urls = current_urls - historical_urls
        new_backlinks = [link for link in current_backlinks if link.get("source_url") in new_urls]
        
        # Analyze new backlinks
        if new_backlinks:
            avg_da = sum(l.get("source_domain_authority", 0) for l in new_backlinks) / len(new_backlinks)
            high_quality = len([l for l in new_backlinks if l.get("source_domain_authority", 0) >= 50])
            toxic = len([l for l in new_backlinks if l.get("source_spam_score", 0) > 60])
            
            print(f"   ✅ Found {len(new_backlinks)} new backlinks")
            print(f"   📊 Avg DA: {avg_da:.1f}")
            print(f"   ⭐ High Quality: {high_quality}")
        else:
            print(f"   📭 No new backlinks since last check")
        
        # Save current state
        save_backlinks(url, current_backlinks)
        
        return {
            "success": True,
            "url": url,
            "new_backlinks_count": len(new_backlinks),
            "new_backlinks": new_backlinks,
            "statistics": {
                "average_da": round(avg_da, 1) if new_backlinks else 0,
                "high_quality_count": high_quality if new_backlinks else 0,
                "toxic_count": toxic if new_backlinks else 0,
                "dofollow_count": len([l for l in new_backlinks if l.get("link_type") == "follow"])
            },
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def detect_lost_backlinks(url: str) -> Dict:
    """
    Find backlinks that were lost since last check
    
    Args:
        url: Target URL
        
    Returns:
        Dict with lost backlinks
    """
    print(f"❌ Detecting lost backlinks for {url}...")
    
    try:
        # Get current backlinks
        moz = MozAPI()
        current_result = moz.get_backlinks(url, limit=200)
        
        if not current_result.get("success"):
            return current_result
        
        current_backlinks = current_result["backlinks"]
        current_urls = set(link.get("source_url", "") for link in current_backlinks)
        
        # Get historical backlinks
        historical = get_historical_backlinks(url)
        historical_active = [link for link in historical if link["status"] == "active"]
        historical_urls = set(link["source_url"] for link in historical_active)
        
        # Find lost ones
        lost_urls = historical_urls - current_urls
        lost_backlinks = [link for link in historical_active if link["source_url"] in lost_urls]
        
        # Mark as lost in database
        if lost_backlinks:
            import sqlite3
            conn = sqlite3.connect("data/seo_audit.db")
            cursor = conn.cursor()
            
            for link in lost_backlinks:
                cursor.execute("""
                    UPDATE backlinks SET status = 'lost', last_seen = ?
                    WHERE target_url = ? AND source_url = ?
                """, (datetime.now().isoformat(), url, link["source_url"]))
            
            conn.commit()
            conn.close()
            
            avg_da = sum(link["source_da"] for link in lost_backlinks) / len(lost_backlinks)
            
            print(f"   ⚠️ Lost {len(lost_backlinks)} backlinks")
            print(f"   📊 Avg DA: {avg_da:.1f}")
        else:
            print(f"   ✅ No backlinks lost")
        
        return {
            "success": True,
            "url": url,
            "lost_backlinks_count": len(lost_backlinks),
            "lost_backlinks": lost_backlinks,
            "statistics": {
                "average_da": round(sum(l["source_da"] for l in lost_backlinks) / len(lost_backlinks), 1) if lost_backlinks else 0,
                "high_value_lost": len([l for l in lost_backlinks if l["source_da"] >= 50])
            },
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_backlink_growth_report(url: str, days: int = 30) -> Dict:
    """
    Get backlink growth over time
    
    Args:
        url: Target URL
        days: Number of days to analyze
        
    Returns:
        Dict with growth report
    """
    print(f"📈 Analyzing backlink growth for last {days} days...")
    
    import sqlite3
    conn = sqlite3.connect("data/seo_audit.db")
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    # Get snapshots
    cursor.execute("""
        SELECT snapshot_date, total_backlinks, dofollow_count, avg_da
        FROM backlink_snapshots
        WHERE target_url = ? AND snapshot_date >= ?
        ORDER BY snapshot_date ASC
    """, (url, cutoff_date))
    
    snapshots = cursor.fetchall()
    conn.close()
    
    if len(snapshots) < 2:
        return {
            "success": False,
            "error": "Insufficient historical data (need at least 2 snapshots)"
        }
    
    first = snapshots[0]
    last = snapshots[-1]
    
    growth = last[1] - first[1]
    growth_percentage = (growth / first[1] * 100) if first[1] > 0 else 0
    
    return {
        "success": True,
        "url": url,
        "period_days": days,
        "starting_backlinks": first[1],
        "current_backlinks": last[1],
        "net_growth": growth,
        "growth_percentage": round(growth_percentage, 1),
        "snapshots": [
            {
                "date": s[0],
                "total": s[1],
                "dofollow": s[2],
                "avg_da": s[3]
            } for s in snapshots
        ]
    }
