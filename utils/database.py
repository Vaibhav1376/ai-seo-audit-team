"""
Database for Historical Backlink Tracking
Uses SQLite for simplicity (can upgrade to PostgreSQL later)
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List
import os

DB_PATH = "data/seo_audit.db"

def init_database():
    """Initialize database with required tables"""
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Backlinks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backlinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_url TEXT NOT NULL,
            source_url TEXT NOT NULL,
            source_domain TEXT NOT NULL,
            anchor_text TEXT,
            link_type TEXT,
            source_da INTEGER,
            source_spam_score INTEGER,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            UNIQUE(target_url, source_url)
        )
    """)
    
    # Backlink snapshots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backlink_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_url TEXT NOT NULL,
            snapshot_date TEXT NOT NULL,
            total_backlinks INTEGER,
            dofollow_count INTEGER,
            avg_da REAL,
            toxic_count INTEGER,
            data_json TEXT,
            UNIQUE(target_url, snapshot_date)
        )
    """)
    
    # Domain metrics history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS domain_metrics_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            check_date TEXT NOT NULL,
            domain_authority INTEGER,
            page_authority INTEGER,
            spam_score INTEGER,
            referring_domains INTEGER,
            UNIQUE(url, check_date)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("Database initialized")


def save_backlinks(target_url: str, backlinks: List[Dict]):
    """Save backlinks to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    current_time = datetime.now().isoformat()
    
    for link in backlinks:
        cursor.execute("""
            INSERT OR REPLACE INTO backlinks 
            (target_url, source_url, source_domain, anchor_text, link_type, 
             source_da, source_spam_score, first_seen, last_seen, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT first_seen FROM backlinks WHERE target_url=? AND source_url=?), ?),
                    ?, 'active')
        """, (
            target_url,
            link.get('source_url', ''),
            link.get('source_domain', ''),
            link.get('anchor_text', ''),
            link.get('link_type', 'follow'),
            link.get('source_domain_authority', 0),
            link.get('source_spam_score', 0),
            target_url,
            link.get('source_url', ''),
            current_time,
            current_time
        ))
    
    conn.commit()
    conn.close()

def init_rank_tracking_tables():
    """Initialize tables for rank tracking"""
    conn = sqlite3.connect("data/seo_audit.db")
    cursor = conn.cursor()
    
    # Rank tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rank_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            keyword TEXT NOT NULL,
            position INTEGER,
            search_engine TEXT DEFAULT 'google',
            location TEXT DEFAULT 'United States',
            device TEXT DEFAULT 'desktop',
            check_date TEXT NOT NULL,
            serp_features TEXT,
            UNIQUE(url, keyword, search_engine, location, device, check_date)
        )
    """)
    
    # SERP features tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS serp_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            check_date TEXT NOT NULL,
            featured_snippet BOOLEAN DEFAULT 0,
            people_also_ask BOOLEAN DEFAULT 0,
            knowledge_panel BOOLEAN DEFAULT 0,
            local_pack BOOLEAN DEFAULT 0,
            image_pack BOOLEAN DEFAULT 0,
            video_results BOOLEAN DEFAULT 0,
            top_stories BOOLEAN DEFAULT 0,
            related_searches BOOLEAN DEFAULT 0,
            data_json TEXT,
            UNIQUE(keyword, check_date)
        )
    """)
    
    # Tracked keywords table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracked_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            keyword TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            target_position INTEGER,
            tracking_frequency TEXT DEFAULT 'daily',
            added_date TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            UNIQUE(url, keyword)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("Rank tracking tables initialized")

# Call this function
init_rank_tracking_tables()


def add_tracked_keyword(url: str, keyword: str, priority: str = "medium", target: int = 1):
    """Add keyword to tracking list"""
    conn = sqlite3.connect("data/seo_audit.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR IGNORE INTO tracked_keywords 
        (url, keyword, priority, target_position, added_date)
        VALUES (?, ?, ?, ?, ?)
    """, (url, keyword, priority, target, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def get_tracked_keywords(url: str) -> list:
    """Get all tracked keywords for a URL"""
    conn = sqlite3.connect("data/seo_audit.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT keyword, priority, target_position, added_date
        FROM tracked_keywords
        WHERE url = ? AND status = 'active'
        ORDER BY priority DESC, added_date DESC
    """, (url,))
    
    columns = ["keyword", "priority", "target_position", "added_date"]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results


def save_rank_check(url: str, keyword: str, position: int, location: str = "United States", device: str = "desktop"):
    """Save rank check result"""
    conn = sqlite3.connect("data/seo_audit.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO rank_tracking
        (url, keyword, position, location, device, check_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (url, keyword, position, location, device, datetime.now().date().isoformat()))
    
    conn.commit()
    conn.close()


def get_rank_history(url: str, keyword: str, days: int = 30) -> list:
    """Get rank history for keyword"""
    from datetime import timedelta
    
    conn = sqlite3.connect("data/seo_audit.db")
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
    
    cursor.execute("""
        SELECT check_date, position, device
        FROM rank_tracking
        WHERE url = ? AND keyword = ? AND check_date >= ?
        ORDER BY check_date ASC
    """, (url, keyword, cutoff_date))
    
    columns = ["date", "position", "device"]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

def save_snapshot(target_url: str, profile_data: Dict):
    """Save backlink profile snapshot"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    snapshot_date = datetime.now().date().isoformat()
    stats = profile_data.get('statistics', {})
    
    cursor.execute("""
        INSERT OR REPLACE INTO backlink_snapshots
        (target_url, snapshot_date, total_backlinks, dofollow_count, avg_da, toxic_count, data_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        target_url,
        snapshot_date,
        profile_data.get('total_backlinks', 0),
        stats.get('dofollow_count', 0),
        stats.get('average_da', 0),
        stats.get('toxic_count', 0),
        json.dumps(profile_data)
    ))
    
    conn.commit()
    conn.close()


def get_historical_backlinks(target_url: str) -> List[Dict]:
    """Get all historical backlinks for a URL"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM backlinks WHERE target_url = ? ORDER BY last_seen DESC
    """, (target_url,))
    
    columns = [desc[0] for desc in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results


# Initialize database on import
init_database()
