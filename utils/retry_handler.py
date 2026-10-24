import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    """Retry failed API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check if it's a rate limit error
                    if 'rate limit' in error_msg or 'quota' in error_msg or '429' in error_msg:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            print(f"⚠️ Rate limit hit. Waiting {delay}s before retry {attempt + 1}/{max_retries}")
                            time.sleep(delay)
                            continue
                    
                    # If not rate limit or last attempt, raise the error
                    raise e
            
            return None
        return wrapper
    return decorator
