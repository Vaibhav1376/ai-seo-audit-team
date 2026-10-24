"""
Competitor SEO Comparison
Audits your site + competitors side-by-side
"""
from typing import Dict, List


def compare_competitors(
    your_audit: Dict,
    competitor_audits: List[Dict]
) -> Dict:
    """
    Compare your site against competitors
    
    Args:
        your_audit: Your site's audit results
        competitor_audits: List of competitor audit results
        
    Returns:
        Comparison analysis
    """
    print(f"\n🎯 Comparing against {len(competitor_audits)} competitors...")
    
    all_sites = [your_audit] + competitor_audits
    
    # Extract scores
    comparison_table = []
    
    for i, audit in enumerate(all_sites):
        if not audit.get('success'):
            continue
            
        scores = audit.get('scores', {})
        audit_data = audit.get('audit_data', audit)
        
        comparison_table.append({
            'site': 'Your Site' if i == 0 else f'Competitor {i}',
            'url': audit.get('url', ''),
            'overall_score': scores.get('overall_score', 0),
            'on_page_score': scores.get('on_page_score', 0),
            'technical_score': scores.get('technical_score', 0),
            'content_score': scores.get('content_score', 0),
            'word_count': audit_data.get('word_count', 0),
            'has_schema': audit_data.get('has_schema', False),
            'has_canonical': audit_data.get('has_canonical', False),
            'primary_keyword': audit_data.get('primary_keyword', ''),
        })
    
    # Rankings
    your_rank = {
        'overall': get_rank(comparison_table, 'overall_score', 0),
        'on_page': get_rank(comparison_table, 'on_page_score', 0),
        'technical': get_rank(comparison_table, 'technical_score', 0),
        'content': get_rank(comparison_table, 'content_score', 0),
    }
    
    # Find strengths and weaknesses
    your_site = comparison_table[0]
    competitor_avg = calculate_average(comparison_table[1:])
    
    strengths = []
    weaknesses = []
    
    for metric in ['overall_score', 'on_page_score', 'technical_score', 'content_score']:
        your_value = your_site.get(metric, 0)
        avg_value = competitor_avg.get(metric, 0)
        
        if your_value > avg_value + 10:
            strengths.append({
                'metric': metric.replace('_', ' ').title(),
                'your_score': your_value,
                'competitor_avg': avg_value,
                'advantage': your_value - avg_value
            })
        elif your_value < avg_value - 10:
            weaknesses.append({
                'metric': metric.replace('_', ' ').title(),
                'your_score': your_value,
                'competitor_avg': avg_value,
                'gap': avg_value - your_value
            })
    
    # Content comparison
    your_word_count = your_site.get('word_count', 0)
    competitor_avg_words = int(sum(c.get('word_count', 0) for c in comparison_table[1:]) / len(competitor_audits))
    
    # Generate competitive insights
    insights = generate_competitive_insights(
        your_site,
        comparison_table[1:],
        strengths,
        weaknesses
    )
    
    return {
        "success": True,
        "comparison_table": comparison_table,
        "your_rankings": your_rank,
        "competitor_average": competitor_avg,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "content_comparison": {
            'your_word_count': your_word_count,
            'competitor_avg_word_count': competitor_avg_words,
            'gap': competitor_avg_words - your_word_count
        },
        "insights": insights,
        "competitive_score": calculate_competitive_score(your_rank)
    }


def get_rank(data: List[Dict], metric: str, your_index: int = 0) -> int:
    """Get ranking for specific metric"""
    sorted_data = sorted(data, key=lambda x: x.get(metric, 0), reverse=True)
    for rank, item in enumerate(sorted_data, 1):
        if item.get('site') == data[your_index].get('site'):
            return rank
    return len(data)


def calculate_average(competitors: List[Dict]) -> Dict:
    """Calculate average scores across competitors"""
    if not competitors:
        return {}
    
    metrics = ['overall_score', 'on_page_score', 'technical_score', 'content_score', 'word_count']
    averages = {}
    
    for metric in metrics:
        total = sum(c.get(metric, 0) for c in competitors)
        averages[metric] = int(total / len(competitors))
    
    return averages


def generate_competitive_insights(
    your_site: Dict,
    competitors: List[Dict],
    strengths: List,
    weaknesses: List
) -> List[Dict]:
    """Generate actionable competitive insights"""
    insights = []
    
    # Overall positioning
    your_overall = your_site.get('overall_score', 0)
    competitor_scores = [c.get('overall_score', 0) for c in competitors]
    avg_competitor = sum(competitor_scores) / len(competitors) if competitors else 0
    
    if your_overall > avg_competitor + 15:
        insights.append({
            'type': 'strength',
            'title': 'You are ahead of competitors',
            'description': f'Your score ({your_overall}) is significantly above average ({int(avg_competitor)})',
            'action': 'Maintain advantage and focus on content expansion'
        })
    elif your_overall < avg_competitor - 15:
        insights.append({
            'type': 'weakness',
            'title': 'You are behind competitors',
            'description': f'Your score ({your_overall}) is below average ({int(avg_competitor)})',
            'action': 'Priority fixes needed to catch up - focus on P0 issues'
        })
    else:
        insights.append({
            'type': 'neutral',
            'title': 'You are competitive with peers',
            'description': 'Scores are similar - differentiation needed',
            'action': 'Focus on unique content and technical excellence'
        })
    
    # Specific advantage opportunities
    if weaknesses:
        top_weakness = max(weaknesses, key=lambda x: x['gap'])
        insights.append({
            'type': 'opportunity',
            'title': f'Close the gap in {top_weakness["metric"]}',
            'description': f'Competitors average {top_weakness["competitor_avg"]}, you are at {top_weakness["your_score"]}',
            'action': f'Focus on improving {top_weakness["metric"]} to match competitors'
        })
    
    # Leverage strengths
    if strengths:
        top_strength = max(strengths, key=lambda x: x['advantage'])
        insights.append({
            'type': 'strength',
            'title': f'Leverage your {top_strength["metric"]} advantage',
            'description': f'You score {top_strength["your_score"]} vs competitor average {top_strength["competitor_avg"]}',
            'action': 'Emphasize this advantage in marketing and further optimize'
        })
    
    return insights


def calculate_competitive_score(rankings: Dict) -> int:
    """Calculate how competitive you are (0-100)"""
    total_competitors = 10  # Assume max 10 competitors
    
    # Average ranking across metrics
    avg_rank = sum(rankings.values()) / len(rankings)
    
    # Convert to score (1st place = 100, last = 0)
    score = int(((total_competitors - avg_rank + 1) / total_competitors) * 100)
    
    return max(0, min(100, score))
