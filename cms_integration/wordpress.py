import requests
import base64
from .base import BaseCMS

class WordPressCMS(BaseCMS):
    def __init__(self, url: str, user: str, app_pass: str, dry_run: bool = True):
        super().__init__(dry_run)
        self.url = f"{url.rstrip('/')}/wp-json/wp/v2"
        # Create Auth Token
        creds = f"{user}:{app_pass}"
        self.token = base64.b64encode(creds.encode()).decode()
        self.headers = {"Authorization": f"Basic {self.token}"}

    def get_post(self, post_id: int):
        # Try posts first, then pages
        r = requests.get(f"{self.url}/posts/{post_id}", headers=self.headers)
        if r.status_code == 404:
            r = requests.get(f"{self.url}/pages/{post_id}", headers=self.headers)
        return r.json() if r.status_code == 200 else None

    def update_seo(self, post_id: int, title: str, meta_desc: str):
        if self.dry_run:
            return {"status": "simulated", "msg": f"Would set Title: {title}"}

        # 1. Update Title (Standard WP)
        data = {"title": title}
        
        # 2. Update Meta Description (Yoast/RankMath specific fields)
        # Note: This often requires a custom meta field update depending on the plugin
        # We start with standard WP fields for safety.
        
        endpoint = f"{self.url}/posts/{post_id}"
        r = requests.post(endpoint, headers=self.headers, json=data)
        
        if r.status_code == 200:
            return {"status": "success", "new_title": title}
        return {"status": "error", "error": r.text}