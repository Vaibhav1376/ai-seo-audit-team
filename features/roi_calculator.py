"""
SEO ROI Calculator
Estimates business impact of SEO improvements
"""
from typing import Dict, List


def calculate_seo_roi(
    current_score: int,
    niche: str = 'general',
    monthly_traffic: int = None,
    avg_order_value: float = None
) -> Dict:
    """
    Calculate potential ROI from SEO improvements
    
    Args:
        current_score: Current overall SEO score
        niche: Industry niche
        monthly_traffic: Current monthly organic traffic (optional)
        avg_order_value: Average order/lead value (optional)
        
    Returns:
        Dict with ROI projections
    """
    print(f"  💰 Calculating SEO ROI for {niche} site (current score: {current_score})...")
    
    # Industry benchmarks
    benchmarks = {
        'ecommerce': {
            'traffic_per_point': 500,
            'conversion_rate': 0.02,
            'avg_order': 100,
            'avg_traffic': 10000,
        },
        'saas': {
            'traffic_per_point': 300,
            'conversion_rate': 0.05,
            'avg_order': 500,
            'avg_traffic': 5000,
        },
        'blog': {
            'traffic_per_point': 1000,
            'conversion_rate': 0.01,
            'avg_order': 50,
            'avg_traffic': 20000,
        },
        'local': {
            'traffic_per_point': 200,
            'conversion_rate': 0.08,
            'avg_order': 200,
            'avg_traffic': 3000,
        },
        'general': {
            'traffic_per_point': 400,
            'conversion_rate': 0.03,
            'avg_order': 150,
            'avg_traffic': 8000,
        }
    }
    
    data = benchmarks.get(niche, benchmarks['general'])
    
    # Use provided values or defaults
    current_traffic = monthly_traffic or data['avg_traffic']
    order_value = avg_order_value or data['avg_order']
    
    # Calculate improvement potential
    potential_improvement = 100 - current_score
    
    # Realistic improvement (not all gaps can be closed immediately)
    realistic_improvement = potential_improvement * 0.6  # 60% achievable
    
    # Traffic projections
    additional_traffic_monthly = int(realistic_improvement * data['traffic_per_point'])
    new_monthly_traffic = current_traffic + additional_traffic_monthly
    traffic_increase_percent = int((additional_traffic_monthly / current_traffic) * 100)
    
    # Conversion projections
    additional_conversions = int(additional_traffic_monthly * data['conversion_rate'])
    additional_revenue_monthly = additional_conversions * order_value
    additional_revenue_annual = additional_revenue_monthly * 12
    
    # Cost-benefit analysis
    typical_seo_investment = {
        'diy': 500,  # Just tools and time
        'freelancer': 2000,  # Monthly freelancer
        'agency': 5000,  # Monthly agency
    }
    
    roi_scenarios = {}
    for approach, cost in typical_seo_investment.items():
        months_to_break_even = cost / additional_revenue_monthly if additional_revenue_monthly > 0 else 999
        annual_roi = ((additional_revenue_annual - (cost * 12)) / (cost * 12)) * 100 if cost > 0 else 0
        
        roi_scenarios[approach] = {
            'monthly_investment': cost,
            'monthly_return': int(additional_revenue_monthly),
            'annual_return': int(additional_revenue_annual),
            'months_to_break_even': round(months_to_break_even, 1),
            'annual_roi_percent': int(annual_roi)
        }
    
    return {
        "success": True,
        "current_state": {
            "seo_score": current_score,
            "monthly_traffic": current_traffic,
            "estimated_monthly_revenue": int(current_traffic * data['conversion_rate'] * order_value)
        },
        "improvement_potential": {
            "score_gap": potential_improvement,
            "realistic_improvement": int(realistic_improvement),
            "additional_monthly_traffic": additional_traffic_monthly,
            "traffic_increase_percent": traffic_increase_percent,
            "new_monthly_traffic": new_monthly_traffic
        },
        "revenue_projections": {
            "additional_conversions_monthly": additional_conversions,
            "additional_revenue_monthly": int(additional_revenue_monthly),
            "additional_revenue_annual": int(additional_revenue_annual),
            "total_new_annual_revenue": int((current_traffic + additional_traffic_monthly) * data['conversion_rate'] * order_value * 12)
        },
        "roi_scenarios": roi_scenarios,
        "recommendations": generate_roi_recommendations(
            current_score,
            additional_revenue_monthly,
            roi_scenarios
        )
    }


def generate_roi_recommendations(
    current_score: int,
    monthly_return: float,
    scenarios: Dict
) -> List[Dict]:
    """Generate ROI-based recommendations"""
    recommendations = []
    
    if current_score < 50:
        recommendations.append({
            'title': 'High ROI opportunity - Low-hanging fruit',
            'description': f'With score of {current_score}, quick fixes can yield significant returns',
            'recommendation': 'Start with DIY or freelancer to address P0 issues',
            'expected_timeframe': '1-3 months to see results'
        })
    elif current_score < 70:
        recommendations.append({
            'title': 'Moderate ROI opportunity',
            'description': 'Solid foundation, but room for strategic improvements',
            'recommendation': 'Consider freelancer or small agency for technical and content work',
            'expected_timeframe': '3-6 months for significant gains'
        })
    else:
        recommendations.append({
            'title': 'Optimization phase - Diminishing returns',
            'description': 'Site is well-optimized; focus on advanced tactics',
            'recommendation': 'In-house or specialist for competitive edge',
            'expected_timeframe': '6-12 months for incremental gains'
        })
    
    # Best approach based on ROI
    best_approach = max(scenarios.items(), key=lambda x: x[1]['annual_roi_percent'])
    
    recommendations.append({
        'title': f'Best ROI approach: {best_approach[0].upper()}',
        'description': f"{best_approach[1]['annual_roi_percent']}% annual ROI",
        'monthly_investment': best_approach[1]['monthly_investment'],
        'expected_monthly_return': best_approach[1]['monthly_return'],
        'break_even': f"{best_approach[1]['months_to_break_even']} months"
    })
    
    return recommendations
