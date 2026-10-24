from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseCMS(ABC):
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    @abstractmethod
    def get_post(self, post_id: int) -> Dict:
        pass

    @abstractmethod
    def update_seo(self, post_id: int, title: str, meta_desc: str) -> Dict:
        pass