"""
AI-Powered Topic Clustering
Groups content into semantic topics using Gemini
"""
import google.generativeai as genai
import os
import json

def cluster_topics(text: str, url: str, model: str = "gemini-1.5-flash") -> dict:
    """
    Analyze content and identify main topics
    
    Args:
        text: Full page text content
        url: Page URL for context
        model: Gemini model to use
        
    Returns:
        Dict with topic clusters
    """
    print("🧠 Clustering topics with AI...")
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini = genai.GenerativeModel(model_name=model)
    
    prompt = f"""Analyze this webpage content and identify the main topic clusters.

URL: {url}

CONTENT (first 3000 chars):
{text[:3000]}...

Your task:
1. Identify 3-5 MAIN TOPICS covered on this page
2. For each topic, list 3-5 related keywords
3. Determine the PRIMARY topic (most dominant)
4. Suggest 2-3 MISSING topics that would improve completeness

Return as JSON:
{{
    "primary_topic": "Main topic name",
    "topics": [
        {{
            "name": "Topic 1",
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "coverage_percentage": 40,
            "depth_score": 8
        }},
        {{
            "name": "Topic 2",
            "keywords": ["keyword1", "keyword2"],
            "coverage_percentage": 30,
            "depth_score": 6
        }}
    ],
    "missing_topics": [
        "Suggested topic 1",
        "Suggested topic 2"
    ],
    "content_focus": "focused" or "scattered",
    "recommendation": "Brief recommendation for improving topic coverage"
}}
"""
    
    try:
        response = gemini.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean JSON
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text
        
        result = json.loads(json_str)
        result["success"] = True
        
        print(f"✅ Found {len(result.get('topics', []))} topic clusters")
        return result
        
    except Exception as e:
        print(f"❌ Topic clustering failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "primary_topic": "Unknown",
            "topics": []
        }
