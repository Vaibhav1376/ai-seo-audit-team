"""
Agent 3: Strategy Writer
Generates comprehensive SEO reports
"""
import os
import google.generativeai as genai
from typing import Dict
from config import AGENT_CONFIG, NICHE_TEMPLATES


def strategywriter(audit_data: Dict, serp_data: Dict, niche: str = "general", model: str = None) -> str:
    """Agent 3: Strategy Writer
    
    Args:
        audit_data: Results from Agent 1
        serp_data: Results from Agent 2
        niche: Industry niche
        model: Gemini model to use
        
    Returns:
        Markdown report
    """

    print(f"\n{'='*70}")
    print(f"🤖 AGENT 3: Strategy Writer")
    print(f"{'='*70}")
    print(f"📝 Niche: {niche}")
    
    # Get niche template
    template = NICHE_TEMPLATES.get(niche, NICHE_TEMPLATES['general'])
    
    # Generate report with AI
    report = _generate_report_with_ai(audit_data, serp_data, template, model)
    
    print(f"✅ Agent 3 Complete! Report generated ({len(report)} chars)")
    
    return report


def _generate_report_with_ai(audit_data: Dict, serp_data: Dict, template: Dict, model: str = None) -> str:
    """Generate report with Gemini"""
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model_name = model or os.getenv("SELECTED_MODEL", AGENT_CONFIG['model'])
    gemini_model = genai.GenerativeModel(model_name=model_name)
    
    # Build comprehensive prompt
    prompt = f"""You are a senior SEO strategist. Create a comprehensive SEO audit report.

# AUDIT DATA:
- URL: {audit_data.get('url')}
- Overall Score: {audit_data.get('scores', {}).get('overall_score', 0)}/100
- Primary Keyword: {audit_data.get('primary_keyword')}
- Technical Issues: {audit_data.get('technical_issues', [])}
- Word Count: {audit_data.get('word_count')}

# TEMPLATE FOCUS:
{template.get('focus_areas', [])}

# REPORT STRUCTURE:
Create a detailed markdown report with:
1. Executive Summary (2-3 sentences)
2. Current Performance (scores breakdown)
3. Critical Issues (P0 issues that must be fixed immediately)
4. Technical Audit (on-page elements)
5. Content Analysis (quality, depth, keywords)
6. Recommendations (prioritized action items)
7. Expected Impact (realistic outcomes)

**Make it actionable, specific, and use data from the audit.**
Return ONLY the markdown report.
"""
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Report generation failed: {e}")
        return f"# SEO Audit Report\n\nError: Could not generate report - {str(e)}"
