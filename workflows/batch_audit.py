"""
Batch Audit Workflow
Audit multiple URLs at once
"""
from agents.page_auditor import pageauditor
from agents.report_generator import generate_report
from typing import List, Dict, Tuple
import time

def run_batch_audit_with_features(
    urls: List[str],
    niche: str = "general",
    model: str = "gemini-1.5-flash",
    features: Dict = None
) -> Tuple[List[Dict], str]:
    """
    Run batch audit on multiple URLs
    
    Args:
        urls: List of URLs to audit
        niche: Business niche
        model: Gemini model to use
        features: Dict of enabled features
        
    Returns:
        Tuple of (results_list, analysis_summary)
    """
    print(f"\n{'='*70}")
    print(f"📦 BATCH AUDIT: {len(urls)} URLs")
    print(f"{'='*70}")
    
    if features is None:
        features = {}
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        
        try:
            # Run audit
            audit_data = pageauditor(url, model=model, features=features)
            
            # Generate report
            report = generate_report(audit_data, niche=niche)
            
            results.append({
                "url": url,
                "success": audit_data.get("success", True),
                "auditdata": audit_data,
                "report": report
            })
            
            print(f"   ✅ Complete - Score: {audit_data.get('scores', {}).get('overall_score', 0)}/100")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({
                "url": url,
                "success": False,
                "error": str(e),
                "auditdata": {"scores": {"overall_score": 0, "content_score": 0, "on_page_score": 0, "technical_score": 0, "mobile_score": 0}},
                "report": f"# Error\n\nFailed to audit {url}: {str(e)}"
            })
        
        # Small delay to avoid rate limits
        if i < len(urls):
            time.sleep(2)
    
    # Generate batch analysis
    print("\n📊 Generating batch analysis...")
    batch_analysis = _generate_batch_analysis(results)
    
    return results, batch_analysis


def _generate_batch_analysis(results: List[Dict]) -> str:
    """Generate analysis summary for batch results"""
    
    successful_results = [r for r in results if r.get("success")]
    failed_results = [r for r in results if not r.get("success")]
    
    if not successful_results:
        return "# Batch Analysis\n\n❌ All audits failed. Please check your URLs and try again."
    
    # Calculate average scores
    avg_scores = _calculate_average_scores(successful_results)
    
    # Find best and worst
    best = max(successful_results, key=lambda x: x.get("auditdata", {}).get("scores", {}).get("overall_score", 0))
    worst = min(successful_results, key=lambda x: x.get("auditdata", {}).get("scores", {}).get("overall_score", 0))
    
    # Build analysis
    analysis = f"""# 📊 Batch Audit Analysis

## Summary

- **Total URLs Analyzed:** {len(results)}
- **Successful Audits:** {len(successful_results)}
- **Failed Audits:** {len(failed_results)}

## Average Scores

- **Overall Score:** {avg_scores['overall_score']}/100
- **Content Score:** {avg_scores['content_score']}/100
- **On-Page Score:** {avg_scores['on_page_score']}/100
- **Technical Score:** {avg_scores['technical_score']}/100
- **Mobile Score:** {avg_scores['mobile_score']}/100

## Best Performing Page

**URL:** {best['url']}  
**Score:** {best['auditdata']['scores']['overall_score']}/100

## Worst Performing Page

**URL:** {worst['url']}  
**Score:** {worst['auditdata']['scores']['overall_score']}/100

## Recommendations

"""
    
    # Add recommendations based on average scores
    if avg_scores['content_score'] < 60:
        analysis += "- **Content:** Improve content depth and quality across all pages\n"
    
    if avg_scores['on_page_score'] < 60:
        analysis += "- **On-Page SEO:** Focus on optimizing meta tags and internal linking\n"
    
    if avg_scores['technical_score'] < 60:
        analysis += "- **Technical SEO:** Address technical issues site-wide\n"
    
    if avg_scores['mobile_score'] < 80:
        analysis += "- **Mobile:** Improve mobile performance and responsiveness\n"
    
    # Failed URLs
    if failed_results:
        analysis += "\n## ⚠️ Failed Audits\n\n"
        for failed in failed_results:
            analysis += f"- {failed['url']}: {failed.get('error', 'Unknown error')}\n"
    
    return analysis


def _calculate_average_scores(results: List[Dict]) -> Dict:
    """Calculate average scores safely"""
    
    # Filter only successful results with valid scores
    valid_results = [
        r for r in results 
        if r.get("success") 
        and r.get("auditdata", {}).get("scores")
    ]
    
    if not valid_results:
        return {
            "overall_score": 0,
            "content_score": 0,
            "on_page_score": 0,
            "technical_score": 0,
            "mobile_score": 0
        }
    
    # Initialize totals
    total_scores = {
        "overall_score": 0,
        "content_score": 0,
        "on_page_score": 0,
        "technical_score": 0,
        "mobile_score": 0
    }
    
    # Sum all scores
    for result in valid_results:
        scores = result["auditdata"]["scores"]
        total_scores["overall_score"] += scores.get("overall_score", 0)
        total_scores["content_score"] += scores.get("content_score", 0)
        total_scores["on_page_score"] += scores.get("on_page_score", 0)
        total_scores["technical_score"] += scores.get("technical_score", 0)
        total_scores["mobile_score"] += scores.get("mobile_score", 0)
    
    # Calculate averages
    count = len(valid_results)
    return {
        "overall_score": round(total_scores["overall_score"] / count, 1),
        "content_score": round(total_scores["content_score"] / count, 1),
        "on_page_score": round(total_scores["on_page_score"] / count, 1),
        "technical_score": round(total_scores["technical_score"] / count, 1),
        "mobile_score": round(total_scores["mobile_score"] / count, 1)
    }
