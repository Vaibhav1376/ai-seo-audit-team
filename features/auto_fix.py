import requests
from typing import Dict, List
import os

class WordPressAutoFix:
    """Automated fixes for WordPress sites"""
    
    def __init__(self, site_url: str, wp_user: str, wp_app_password: str):
        self.site_url = site_url.rstrip('/')
        self.auth = (wp_user, wp_app_password)
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
    
    def update_post_meta(self, post_id: int, title: str = None, meta_description: str = None) -> Dict:
        """Update post title and meta description"""
        
        payload = {}
        
        if title:
            payload["title"] = title
        
        if meta_description:
            # Requires Yoast SEO plugin
            payload["yoast_head_json"] = {
                "description": meta_description
            }
        
        try:
            response = requests.post(
                f"{self.api_base}/posts/{post_id}",
                json=payload,
                auth=self.auth
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "Meta updated successfully"}
            
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_image_alt_text(self, image_id: int, alt_text: str) -> Dict:
        """Update image alt text"""
        
        try:
            response = requests.post(
                f"{self.api_base}/media/{image_id}",
                json={"alt_text": alt_text},
                auth=self.auth
            )
            
            if response.status_code == 200:
                return {"success": True, "message": f"Alt text updated for image {image_id}"}
            
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_internal_link(self, post_id: int, link_url: str, anchor_text: str, position: str = "end") -> Dict:
        """Add internal link to post content"""
        
        try:
            # Get current content
            response = requests.get(f"{self.api_base}/posts/{post_id}", auth=self.auth)
            post = response.json()
            
            content = post.get("content", {}).get("rendered", "")
            
            # Add link
            link_html = f'<a href="{link_url}">{anchor_text}</a>'
            
            if position == "end":
                new_content = content + f"<p>{link_html}</p>"
            else:
                # Add after first paragraph
                parts = content.split("</p>", 1)
                if len(parts) == 2:
                    new_content = f"{parts}</p><p>{link_html}</p>{parts}"[1]
                else:
                    new_content = content + f"<p>{link_html}</p>"
            
            # Update post
            update_response = requests.post(
                f"{self.api_base}/posts/{post_id}",
                json={"content": new_content},
                auth=self.auth
            )
            
            if update_response.status_code == 200:
                return {"success": True, "message": "Internal link added"}
            
            return {"success": False, "error": update_response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

class ShopifyAutoFix:
    """Automated fixes for Shopify stores"""
    
    def __init__(self, shop_url: str, access_token: str):
        self.shop_url = shop_url.rstrip('/')
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        self.api_base = f"{self.shop_url}/admin/api/2024-01"
    
    def update_product_meta(self, product_id: int, title: str = None, meta_description: str = None) -> Dict:
        """Update product SEO"""
        
        payload = {"product": {}}
        
        if title:
            payload["product"]["title"] = title
        
        if meta_description:
            payload["product"]["metafields_global_description_tag"] = meta_description
        
        try:
            response = requests.put(
                f"{self.api_base}/products/{product_id}.json",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "Product meta updated"}
            
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_image_alt(self, product_id: int, image_id: int, alt_text: str) -> Dict:
        """Update product image alt text"""
        
        try:
            response = requests.put(
                f"{self.api_base}/products/{product_id}/images/{image_id}.json",
                json={"image": {"alt": alt_text}},
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "Image alt text updated"}
            
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

def apply_fixes(platform: str, credentials: Dict, fixes: List[Dict]) -> List[Dict]:
    """Apply automated fixes"""
    
    results = []
    
    if platform == "wordpress":
        fixer = WordPressAutoFix(
            credentials["site_url"],
            credentials["wp_user"],
            credentials["wp_app_password"]
        )
        
        for fix in fixes:
            if fix["type"] == "meta":
                result = fixer.update_post_meta(
                    fix["post_id"],
                    fix.get("title"),
                    fix.get("meta_description")
                )
                results.append({**fix, "result": result})
            
            elif fix["type"] == "image_alt":
                result = fixer.update_image_alt_text(
                    fix["image_id"],
                    fix["alt_text"]
                )
                results.append({**fix, "result": result})
            
            elif fix["type"] == "internal_link":
                result = fixer.add_internal_link(
                    fix["post_id"],
                    fix["link_url"],
                    fix["anchor_text"]
                )
                results.append({**fix, "result": result})
    
    elif platform == "shopify":
        fixer = ShopifyAutoFix(
            credentials["shop_url"],
            credentials["access_token"]
        )
        
        for fix in fixes:
            if fix["type"] == "product_meta":
                result = fixer.update_product_meta(
                    fix["product_id"],
                    fix.get("title"),
                    fix.get("meta_description")
                )
                results.append({**fix, "result": result})
    
    return results
