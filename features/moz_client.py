"""
Moz API Client
Handles authentication and API calls to Moz
"""
import os
import time
import hmac
import hashlib
import base64
import requests
from urllib.parse import quote
from typing import Dict, List

MOZ_ACCESS_ID = os.getenv("MOZ_ACCESS_ID")
MOZ_SECRET_KEY = os.getenv("MOZ_SECRET_KEY")
MOZ_API_ENDPOINT = "https://lsapi.seomoz.com/v2/url_metrics"
MOZ_LINKS_ENDPOINT = "https://lsapi.seomoz.com/v2/links"

class MozAPI:
    """Moz API wrapper"""
    
    def __init__(self, access_id: str = None, secret_key: str = None):
        self.access_id = access_id or MOZ_ACCESS_ID
        self.secret_key = secret_key or MOZ_SECRET_KEY
        
        if not self.access_id or not self.secret_key:
            raise ValueError("Moz API credentials not found in environment")
    
    def _create_auth_header(self) -> str:
        """Create authentication header for Moz API"""
        expires = str(int(time.time()) + 300)  # 5 minutes from now
        
        string_to_sign = f"{self.access_id}\n{expires}"
        
        # Create signature
        binary_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        signature = base64.b64encode(binary_signature).decode('utf-8')
        
        auth_header = f"Basic {base64.b64encode(f'{self.access_id}:{signature}'.encode()).decode()}"
        
        return auth_header
    
    def get_url_metrics(self, url: str) -> Dict:
        """
        Get metrics for a single URL
        
        Args:
            url: URL to check
            
        Returns:
            Dict with DA, PA, spam score, etc.
        """
        headers = {
            "Authorization": self._create_auth_header(),
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                MOZ_API_ENDPOINT,
                headers=headers,
                json={"targets": [url]},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("results") and len(data["results"]) > 0:
                    result = data["results"][0]
                    
                    return {
                        "success": True,
                        "url": url,
                        "domain_authority": result.get("domain_authority", 0),
                        "page_authority": result.get("page_authority", 0),
                        "spam_score": result.get("spam_score", 0),
                        "root_domains_to_root_domain": result.get("root_domains_to_root_domain", 0),
                        "external_pages_to_root_domain": result.get("external_pages_to_root_domain", 0),
                        "last_crawled": result.get("last_crawled"),
                        "http_status_code": result.get("http_status_code", 0)
                    }
            
            return {
                "success": False,
                "error": f"API error: {response.status_code}",
                "message": response.text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_linking_domains(self, url: str, limit: int = 50) -> Dict:
        """
        Get domains linking to this URL
        
        Args:
            url: Target URL
            limit: Max number of domains to return
            
        Returns:
            Dict with linking domains data
        """
        headers = {
            "Authorization": self._create_auth_header(),
            "Content-Type": "application/json"
        }
        
        payload = {
            "target": url,
            "scope": "page",
            "limit": limit,
            "filter": "external"
        }
        
        try:
            response = requests.post(
                f"{MOZ_LINKS_ENDPOINT}/linking_domains",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "success": True,
                    "url": url,
                    "total_linking_domains": len(data.get("results", [])),
                    "linking_domains": data.get("results", []),
                    "next_token": data.get("next_token")
                }
            
            return {
                "success": False,
                "error": f"API error: {response.status_code}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_backlinks(self, url: str, limit: int = 100) -> Dict:
        """
        Get backlinks to a URL
        
        Args:
            url: Target URL
            limit: Max backlinks to return
            
        Returns:
            Dict with backlink data
        """
        headers = {
            "Authorization": self._create_auth_header(),
            "Content-Type": "application/json"
        }
        
        payload = {
            "target": url,
            "scope": "page",
            "limit": limit,
            "filter": "external"
        }
        
        try:
            response = requests.post(
                f"{MOZ_LINKS_ENDPOINT}/links",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "success": True,
                    "url": url,
                    "total_backlinks": len(data.get("results", [])),
                    "backlinks": data.get("results", []),
                    "next_token": data.get("next_token")
                }
            
            return {
                "success": False,
                "error": f"API error: {response.status_code}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
