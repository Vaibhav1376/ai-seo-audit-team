import os
import google.generativeai as genai
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Load Env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    print("❌ ERROR: GOOGLE_API_KEY missing in content_intelligence.py")

def analyze_serp_competition(keyword, country="us"):
    """
    Analyzes Top 10 Google Results for content gaps using Gemini.
    """
    print(f"🧠 Analyzing competition for: {keyword}")
    
    serp_key = os.getenv("SERPAPI_KEY")
    if not serp_key:
        return {"success": False, "error": "Missing SERPAPI_KEY in .env"}

    try:
        # 1. Get Real Google Results
        params = {
            "engine": "google",
            "q": keyword,
            "api_key": serp_key,
            "gl": country,
            "num": 10
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        organic = results.get("organic_results", [])

        if not organic:
            return {"success": False, "error": "No search results found to analyze."}

        # 2. Prepare Data for AI
        competitors_text = ""
        for i, res in enumerate(organic[:5], 1):
            competitors_text += f"{i}. {res.get('title')} - {res.get('link')}\n   Snippet: {res.get('snippet')}\n\n"

        # 3. Ask Gemini (Using Stable Model)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        prompt = f"""
        I want to rank for the keyword: "{keyword}".
        Here are the current top 5 competitors on Google:
        
        {competitors_text}
        
        Analyze these results and tell me:
        1. What is the search intent? (Informational, Transactional, etc.)
        2. What are 3 things these competitors are missing? (Content Gaps). Focus on "Actionability" vs "Density".
        3. Write 5 "Hooky" Titles that uses Numbers or Brackets to improve CTR.
        
        Format the output in clean Markdown.
        """
        
        response = model.generate_content(prompt)
        return {"success": True, "analysis": response.text, "competitors": organic[:5]}

    except Exception as e:
        print(f"Error in analyze_serp_competition: {e}")
        return {"success": False, "error": str(e)}

def generate_content_outline(topic, tone="Professional"):
    """
    Generates a High-Authority SEO outline with Data Hooks.
    """
    if not api_key:
        return "Error: GOOGLE_API_KEY is missing. Please check your .env file."

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # --- THE UPGRADED PROMPT ---
        prompt = f"""
        Act as an expert Market Analyst and SEO Copywriter.
        Create a "Skyscraper" blog post outline for the topic: "{topic}".
        Tone: {tone}
        
        CRITICAL INSTRUCTIONS:
        1. **Beat the Giants:** The competitors are boring government reports. Your goal is "Simplicity & Actionability".
        2. **Data Hooks:** Do NOT use generic headers like "Rising Solar Trends". Use specific hooks like "Why Solar Costs Will Drop 15% in 2025" or "The $2 Trillion Shift".
        3. **Tech Focus:** Explicitly include a section on AI, Digitalization, or 'Smart' tech if relevant.
        4. **User-Centric:** Add a "Why This Matters to You" bullet in every section (Consumer Impact).
        
        The outline must include:
        - **H1 Title:** Must be catchy and promise value.
        - **Executive Summary:** A 3-bullet snapshot for busy readers.
        - **H2 Headers (Trends):** Use powerful, active language.
        - **H3 Subheaders:** Specific details.
        - **Data Placeholders:** [Insert Stat about X] - tell the writer exactly what data to find.
        - **Estimated Word Count**
        
        Format in Markdown.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating outline: {e}"