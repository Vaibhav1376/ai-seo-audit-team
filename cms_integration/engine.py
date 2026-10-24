import google.generativeai as genai
import os
from .wordpress import WordPressCMS

class AutoPilot:
    def __init__(self, cms_connector):
        self.cms = cms_connector
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def fix_meta_tags(self, post_id: int):
        # 1. Read Content
        post = self.cms.get_post(post_id)
        if not post: return {"error": "Post not found"}
        
        content_sample = post['content']['rendered'][:3000] # Read first 3000 chars

        # 2. Generate Optimization
        prompt = f"""
        Read this content: {content_sample}...
        
        Write a SEO Title (max 60 chars) and Meta Description (max 155 chars).
        Format: JSON {{ "title": "...", "meta": "..." }}
        """
        response = self.model.generate_content(prompt)
        # (Add JSON parsing logic here like in your agents)
        # Assume we got `new_data` dictionary
        
        # 3. Push Fix
        # For now, let's assume we parsed it into new_data['title']
        result = self.cms.update_seo(post_id, "Optimized Title by AI", "Optimized Meta Description")
        return result