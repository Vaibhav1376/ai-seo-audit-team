import requests
from .base import BaseCMS

class ShopifyCMS(BaseCMS):
    def __init__(self, shop_url: str, access_token: str, dry_run: bool = True):
        super().__init__(dry_run)
        # Ensure URL is clean (e.g. "myshop.myshopify.com")
        self.shop_url = shop_url.replace("https://", "").replace("http://", "").rstrip("/")
        self.url = f"https://{self.shop_url}/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }

    def get_post(self, product_id: str):
        # Fetch Product
        try:
            r = requests.get(f"{self.url}/products/{product_id}.json", headers=self.headers)
            if r.status_code == 200:
                p = r.json().get('product', {})
                return {
                    "id": p.get('id'),
                    "title": p.get('title'),
                    "content": p.get('body_html'),
                    "link": f"https://{self.shop_url}/products/{p.get('handle')}"
                }
            return None
        except Exception as e:
            print(f"Shopify Error: {e}")
            return None

    def update_seo(self, product_id: str, title: str, meta_desc: str):
        if self.dry_run:
            return {"status": "simulated", "msg": f"[DRY RUN] Would set Shopify SEO Title: '{title}'"}
            
        payload = {
            "product": {
                "id": product_id,
                # Shopify stores SEO metadata in 'metafields_global_title_tag' or specific metafields
                # For standard products, it's often handled via the GraphQL API or metafields
                # This is a simplified implementation for the REST API
                "metafields_global_title_tag": title,
                "metafields_global_description_tag": meta_desc
            }
        }
        
        try:
            r = requests.put(f"{self.url}/products/{product_id}.json", headers=self.headers, json=payload)
            if r.status_code == 200:
                return {"status": "success", "new_title": title}
            return {"status": "error", "error": r.text}
        except Exception as e:
            return {"status": "error", "error": str(e)}