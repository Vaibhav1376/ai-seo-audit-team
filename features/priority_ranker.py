import os
import google.generativeai as genai
from typing import List, Dict

def rank_recommendations(recommendations: List[Dict], current_scores: Dict, niche: str) -> List[Dict]:
    """Rank recommendations by predicted impact using AI"""
    
    print("Ranking recommendations by AI-predicted impact...")
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name="gemini-2.5-flash-exp")
    
    prompt = f"""You are an SEO impact prediction model. Rank these recommendations by predicted traffic increase.

CURRENT STATE:
- Overall Score: {current_scores.get('overall_score', 0)}/100
- On-Page: {current_scores.get('onpage_score', 0)}/100
- Technical: {current_scores.get('technical_score', 0)}/100
- Content: {current_scores.get('content_score', 0)}/100
- Industry: {niche}

RECOMMENDATIONS:
{recommendations}

For each recommendation, predict:
1. Traffic impact: percentage increase (0-100%)
2. Implementation effort: hours needed
3. ROI score: impact / effort (0-100)
4. Quick win: true/false (high impact, low effort)
5. Priority: P0/P1/P2

Return as JSON array sorted by ROI score (highest first):
[
  {{
    "original_index": 0,
    "recommendation": "original text",
    "predicted_traffic_increase": 15,
    "effort_hours": 2,
    "roi_score": 85,
    "quick_win": true,
    "priority": "P0",
    "reasoning": "why this impact"
  }}
]"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        
        import json
        ranked = json.loads(text)
        
        return ranked
        
    except Exception as e:
        print(f"AI ranking failed: {e}")
        # Fallback: return original with default scores
        return [
            {**rec, "roi_score": 50, "quick_win": False}
            for rec in recommendations
        ]

def categorize_by_effort(recommendations: List[Dict]) -> Dict:
    """Categorize recommendations into quick wins vs long-term"""
    
    quick_wins = []
    long_term = []
    
    for rec in recommendations:
        if rec.get("quick_win") or rec.get("effort_hours", 999) < 4:
            quick_wins.append(rec)
        else:
            long_term.append(rec)
    
    return {
        "quick_wins": sorted(quick_wins, key=lambda x: x.get("roi_score", 0), reverse=True)[:5],
        "long_term": sorted(long_term, key=lambda x: x.get("predicted_traffic_increase", 0), reverse=True)
    }
