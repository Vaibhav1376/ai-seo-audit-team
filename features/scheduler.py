import os
import json
import sqlite3
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
DB_PATH = os.path.join(os.getcwd(), "data", "seo_audit.db")
# --- New Imports for Rank Tracking ---
# Ensure you have these modules or comment them out if testing without them
try:
    from features.rank_tracking import check_keyword_rank
    from utils.database import get_tracked_keywords
except ImportError:
    pass # Handle cases where these modules might not exist yet

class AuditScheduler:
    def __init__(self):
        self.db_path = DB_PATH
        self.scheduler = BackgroundScheduler()
        logging.basicConfig(level=logging.INFO)
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database (Shared with main app)"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create schedules table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                frequency TEXT NOT NULL,
                niche TEXT,
                created_at TEXT,
                last_run TEXT,
                active INTEGER DEFAULT 1
            )
        """)
        # Create results table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                date TEXT NOT NULL,
                score INTEGER,
                data_json TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def add_schedule(self, url: str, frequency: str, niche: str = "general"):
        """Add a new scheduled audit
        frequency: 'daily', 'weekly', 'monthly'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO schedules (url, frequency, niche, created_at)
            VALUES (?, ?, ?, ?)
        """, (url, frequency, niche, now))
        
        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Add to APScheduler
        self._schedule_job(schedule_id, url, frequency, niche)
        
        return schedule_id
    
    def _schedule_job(self, schedule_id: int, url: str, frequency: str, niche: str):
        """Schedule the actual job"""
        # Lazy import to avoid circular dependencies
        try:
            from workflows import run_single_page_audit
        except ImportError:
            run_single_page_audit = None
        
        def run_audit():
            if not run_single_page_audit:
                print("❌ Workflow module not found")
                return

            try:
                report, auditdata, serpdata = run_single_page_audit(url, niche)
                
                # Save results
                self._save_result(schedule_id, url, auditdata)
                
                print(f"✅ Scheduled audit complete for {url}")
            except Exception as e:
                print(f"❌ Scheduled audit failed: {e}")
        
        # Set trigger
        if frequency == "daily":
            trigger = CronTrigger(hour=2, minute=0)  # 2 AM daily
        elif frequency == "weekly":
            trigger = CronTrigger(day_of_week=1, hour=2, minute=0)  # Monday 2 AM
        elif frequency == "monthly":
            trigger = CronTrigger(day=1, hour=2, minute=0)  # 1st of month
        else:
            raise ValueError(f"Invalid frequency: {frequency}")
        
        self.scheduler.add_job(
            run_audit,
            trigger=trigger,
            id=f"audit_{schedule_id}",
            replace_existing=True
        )
    
    def _save_result(self, schedule_id: int, url: str, auditdata: dict):
        """Save audit result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        scores = auditdata.get("scores", {})
        now = datetime.now().isoformat()
        
        # Save to JSON file
        safe_url = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50]
        report_filename = f"audits_history/{safe_url}_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(report_filename, "w") as f:
            json.dump(auditdata, f, indent=2)
        
        cursor.execute("""
            INSERT INTO audit_results 
            (schedule_id, url, run_date, overall_score, onpage_score, technical_score, content_score, report_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            schedule_id, url, now,
            scores.get("overall_score", 0),
            scores.get("onpage_score", 0),
            scores.get("technical_score", 0),
            scores.get("content_score", 0),
            report_filename
        ))
        
        conn.commit()
        conn.close()
    
    def get_history(self, url: str, limit: int = 10):
        """Get audit history for a URL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT run_date, overall_score, onpage_score, technical_score, content_score
            FROM audit_results
            WHERE url = ?
            ORDER BY run_date DESC
            LIMIT ?
        """, (url, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            "date": r[0],
            "overall": r[1],
            "onpage": r[2],
            "technical": r[3],
            "content": r[4]
        } for r in results]

    # ---------------------------------------------------------
    #  NEW: Scheduled Rank Tracking Implementation
    # ---------------------------------------------------------

    def run_daily_rank_checks(self):
        """Run rank checks for all tracked keywords"""
        print("\n" + "="*70)
        print("🕐 SCHEDULED RANK CHECK - " + datetime.now().strftime("%Y-%m-%d %H:%M"))
        print("="*70)
        
        # Note: Keeps original DB path from your snippet (separate from audits DB)
        try:
            conn = sqlite3.connect("data/seo_audit.db")
            cursor = conn.cursor()
            
            # Get all active tracked keywords
            cursor.execute("""
                SELECT DISTINCT url, keyword 
                FROM tracked_keywords 
                WHERE status = 'active'
            """)
            
            keywords = cursor.fetchall()
            conn.close()
            
            print(f"📊 Checking {len(keywords)} tracked keywords...")
            
            for url, keyword in keywords:
                try:
                    # using the imported function from features.rank_tracking
                    result = check_keyword_rank(url, keyword)
                    if result.get("success"):
                        position = result.get("position")
                        if position:
                            print(f"   ✅ {keyword}: #{position}")
                        else:
                            print(f"   📭 {keyword}: Not in top 100")
                    else:
                        error_msg = result.get("error", "Unknown error")
                        print(f"   ❌ {keyword}: Error - {error_msg}")
                except Exception as e:
                    print(f"   ❌ {keyword}: Error - {e}")
            
            print("✅ Daily rank check complete!\n")
            
        except sqlite3.OperationalError:
            print("❌ Error: Could not connect to 'data/seo_audit.db'. Check if database exists.")
        except Exception as e:
            print(f"❌ Rank check failed: {e}")

    def start_rank_tracking(self):
        """Add the daily rank tracking job to the scheduler"""
        # Run daily at 8 AM
        self.scheduler.add_job(
            self.run_daily_rank_checks,
            'cron',
            hour=8,
            minute=0,
            id='daily_rank_check',
            replace_existing=True
        )
        print("✅ Rank tracking job added (runs daily at 8 AM)")

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("✅ Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("⏹️  Scheduler stopped")
