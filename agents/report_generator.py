"""
Report Generator
Generates markdown reports from audit data
"""
from agents.strategy_writer import strategywriter
from typing import Dict


def generate_report(audit_data: Dict, serp_data: Dict = None, niche: str = "general", model: str = None) -> str:
    """
    Generate a markdown report from audit data
    
    Args:
        audit_data: Results from page auditor
        serp_data: Optional SERP analysis data
        niche: Industry niche
        model: Gemini model to use
        
    Returns:
        Markdown report string
    """
    if serp_data is None:
        serp_data = {}
    
    # Use strategywriter to generate the report
    report = strategywriter(audit_data, serp_data, niche=niche, model=model)
    
    return report
