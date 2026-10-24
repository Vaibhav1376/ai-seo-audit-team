import os
import google.generativeai as genai
from typing import Dict, List
from .wordpress_api import WordPressConnector

class AutoFixEngine:
    def __init__(self, connector):
        self.connector = connector
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def fix_meta_description(self, page_id: str, current_content: str, keywords: List[str]) -> Dict:
        """
        1. AI reads the content.
        2. AI writes a perfect meta description.
        3. Connector pushes it to the site.
        """
        print(f"🤖 AI Generating Meta Description for Page ID: {page_id}...")
        
        # 1. Generate the Fix
        prompt = f"""
        Read this website content:
        {current_content[:2000]}...

        Target Keywords: {keywords}

        Write a SEO Meta Description (max 160 chars). 
        It must be catchy, include the keyword, and encourage clicks.
        Return ONLY the raw description text.
        """
        response = self.model.generate_content(prompt)
        new_description = response.text.strip().replace('"', '')

        # 2. Generate the Title (Bonus)
        title_prompt = f"Write a SEO Title Tag (max 60 chars) for the content above. Return ONLY text."
        new_title = self.model.generate_content(title_prompt).text.strip().replace('"', '')

        # 3. Push to CMS
        print(f"🚀 Pushing to CMS: {new_title}")
        result = self.connector.update_meta_tags(page_id, new_title, new_description)
        
        return {
            "action": "Meta Update",
            "generated_title": new_title,
            "generated_desc": new_description,
            "api_result": result
        }

    def fix_image_alt_tags(self, page_id: str, html_content: str) -> Dict:
        """
        Scans HTML for images without Alt tags, uses AI to describe them,
        and patches the HTML.
        """
        # This requires parsing HTML, finding <img> tags, 
        # generating alt text, and calling update_content_html
        # (Simplified for this snippet)
        pass