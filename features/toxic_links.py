"""
Toxic Link Detection
Identify and analyze potentially harmful backlinks
"""
from features.moz_client import MozAPI
import google.generativeai as genai
import os
from typing import Dict, List
from datetime import datetime

def detect_toxic_links(url: str, threshold: int = 60) -> Dict:
    """
    Find toxic/spammy backlinks
    
    Args:
        url: Target URL
        threshold: Spam score threshold (default 60%)
        
    Returns:
        Dict with toxic links
    """
    print(f"🦠 Detecting toxic backlinks for {url}...")
    
    try:
        moz = MozAPI()
        result = moz.get_backlinks(url, limit=200)
        
        if not result.get("success"):
            return result
        
        backlinks = result["backlinks"]
        
        # Identify toxic links
        toxic_links = []
        for link in backlinks:
            spam_score = link.get("source_spam_score", 0)
            da = link.get("source_domain_authority", 0)
            
            # Multiple toxicity criteria
            is_toxic = False
            risk_factors = []
            
            if spam_score >= threshold:
                is_toxic = True
                risk_factors.append(f"High spam score ({spam_score}%)")
            
            if spam_score > 40 and da < 10:
                is_toxic = True
                risk_factors.append("Low authority + moderate spam")
            
            if link.get("anchor_text", "").lower() in ["viagra", "casino", "porn", "pills"]:
                is_toxic = True
                risk_factors.append("Suspicious anchor text")
            
            if is_toxic:
                toxic_links.append({
                    **link,
                    "risk_factors": risk_factors,
                    "risk_level": _calculate_risk_level(spam_score, da)
                })
        
        # Sort by risk
        toxic_links.sort(key=lambda x: x.get("source_spam_score", 0), reverse=True)
        
        # Generate disavow file
        disavow_content = _generate_disavow_file(toxic_links)
        
        print(f"   ⚠️ Found {len(toxic_links)} toxic backlinks")
        
        return {
            "success": True,
            "url": url,
            "toxic_count": len(toxic_links),
            "toxic_links": toxic_links,
            "risk_breakdown": {
                "critical": len([l for l in toxic_links if l["risk_level"] == "Critical"]),
                "high": len([l for l in toxic_links if l["risk_level"] == "High"]),
                "medium": len([l for l in toxic_links if l["risk_level"] == "Medium"])
            },
            "disavow_file": disavow_content,
            "threshold_used": threshold
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def analyze_toxic_pattern(toxic_links: List[Dict]) -> Dict:
    """
    Use AI to analyze patterns in toxic links
    
    Args:
        toxic_links: List of toxic link dicts
        
    Returns:
        Dict with pattern analysis
    """
    print("🔍 Analyzing toxic link patterns with AI...")
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    # Prepare data for AI
    sample = toxic_links[:20]  # First 20
    domains = [link.get("source_domain", "") for link in sample]
    anchors = [link.get("anchor_text", "") for link in sample]
    
    prompt = f"""Analyze these toxic backlinks and identify attack patterns.

Toxic Domains (sample):
{', '.join(domains[:15])}

Anchor Texts:
{', '.join([a for a in anchors if a][:15])}

Identify:
1. **Attack Type**: Is this negative SEO, spam network, or natural low-quality links?
2. **Common Patterns**: What do these links have in common?
3. **Severity**: How urgent is this issue (1-10)?
4. **Action Plan**: What should be done immediately?

Return as JSON:
{{
    "attack_type": "negative_seo" | "spam_network" | "natural_spam" | "mixed",
    "severity_score": 8,
    "common_patterns": ["pattern1", "pattern2"],
    "recommendations": ["action1", "action2"],
    "disavow_priority": "urgent" | "high" | "medium"
}}
"""
    
    try:
        response = gemini.generate_content(prompt)
        response_text = response.text.strip()
        
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        else:
            json_str = response_text
        
        import json
        result = json.loads(json_str)
        result["success"] = True
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _calculate_risk_level(spam_score: int, da: int) -> str:
    """Calculate risk level based on spam score and DA"""
    if spam_score >= 80 or (spam_score >= 60 and da < 10):
        return "Critical"
    elif spam_score >= 60 or (spam_score >= 40 and da < 20):
        return "High"
    elif spam_score >= 40:
        return "Medium"
    else:
        return "Low"


def _generate_disavow_file(toxic_links: List[Dict]) -> str:
    """
    Generate Google Disavow file content
    
    Format: https://support.google.com/webmasters/answer/2648487
    """
    lines = ["# Disavow file generated by AI SEO Audit Pro"]
    lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"# Total toxic links: {len(toxic_links)}")
    lines.append("")
    
    # Group by domain for efficiency
    domains = set()
    for link in toxic_links:
        domain = link.get("source_domain", "")
        if domain:
            domains.add(domain)
    
    # Add domains to disavow
    for domain in sorted(domains):
        lines.append(f"domain:{domain}")
    
    return "\n".join(lines)
