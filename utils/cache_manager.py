import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

class AuditCache:
    def __init__(self, cache_dir=".cache", ttl_hours=24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, url, niche):
        """Generate cache key from URL and niche"""
        key_string = f"{url}_{niche}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, url, niche):
        """Retrieve cached result if valid"""
        cache_file = self.cache_dir / f"{self._get_cache_key(url, niche)}.json"
        
        if not cache_file.exists():
            return None
        
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        # Check if cache is still valid
        cached_time = datetime.fromisoformat(data['timestamp'])
        if datetime.now() - cached_time > self.ttl:
            cache_file.unlink()  # Delete expired cache
            return None
        
        return data['result']
    
    def set(self, url, niche, result):
        """Store audit result in cache"""
        cache_file = self.cache_dir / f"{self._get_cache_key(url, niche)}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'niche': niche,
            'result': result
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)

# Global instance
audit_cache = AuditCache(ttl_hours=24)
