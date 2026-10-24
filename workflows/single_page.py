"""
Single Page Audit Workflow
"""
from typing import Dict, Tuple
from datetime import datetime
from agents.page_auditor import pageauditor
from agents.serp_analyst import serpanalyst
from agents.strategy_writer import strategywriter

def run_single_page_audit(
    url: str,
    niche: str = "general",
    model: str = None,
    features: Dict = None
) -> Tuple[str, Dict, Dict]:
    """
    Run complete single page audit
    
    Returns:
        Tuple of (report, audit_data, serp_data)
    """
    print(f"\n{'='*70}")
    print(f"🚀 SINGLE PAGE AUDIT")
    print(f"{'='*70}")
    print(f"🌐 URL: {url}")
    print(f"🏢 Niche: {niche}")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Agent 1: Page Audit
    audit_data = pageauditor(url, model=model, features=features)
    
    if not audit_data.get("success"):
        return (
            f"# Audit Failed\n\nError: {audit_data.get('error')}",
            audit_data,
            {}
        )
    
    # Agent 2: SERP Analysis
    primary_keyword = audit_data.get("primary_keyword", "")
    serp_data = {}
    
    if primary_keyword:
        serp_data = serpanalyst(primary_keyword, model=model)
    
    # Agent 3: Strategy Report
    report = strategywriter(audit_data, serp_data, niche, model=model)
    
    print(f"\n{'='*70}")
    print("✅ AUDIT COMPLETE!")
    print(f"{'='*70}\n")
    
    return report, audit_data, serp_data
