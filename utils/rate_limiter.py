import time
from functools import wraps
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.last_call = defaultdict(float)
        self.delays = {
            'gemini': 2.0,      # 2 seconds between Gemini calls
            'firecrawl': 1.5,   # 1.5 seconds between Firecrawl
            'google_search': 1.0 # 1 second between searches
        }
    
    def wait(self, api_name):
        """Enforce minimum delay between API calls"""
        now = time.time()
        elapsed = now - self.last_call[api_name]
        delay = self.delays.get(api_name, 1.0)
        
        if elapsed < delay:
            sleep_time = delay - elapsed
            time.sleep(sleep_time)
        
        self.last_call[api_name] = time.time()

# Global instance
rate_limiter = RateLimiter()

def rate_limit(api_name):
    """Decorator for rate limiting API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            rate_limiter.wait(api_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator
