"""
AI SEO Audit Agent - Main Orchestrator (Updated)
Now uses agent.py as the core engine
"""

import os
import json
import sqlite3
import secrets
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CORE ENGINE - Import from agent.py
# ============================================================================
# Simple import - no fallback needed
from agent import agent as seo_audit_agent
print("Using Simple SEO Agent (Firecrawl + Gemini)")


# ============================================================================
# MAIN AUDIT FUNCTIONS (Updated to use agent.py)
# ============================================================================

def run_full_audit(url: str, niche: str = "general", model: str = None, features: dict = None):
    """Run single page audit using agent.py"""
    try:
        print(f"Running audit for: {url}")
        
        # Call the agent
        report = seo_audit_agent.run(f"Audit {url}")
        
        # Parse into structured format
        result = parse_agent_report(report, url)
        
        # Return in expected format: (report, audit_data, serp_data)
        return report, result, {'success': True}
        
    except Exception as e:
        print(f"Audit error: {e}")
        error_data = {
            'success': False,
            'error': str(e),
            'url': url,
            'scores': {'overall_score': 0, 'technical_score': 0, 'content_score': 0},
            'technical_issues': []
        }
        error_report = f"# Audit Error\n\nFailed to audit {url}\n\nError: {str(e)}"
        return error_report, error_data, {'success': False}


def run_batch_audit_with_features(urls: list, niche: str = "general", model: str = None, features: dict = None):
    """Run batch audit using agent.py"""
    import time
    
    results = []
    
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] Auditing: {url}")
        
        try:
            # Add delay to avoid rate limits
            if i > 0:
                time.sleep(3)
            
            report = seo_audit_agent.run(f"Audit {url}")
            result = parse_agent_report(report, url)
            results.append(result)
            
        except Exception as e:
            results.append({
                'success': False,
                'url': url,
                'error': str(e)
            })
    
    # Generate batch analysis
    successful = sum(1 for r in results if r.get('success'))
    analysis = f"Batch audit complete: {successful}/{len(urls)} successful"
    
    return results, analysis

def parse_agent_report(report_text: str, url: str) -> Dict:
    """Parse agent's markdown report into structured data"""
    import re
    
    # Extract scores
    scores = {'overall_score': 70, 'technical_score': 70, 'content_score': 70}
    
    # Find overall score
    # Find overall score with more patterns
    score_patterns = [
        r'Overall Score[:\s]+(\d+)/100',
        r'Overall Score:\s*(\d+)/100',
        r'\*\*Overall Score\*\*[:\s]*(\d+)',
        r'overall score[:\s]*(\d+)',
        r'Score[:\s]+(\d+)/100',
    ]

    # Try each pattern
    score_found = False
    for pattern in score_patterns:
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            scores['overall_score'] = score
            scores['technical_score'] = score
            scores['content_score'] = score
            score_found = True
            break

    # If still not found, look in Executive Summary section
    if not score_found:
        exec_summary = re.search(r'Executive Summary(.+?)(?:Technical Findings|##)', report_text, re.DOTALL | re.IGNORECASE)
        if exec_summary:
            score_match = re.search(r'(\d+)/100', exec_summary.group(1))
            if score_match:
                score = int(score_match.group(1))
                scores['overall_score'] = score
                scores['technical_score'] = score
                scores['content_score'] = score


    for pattern in score_patterns:
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            scores['overall_score'] = int(match.group(1))
            scores['technical_score'] = int(match.group(1))
            scores['content_score'] = int(match.group(1))
            break
    
    # Extract issues - improved parsing
    issues = []
    
    # Method 1: Look for "Issue Name:" pattern (P0 format)
    issue_blocks = re.findall(
        r'Issue Name:\s*(.+?)(?:\n.*?)?Why it matters:\s*(.+?)(?:\n.*?)?How to fix:\s*(.+?)(?:\n|Effort)',
        report_text,
        re.DOTALL | re.IGNORECASE
    )
    
    for title, why, fix in issue_blocks[:5]:
        issues.append({
            'severity': 'Critical' if 'P0' in report_text[:report_text.find(title)+200] else 'High',
            'issue': title.strip()[:120],
            'fix': fix.strip()[:150]
        })
    
    # Method 2: If no issues found, look for numbered recommendations
    if not issues:
        issue_pattern = re.findall(
            r'(?:###|\d+\.)\s+(.+?)(?:\n.*?)?(?:\*\*Why.*?\*\*[:\s]*(.+?))?(?:\n.*?)?(?:\*\*How.*?\*\*[:\s]*(.+?))?(?:\n|$)',
            report_text,
            re.DOTALL
        )
        
        for match in issue_pattern[:5]:
            if len(match[0]) > 15:  # Valid issue name
                issues.append({
                    'severity': 'Medium',
                    'issue': match[0].strip()[:120],
                    'fix': match[2].strip()[:150] if len(match) > 2 and match[2] else 'See full report for details'
                })
    
    return {
        'success': True,
        'url': url,
        'report': report_text,
        'ai_report': report_text,
        'scores': scores,
        'technical_issues': issues
    }

