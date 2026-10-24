'''from .agent import agent

__all__ = ["agent"]
'''
"""
AI SEO Audit Team Package
Sequential multi-agent system for comprehensive SEO audits
"""

from .agent import (
    seo_audit_team,
    page_auditor_agent,
    serp_analyst_agent,
    optimization_advisor_agent,
    PageAuditOutput,
    SerpAnalysis,
)

__version__ = "1.0.0"
__all__ = [
    "seo_audit_team",
    "page_auditor_agent",
    "serp_analyst_agent",
    "optimization_advisor_agent",
    "PageAuditOutput",
    "SerpAnalysis",
]
