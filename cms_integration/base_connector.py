from abc import ABC, abstractmethod
from typing import Dict, Any

class CMSConnector(ABC):
    """
    Abstract Base Class to ensure all connectors (WP, Shopify, Webflow)
    follow the exact same strict standards.
    """

    def __init__(self, credentials: Dict[str, str], dry_run: bool = True):
        self.credentials = credentials
        self.dry_run = dry_run  # Safety Switch

    @abstractmethod
    def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Fetch current state before touching anything"""
        pass

    @abstractmethod
    def update_meta_tags(self, page_id: str, title: str, description: str) -> bool:
        """Update SEO Title and Description"""
        pass

    @abstractmethod
    def update_content_html(self, page_id: str, html_content: str) -> bool:
        """Update the actual body content"""
        pass