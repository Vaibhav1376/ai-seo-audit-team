import requests
import base64
from typing import Dict, Any
from .base_connector import CMSConnector

class WordPressConnector(CMSConnector):
    def __init__(self, site_url: str, username: str, app_password: str, dry_run: bool = True):
        super().__init__({}, dry_run)
        self.base_url = f"{site_url.rstrip('/')}/wp-json/wp/v2"
        # Create Basic Auth Header
        creds = f"{username}:{app_password}"
        token = base64.b64encode(creds.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json"
        }

    def get_page_content(self, page_id: str) -> Dict:
        """Get current page data to prevent overwriting accidents"""
        try:
            # Check if it's a Post or Page
            response = requests.get(f"{self.base_url}/pages/{page_id}", headers=self.headers)
            if response.status_code == 404:
                 response = requests.get(f"{self.base_url}/posts/{page_id}", headers=self.headers)
            
            response.raise_for_status()
            data = response.json()
            return {
                "id": data['id'],
                "title": data['title']['rendered'],
                "content": data['content']['rendered'],
                "link": data['link']
            }
        except Exception as e:
            return {"error": str(e)}

    def update_meta_tags(self, page_id: str, title: str, description: str) -> Dict:
        """
        Updates SEO Title/Desc. 
        Note: Requires Yoast or RankMath REST API support.
        This generic version updates the standard WP Title.
        """
        if self.dry_run:
            return {"success": True, "mode": "DRY_RUN", "message": f"Would update title to: {title}"}

        payload = {
            "title": title,
            # For Yoast/RankMath, we would inject into their specific meta_keys here
            # "meta": { "_yoast_wpseo_metadesc": description } 
        }

        try:
            # Try updating as a Page first
            endpoint = f"{self.base_url}/pages/{page_id}"
            response = requests.post(endpoint, headers=self.headers, json=payload)
            
            if response.status_code == 404:
                endpoint = f"{self.base_url}/posts/{page_id}"
                response = requests.post(endpoint, headers=self.headers, json=payload)

            response.raise_for_status()
            return {"success": True, "new_title": title}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_content_html(self, page_id: str, new_html: str) -> Dict:
        """Injects optimized content directly into the CMS"""
        if self.dry_run:
            return {"success": True, "mode": "DRY_RUN", "message": "Content update simulated."}

        payload = {"content": new_html}
        
        try:
            response = requests.post(f"{self.base_url}/pages/{page_id}", headers=self.headers, json=payload)
            if response.status_code == 404:
                response = requests.post(f"{self.base_url}/posts/{page_id}", headers=self.headers, json=payload)
                
            response.raise_for_status()
            return {"success": True, "message": "Content updated automatically."}
        except Exception as e:
            return {"success": False, "error": str(e)}