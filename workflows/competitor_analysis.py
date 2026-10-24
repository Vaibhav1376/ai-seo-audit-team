"""
Competitor Analysis Workflow
Compare two URLs side-by-side
"""
from agents.page_auditor import pageauditor
from agents.strategy_writer import strategywriter
import google.generativeai as genai
import os

def run_competitor_analysis(my_url: str, competitor_url: str, model: str = "Gemini 1.5 Flash"):
    """
    Compare your site against a competitor
    
    Args:
        my_url: Your website URL
        competitor_url: Competitor's URL
        model: Gemini model to use
        
    Returns:
        Dict with comparison report
    """
    print(f"\n{'='*70}")
    print(f"🔍 COMPETITOR ANALYSIS")
    print(f"{'='*70}")
    print(f"Your Site: {my_url}")
    print(f"Competitor: {competitor_url}")
    
    # Step 1: Audit both sites
    print("\n📊 Step 1/3: Auditing your site...")
    my_audit = pageauditor(my_url, model=model)
    
    print("\n📊 Step 2/3: Auditing competitor...")
    comp_audit = pageauditor(competitor_url, model=model)

    print("\n🎯 Step 3/4: Keyword gap analysis...")
    from features.competitor_keywords import analyze_competitor_keywords
    keyword_gap = analyze_competitor_keywords(my_url, competitor_url, model)
    
    # Step 3: AI Comparison
    print("\n🤖 Step 4/4: Generating comparison report...")
    comparison = _generate_comparison(my_audit, comp_audit, model)
    
    return {
        "my_audit": my_audit,
        "competitor_audit": comp_audit,
        "comparison": comparison,
        "keyword_gap": keyword_gap,  # NEW
        "success": True
    }


def _generate_comparison(my_data: dict, comp_data: dict, model: str):
    """Use AI to compare the two audits"""
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini = genai.GenerativeModel(model_name=model)
    
    prompt = f"""Compare these two websites and identify competitive gaps.

# YOUR SITE:
- Score: {my_data['scores']['overall_score']}/100
- Word Count: {my_data.get('word_count', 0)}
- Keywords: {my_data.get('primary_keyword', 'N/A')}
- Content: {my_data.get('text', '')[:800]}

# COMPETITOR:
- Score: {comp_data['scores']['overall_score']}/100
- Word Count: {comp_data.get('word_count', 0)}
- Keywords: {comp_data.get('primary_keyword', 'N/A')}
- Content: {comp_data.get('text', '')[:800]}

Provide:
1. **Winner**: Who has better SEO? (Your Site / Competitor / Tie)
2. **Content Gaps**: 5 topics competitor covers that you don't
3. **Technical Advantages**: What competitor does better technically
4. **Your Strengths**: What you do better than competitor
5. **Action Plan**: Top 3 things to do to beat competitor

Format as markdown with clear sections.
"""
    
    try:
        response = gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Comparison failed: {str(e)}"
