"""
JavaScript Rendering - Feature #1
Render JS-heavy pages using Playwright
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
from typing import Dict

def render_javascript_page(url: str, wait_time: int = 5) -> Dict:
    """
    Render JavaScript-heavy pages
    
    Args:
        url: URL to render
        wait_time: Seconds to wait for JS execution
        
    Returns:
        Dict with HTML content and metadata
    """
    
    print(f"Rendering JavaScript for: {url}")
    
    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create context with realistic headers
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = context.new_page()
            
            # Navigate and wait for network to be idle
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Additional wait for dynamic content
            time.sleep(wait_time)
            
            # Get rendered HTML
            html_content = page.content()
            
            # Get page title
            title = page.title()
            
            # Get final URL (in case of redirects)
            final_url = page.url
            
            # Check if page has JavaScript
            has_js = page.evaluate("() => document.scripts.length > 0")
            
            # Close browser
            browser.close()
            
            return {
                "success": True,
                "html": html_content,
                "title": title,
                "final_url": final_url,
                "has_javascript": has_js,
                "method": "playwright"
            }
            
    except PlaywrightTimeout:
        return {
            "success": False,
            "error": "Page load timeout (30s exceeded)",
            "method": "playwright"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "method": "playwright"
        }

def should_use_js_rendering(url: str) -> bool:
    """
    Determine if URL needs JavaScript rendering
    
    Common JS-heavy frameworks:
    - React, Vue, Angular SPAs
    - Next.js, Nuxt.js
    - Gatsby
    """
    
    js_indicators = [
        'app.js',
        'bundle.js',
        'react',
        'vue',
        'angular',
        'next',
        'gatsby'
    ]
    
    url_lower = url.lower()
    
    # Check if URL suggests JS framework
    return any(indicator in url_lower for indicator in js_indicators)
