import os
import google.generativeai as genai
from typing import Dict, List
from config import AGENT_CONFIG

def analyze_content_gaps(auditdata: Dict, serpdata: Dict, model: str = None) -> Dict:
    """Analyze content gaps vs competitors"""
    
    print("="*70)
    print("CONTENT GAP ANALYSIS")
    print("="*70)
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model_name = model or os.getenv("SELECTED_MODEL", AGENT_CONFIG["model"])
    gemini_model = genai.GenerativeModel(model_name=model_name)
    
    # Your content
    your_h2s = [h.get("text", "") for h in auditdata.get("h2h4_tags", [])]
    your_wordcount = auditdata.get("wordcount", 0)
    
    # Competitor content (from SERP)
    top10 = serpdata.get("serpdata", {}).get("top10_results", [])
    
    prompt = f"""Compare this page's content vs top SERP competitors:

YOUR PAGE:
- Word count: {your_wordcount}
- H2 headings: {your_h2s[:10]}

TOP COMPETITORS:
{top10[:3]}

Identify as JSON:
{{
  "word_count_gap": -500 (negative means you have less),
  "missing_topics": ["topic1", "topic2"],
  "content_depth_score": 0-100,
  "recommended_h2s": ["New H2 #1", "New H2 #2"],
  "competitive_advantage": "what you do better",
  "improvement_priority": "P0/P1/P2"
}}"""
    
    try:
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        
        import json
        gaps = json.loads(text)
        
        print(f"✅ Found {len(gaps.get('missing_topics', []))} content gaps")
        
        return {
            "success": True,
            **gaps
        }
        
    except Exception as e:
        print(f"Content gap analysis failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