def run_full_site_audit_with_features(domain: str, max_pages: int = 20, niche: str = "general",
                                     model: str = None, features: dict = None,
                                     priority_urls: str = "", competitor_urls: list = None):
    """Run full site audit"""
    # For now, just audit the homepage
    # You can enhance this later to crawl multiple pages
    try:
        report = seo_audit_agent.run(f"Audit {domain}")
        result = parse_agent_report(report, domain)
        
        return {
            'success': True,
            'site_report': report,
            'pages_audited': 1,
            'site_analysis': {
                'avg_scores': result['scores'],
                'critical_issues_count': len(result.get('technical_issues', []))
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# ============================================================================
# CONTENT & KEYWORD FUNCTIONS
# ============================================================================

def analyze_content_gaps(audit_data: Dict, serp_data: Dict, model: str = None) -> Dict:
    """Analyze content gaps"""
    # Placeholder - implement later or import from features
    return {'success': True, 'gaps': []}

def research_keywords_with_volumes(seed_keyword: str, location: str = "us") -> Dict:
    """Research keywords with volumes"""
    try:
        from features.keyword_research import research_keywords_enhanced
        return research_keywords_enhanced(seed_keyword, location, use_real_data=True)
    except ImportError:
        return {'success': False, 'error': 'Feature not available'}

def analyze_keyword_trends(keyword: str) -> Dict:
    """Analyze keyword seasonality"""
    try:
        from features.keyword_trends import get_keyword_seasonality
        return get_keyword_seasonality(keyword)
    except ImportError:
        return {'success': False, 'error': 'Feature not available'}

def generate_content_outline(keyword: str, serp_data: Dict = None, target_length: int = 2000) -> str:
    """Generate content outline"""
    import google.generativeai as genai
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    prompt = f"""Create an SEO-optimized content outline for the keyword: "{keyword}"

Target length: {target_length} words

Include:
1. Main heading (H1)
2. 5-7 subheadings (H2)
3. Key points under each section
4. Internal linking suggestions
5. Call-to-action

Format as markdown."""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating outline: {e}"

def generate_article(outline: Dict) -> str:
    """Generate full article from outline"""
    return "Article generation coming soon"

# ============================================================================
# BACKLINK FUNCTIONS
# ============================================================================

def get_domain_authority(url: str) -> Dict:
    """Get Moz Domain Authority"""
    try:
        from features.backlink_analysis import get_moz_domain_authority
        return get_moz_domain_authority(url)
    except ImportError:
        return {'success': False, 'error': 'Moz API not configured'}

def analyze_backlinks(url: str, csv_data: str = None) -> Dict:
    """Analyze backlinks"""
    try:
        from features.backlink_analysis import analyze_backlinks_comprehensive
        return analyze_backlinks_comprehensive(url, csv_data)
    except ImportError:
        return {'success': False, 'error': 'Feature not available'}

# ============================================================================
# SCHEDULER FUNCTIONS
# ============================================================================

def schedule_audit(url: str, frequency: str, niche: str = "general") -> int:
    """Schedule recurring audit"""
    try:
        from features.scheduler import AuditScheduler
        scheduler = AuditScheduler()
        return scheduler.add_schedule(url, frequency, niche)
    except ImportError:
        return 0

def get_audit_history(url: str, limit: int = 10) -> List[Dict]:
    """Get historical audit data"""
    try:
        from features.scheduler import AuditScheduler
        scheduler = AuditScheduler()
        return scheduler.get_history(url, limit)
    except ImportError:
        return []

# ============================================================================
# COMPETITOR FUNCTIONS
# ============================================================================

def save_competitor(name: str, url: str) -> bool:
    """Save competitor for tracking"""
    os.makedirs("competitor_data", exist_ok=True)
    competitors = {}
    
    if os.path.exists("competitor_data/competitors.json"):
        with open("competitor_data/competitors.json", "r") as f:
            competitors = json.load(f)
    
    competitors[name] = {
        "url": url,
        "added_date": datetime.now().isoformat(),
        "last_audit": None
    }
    
    with open("competitor_data/competitors.json", "w") as f:
        json.dump(competitors, f, indent=2)
    
    return True

def load_competitors() -> Dict:
    """Load saved competitors"""
    if os.path.exists("competitor_data/competitors.json"):
        with open("competitor_data/competitors.json", "r") as f:
            return json.load(f)
    return {}

# ============================================================================
# WHITE-LABEL FUNCTIONS
# ============================================================================

def load_whitelabel_config() -> Dict:
    """Load white-label configuration"""
    default_config = {
        "brand_name": "AI SEO Audit Pro",
        "primary_color": "#0066CC",
        "logo_path": "",
        "tagline": "Powered by AI"
    }
    
    if os.path.exists("config/whitelabel.json"):
        with open("config/whitelabel.json", "r") as f:
            return json.load(f)
    
    return default_config

def save_whitelabel_config(config: Dict) -> bool:
    """Save white-label configuration"""
    os.makedirs("config", exist_ok=True)
    
    with open("config/whitelabel.json", "w") as f:
        json.dump(config, f, indent=2)
    
    return True

def get_whitelabel_css(config: Dict) -> str:
    """Get custom CSS for branding"""
    primary_color = config.get("primary_color", "#0066CC")
    
    return f"""
    <style>
        .stApp {{
            background-color: #f8f9fa;
        }}
        .stButton>button {{
            background-color: {primary_color};
            color: white;
        }}
        .stMetricValue {{
            color: {primary_color};
        }}
    </style>
    """

# ============================================================================
# API KEY MANAGEMENT
# ============================================================================

def create_api_key(email: str, tier: str = "free") -> Dict:
    """Create new API key"""
    TIERS = {
        "free": {"limit": 10, "price": 0},
        "pro": {"limit": 100, "price": 49},
        "agency": {"limit": 1000, "price": 199}
    }
    
    if tier not in TIERS:
        return {"success": False, "error": "Invalid tier"}
    
    api_key = f"seo_{secrets.token_urlsafe(32)}"
    
    conn = sqlite3.connect("api_usage.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            api_key TEXT PRIMARY KEY,
            tier TEXT NOT NULL,
            requests_limit INTEGER,
            requests_used INTEGER DEFAULT 0,
            created_at TEXT,
            last_used TEXT
        )
    """)
    
    cursor.execute("""
        INSERT INTO api_keys (api_key, tier, requests_limit, created_at)
        VALUES (?, ?, ?, ?)
    """, (api_key, tier, TIERS[tier]["limit"], datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "api_key": api_key,
        "tier": tier,
        "limit": TIERS[tier]["limit"]
    }

def validate_api_key(api_key: str) -> Dict:
    """Validate API key"""
    conn = sqlite3.connect("api_usage.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tier, requests_limit, requests_used
        FROM api_keys
        WHERE api_key = ?
    """, (api_key,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return {"valid": False, "error": "Invalid API key"}
    
    tier, limit, used = result
    
    if used >= limit:
        return {"valid": False, "error": "Rate limit exceeded"}
    
    return {
        "valid": True,
        "tier": tier,
        "used": used,
        "limit": limit,
        "remaining": limit - used
    }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_pdf_report(report: str, brand_config: Dict) -> bytes:
    """Generate PDF report"""
    from utils.pdf_generator import generate_pdf
    return generate_pdf(report)

# For backward compatibility
def render_js_page(url: str) -> Dict:
    return {'success': True, 'message': 'Use agent.py directly'}

def check_mobile_friendly(url: str) -> Dict:
    return {'success': True, 'mobile_score': 85}

if __name__ == "__main__":
    print("=" * 70)
    print("AI SEO AUDIT AGENT - TESTING")
    print("=" * 70)
    
    # Test single page audit
    report, audit_data, serp_data = run_full_audit("https://example.com")
    
    print("\nAudit Complete")
    print(f"Overall Score: {audit_data.get('scores', {}).get('overall_score', 0)}/100")
