"""
Keyword Cannibalization Detector
Finds pages competing for the same keywords
"""
from typing import Dict, List
from collections import defaultdict


def detect_cannibalization(audit_results: List[Dict]) -> Dict:
    """
    Detect keyword cannibalization across multiple pages
    
    Args:
        audit_results: List of audit results from multiple pages
        
    Returns:
        Dict with cannibalization analysis
    """
    print(f"\n🔍 Detecting keyword cannibalization across {len(audit_results)} pages...")
    
    keyword_map = defaultdict(list)
    
    # Map keywords to URLs
    for result in audit_results:
        if result.get('success'):
            audit_data = result.get('audit_data', {})
            
            # Primary keyword
            primary_kw = audit_data.get('primary_keyword', '').lower().strip()
            if primary_kw and primary_kw != 'website optimization':
                keyword_map[primary_kw].append({
                    'url': result['url'],
                    'type': 'primary',
                    'score': audit_data.get('scores', {}).get('overall_score', 0),
                    'word_count': audit_data.get('word_count', 0)
                })
            
            # Secondary keywords
            secondary_kws = audit_data.get('secondary_keywords', [])
            for kw in secondary_kws:
                kw_clean = kw.lower().strip()
                if kw_clean:
                    keyword_map[kw_clean].append({
                        'url': result['url'],
                        'type': 'secondary',
                        'score': audit_data.get('scores', {}).get('overall_score', 0),
                        'word_count': audit_data.get('word_count', 0)
                    })
    
    # Find cannibalization (keywords with multiple pages)
    cannibalization_issues = []
    
    for keyword, pages in keyword_map.items():
        if len(pages) > 1:
            # Check if multiple pages are PRIMARILY targeting this keyword
            primary_pages = [p for p in pages if p['type'] == 'primary']
            
            if len(primary_pages) > 1:
                # Sort by score to find the "winner"
                sorted_pages = sorted(primary_pages, key=lambda x: x['score'], reverse=True)
                
                cannibalization_issues.append({
                    'keyword': keyword,
                    'severity': 'High' if len(primary_pages) > 2 else 'Medium',
                    'pages_competing': len(primary_pages),
                    'pages': sorted_pages,
                    'recommended_winner': sorted_pages[0]['url'],
                    'recommended_action': 'consolidate' if len(primary_pages) > 3 else 'differentiate',
                    'explanation': f"{len(primary_pages)} pages competing for '{keyword}'"
                })
    
    # Generate recommendations
    recommendations = generate_cannibalization_recommendations(cannibalization_issues)
    
    # Calculate score
    cannibalization_score = calculate_cannibalization_score(
        len(cannibalization_issues),
        len(audit_results)
    )
    
    return {
        "success": True,
        "total_pages_analyzed": len(audit_results),
        "unique_keywords": len(keyword_map),
        "cannibalization_issues": len(cannibalization_issues),
        "issues": sorted(cannibalization_issues, key=lambda x: x['pages_competing'], reverse=True),
        "recommendations": recommendations,
        "cannibalization_score": cannibalization_score
    }


def generate_cannibalization_recommendations(issues: List[Dict]) -> List[Dict]:
    """Generate actionable recommendations for cannibalization issues"""
    recommendations = []
    
    if not issues:
        return [{
            'title': 'No keyword cannibalization detected',
            'description': 'Each page targets unique keywords - good job!'
        }]
    
    high_severity = [i for i in issues if i['severity'] == 'High']
    medium_severity = [i for i in issues if i['severity'] == 'Medium']
    
    if high_severity:
        recommendations.append({
            'priority': 'P0',
            'title': f'{len(high_severity)} high-severity cannibalization issues',
            'description': 'Multiple pages strongly competing for same keywords',
            'action': 'Consolidate or significantly differentiate these pages',
            'issues': high_severity[:5]
        })
    
    if medium_severity:
        recommendations.append({
            'priority': 'P1',
            'title': f'{len(medium_severity)} medium-severity cannibalization issues',
            'description': 'Some keyword overlap detected',
            'action': 'Differentiate keyword focus or consolidate content',
            'issues': medium_severity[:5]
        })
    
    # Add specific recommendations
    for issue in issues[:3]:  # Top 3
        if issue['recommended_action'] == 'consolidate':
            recommendations.append({
                'priority': 'P0',
                'title': f"Consolidate pages for '{issue['keyword']}'",
                'description': f"{issue['pages_competing']} pages found - pick strongest and redirect others",
                'winner': issue['recommended_winner'],
                'pages_to_consolidate': [p['url'] for p in issue['pages'][1:]]
            })
        else:
            recommendations.append({
                'priority': 'P1',
                'title': f"Differentiate pages for '{issue['keyword']}'",
                'description': 'Modify content to target different long-tail variations',
                'pages': [p['url'] for p in issue['pages']]
            })
    
    return recommendations


def calculate_cannibalization_score(issues_count: int, total_pages: int) -> int:
    """Calculate how well the site avoids cannibalization (0-100)"""
    if total_pages == 0:
        return 100
    
    # Percentage of pages with cannibalization
    issue_rate = issues_count / total_pages
    
    if issue_rate == 0:
        return 100
    elif issue_rate < 0.1:  # Less than 10%
        return 90
    elif issue_rate < 0.2:
        return 75
    elif issue_rate < 0.3:
        return 60
    elif issue_rate < 0.5:
        return 40
    else:
        return 20
