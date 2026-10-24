import requests
from typing import Dict
import os
def check_mobile_friendly(url: str) -> Dict:
    """Check mobile-friendliness"""
    
    print("Checking mobile-friendliness...")
    
    # Basic checks from HTML
    mobile_score = 0
    issues = []
    
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        })
        html = response.text.lower()
        
        # Check viewport meta tag
        if 'viewport' in html and 'width=device-width' in html:
            mobile_score += 30
        else:
            issues.append("Missing or incorrect viewport meta tag")
        
        # Check responsive CSS
        if '@media' in html or 'responsive' in html:
            mobile_score += 20
        else:
            issues.append("No responsive CSS detected")
        
        # Check font size
        if 'font-size' in html:
            mobile_score += 15
        
        # Check touch targets
        if 'touch' in html or 'tap' in html:
            mobile_score += 15
        
        # Check mobile-friendly frameworks
        if any(fw in html for fw in ['bootstrap', 'tailwind', 'material', 'foundation']):
            mobile_score += 10
        
        # Default score if nothing found
        if mobile_score == 0:
            mobile_score = 40
            issues.append("Could not verify mobile optimization")
        
        return {
            "success": True,
            "mobile_score": min(mobile_score, 100),
            "has_viewport": 'viewport' in html,
            "has_responsive_css": '@media' in html,
            "issues": issues,
            "recommendations": generate_mobile_recommendations(issues)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "mobile_score": 0
        }

def generate_mobile_recommendations(issues: list) -> list:
    """Generate mobile optimization recommendations"""
    recommendations = []
    
    if "viewport" in str(issues):
        recommendations.append({
            "priority": "P0",
            "issue": "Missing viewport meta tag",
            "fix": 'Add <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            "impact": "Critical for mobile rendering"
        })
    
    if "responsive" in str(issues):
        recommendations.append({
            "priority": "P1",
            "issue": "No responsive CSS detected",
            "fix": "Use CSS media queries or responsive framework like Bootstrap/Tailwind",
            "impact": "Improves mobile UX significantly"
        })
    
    return recommendations

def check_with_google_api(url: str) -> Dict:
    """Check mobile-friendliness with Google API"""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return {"success": False, "error": "API key required"}
    
    try:
        endpoint = "https://searchconsole.googleapis.com/v1/urlTestingTools/mobileFriendlyTest:run"
        
        response = requests.post(
            f"{endpoint}?key={api_key}",
            json={"url": url},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                "success": True,
                "mobile_friendly": data.get("mobileFriendliness") == "MOBILE_FRIENDLY",
                "mobile_score": 100 if data.get("mobileFriendliness") == "MOBILE_FRIENDLY" else 30,
                "issues": data.get("mobileFriendlyIssues", [])
            }
        
        return {"success": False, "error": f"API error: {response.status_code}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
