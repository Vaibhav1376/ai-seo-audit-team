import os
import google.generativeai as genai
from typing import Dict, List

def generate_content_outline(keyword: str, serp_data: Dict, target_length: int = 2000) -> Dict:
    """Generate optimized content outline"""
    
    print(f"Generating content outline for: {keyword}")
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name="gemini-2.5-flash-exp")
    
    top_results = serp_data.get("serpdata", {}).get("top10_results", [])[:5]
    paa = serp_data.get("serpdata", {}).get("people_also_ask", [])
    
    prompt = f"""Create a comprehensive content outline for target keyword: "{keyword}"

TARGET:
- Length: ~{target_length} words
- Intent: {serp_data.get('analysis', {}).get('search_intent', 'informational')}

TOP SERP COMPETITORS:
{top_results}

PEOPLE ALSO ASK:
{paa}

Generate as JSON:
{{
  "title": "Optimized H1 Title (60 chars)",
  "meta_description": "Compelling meta (155 chars)",
  "introduction": {{
    "hook": "Opening sentence",
    "length": 150
  }},
  "sections": [
    {{
      "h2": "Section heading",
      "h3_subheadings": ["Sub 1", "Sub 2"],
      "key_points": ["Point 1", "Point 2"],
      "target_words": 300
    }}
  ],
  "conclusion": {{
    "summary": "Key takeaways",
    "cta": "Call to action"
  }},
  "internal_link_opportunities": ["Topic 1", "Topic 2"],
  "estimated_word_count": 2000
}}"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if "```json" in text:
            text = text.split("``````")[0].strip()
        
        import json
        outline = json.loads(text)
        
        return {
            "success": True,
            **outline
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def write_section(h2_title: str, key_points: List[str], target_words: int = 300) -> str:
    """Write a content section"""
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name="gemini-2.5-flash-exp")
    
    prompt = f"""Write a {target_words}-word section for:

H2: {h2_title}

Key points to cover:
{chr(10).join(f'- {p}' for p in key_points)}

Requirements:
- Natural, conversational tone
- Use short paragraphs (2-3 sentences)
- Include specific examples
- SEO-optimized but human-first
- {target_words} words

Return only the content (no markdown headers)."""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Error generating section: {e}]"

def generate_full_article(outline: Dict) -> str:
    """Generate full article from outline"""
    
    print("Writing full article...")
    
    article = f"# {outline['title']}\n\n"
    
    # Introduction
    article += f"{outline['introduction']['hook']}\n\n"
    
    # Sections
    for section in outline.get("sections", []):
        article += f"## {section['h2']}\n\n"
        
        content = write_section(
            section['h2'],
            section.get('key_points', []),
            section.get('target_words', 300)
        )
        
        article += f"{content}\n\n"
        
        # H3 subsections
        for h3 in section.get('h3_subheadings', []):
            article += f"### {h3}\n\n"
            
            sub_content = write_section(h3, [], 150)
            article += f"{sub_content}\n\n"
    
    # Conclusion
    article += f"## Conclusion\n\n"
    article += f"{outline['conclusion']['summary']}\n\n"
    article += f"{outline['conclusion']['cta']}\n"
    
    return article

def optimize_existing_content(content: str, target_keyword: str, improvements: List[str]) -> str:
    """Optimize existing content"""
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name="gemini-2.5-flash-exp")
    
    prompt = f"""Optimize this content for keyword "{target_keyword}"

CURRENT CONTENT:
{content[:3000]}

REQUIRED IMPROVEMENTS:
{chr(10).join(f'- {i}' for i in improvements)}

Rewrite to:
1. Naturally include target keyword 3-5 times
2. Address all improvement points
3. Keep original meaning and tone
4. Make it more comprehensive

Return optimized version:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return content  # Return original on error
