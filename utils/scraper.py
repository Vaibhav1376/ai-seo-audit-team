"""
Multi-scraper utility with fallback chain:
1. Firecrawl (best for modern sites)
2. ScraperAPI (best for JavaScript/anti-bot)
3. Apify (best for complex automation)
4. BeautifulSoup (free fallback)
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import os
import time
from features.js_renderer import render_javascript_page, should_use_js_rendering

# =============================================================================
# 1. FIRECRAWL SCRAPER (AI-powered markdown)
# =============================================================================

def scrape_with_firecrawl(url: str) -> Dict:
    """Firecrawl API - Best for clean markdown output"""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return {"success": False, "error": "Firecrawl API key not set"}
    
    try:
        endpoint = "https://api.firecrawl.dev/v0/scrape"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "formats": ["markdown", "html", "links"],
            "onlyMainContent": True,
            "timeout": 30000
        }
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            content = data.get("data", {})
            metadata = content.get("metadata", {})
            return {
                "success": True,
                "url": url,
                "title": metadata.get("title", ""),
                "meta_description": metadata.get("description", ""),
                "markdown": content.get("markdown", ""),
                "source": "firecrawl"
            }
        return {"success": False, "error": "Firecrawl scraping failed"}
    except Exception as e:
        return {"success": False, "error": f"Firecrawl: {str(e)}"}


# =============================================================================
# 2. SCRAPERAPI SCRAPER (Best for JavaScript & anti-bot)
# =============================================================================

def scrape_with_scraperapi(url: str) -> Dict:
    """ScraperAPI - Best for JavaScript-heavy and protected sites"""
    api_key = os.getenv("SCRAPERAPI_KEY")
    if not api_key:
        return {"success": False, "error": "ScraperAPI key not set"}
    
    try:
        # ScraperAPI endpoint
        endpoint = "http://api.scraperapi.com"
        params = {
            "api_key": api_key,
            "url": url,
            "render": "true",  # Enable JavaScript rendering
            "country_code": "us",  # Optional: set location
        }
        
        response = requests.get(endpoint, params=params, timeout=60)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc.get('content', '').strip() if meta_desc else ""
        
        # Get main content
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        text = soup.get_text()
        clean_text = ' '.join(text.split())
        
        return {
            "success": True,
            "url": url,
            "title": title_text,
            "meta_description": meta_description,
            "html": response.text,
            "text": clean_text,
            "word_count": len(clean_text.split()),
            "source": "scraperapi"
        }
    except Exception as e:
        return {"success": False, "error": f"ScraperAPI: {str(e)}"}


# =============================================================================
# 3. APIFY SCRAPER (Best for complex automation)
# =============================================================================

def scrape_with_apify(url: str) -> Dict:
    """Apify Web Scraper - Best for complex sites"""
    api_key = os.getenv("APIFY_API_TOKEN")
    if not api_key:
        return {"success": False, "error": "Apify API token not set"}
    
    try:
        # Run Apify Web Scraper actor
        endpoint = "https://api.apify.com/v2/acts/apify~web-scraper/run-sync-get-dataset-items"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "startUrls": [{"url": url}],
            "pageFunction": """
                async function pageFunction(context) {
                    const { page } = context;
                    return {
                        title: await page.title(),
                        text: await page.evaluate(() => document.body.innerText),
                        html: await page.content()
                    };
                }
            """,
            "maxConcurrency": 1,
        }
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            result = data[0]
            return {
                "success": True,
                "url": url,
                "title": result.get("title", ""),
                "text": result.get("text", ""),
                "html": result.get("html", ""),
                "word_count": len(result.get("text", "").split()),
                "source": "apify"
            }
        return {"success": False, "error": "Apify returned no data"}
    except Exception as e:
        return {"success": False, "error": f"Apify: {str(e)}"}


# =============================================================================
# 4. BEAUTIFULSOUP SCRAPER (Free fallback)
# =============================================================================

def scrape_with_beautifulsoup(url: str, timeout: int = 30) -> Dict:
    """BeautifulSoup - Free fallback scraper"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # Extract meta
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc.get('content', '').strip() if meta_desc else ""
        
        # Extract headings
        h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
        h2_h4_tags = []
        for tag in ['h2', 'h3', 'h4']:
            h2_h4_tags.extend([{'tag': tag, 'text': h.get_text().strip()} for h in soup.find_all(tag)])
        
        # Extract links
        all_links = soup.find_all('a', href=True)
        from urllib.parse import urlparse
        base_domain = urlparse(url).netloc
        internal_links = []
        external_links = []
        
        for link in all_links:
            href = link.get('href', '')
            if href.startswith('http'):
                if base_domain in urlparse(href).netloc:
                    internal_links.append(href)
                else:
                    external_links.append(href)
            elif href.startswith('/'):
                internal_links.append(href)
        
        # Extract text
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        text = soup.get_text()
        clean_text = ' '.join(text.split())
        
        # Check technical elements
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        schema_tags = soup.find_all('script', attrs={'type': 'application/ld+json'})
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        og_tags = soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')})
        
        return {
            "success": True,
            "url": url,
            "title": title_text,
            "title_length": len(title_text),
            "meta_description": meta_description,
            "meta_length": len(meta_description),
            "h1_tags": h1_tags,
            "h1_count": len(h1_tags),
            "h2_h4_tags": h2_h4_tags,
            "internal_links_count": len(internal_links),
            "external_links_count": len(external_links),
            "text": clean_text,
            "word_count": len(clean_text.split()),
            "has_canonical": canonical is not None,
            "has_schema": len(schema_tags) > 0,
            "is_indexable": 'noindex' not in (robots_meta.get('content', '').lower() if robots_meta else ""),
            "has_og_tags": len(og_tags) > 0,
            "source": "beautifulsoup"
        }
    except Exception as e:
        return {"success": False, "error": f"BeautifulSoup: {str(e)}", "url": url}
    
def scrape_with_requests(url: str, use_firecrawl: bool = True, force_js: bool = False) -> Dict:
    """Enhanced scraper with JS rendering fallback"""
    
    # Try Firecrawl first (if available)
    if use_firecrawl and os.getenv("FIRECRAWL_API_KEY"):
        result = scrape_with_firecrawl(url)
        if result.get("success"):
            return result
    
    # Check if JS rendering needed
    if force_js or should_use_js_rendering(url):
        print("🎭 Using Playwright for JavaScript rendering...")
        js_result = render_javascript_page(url)
        
        if js_result.get("success"):
            # Parse with BeautifulSoup
            soup = BeautifulSoup(js_result["html"], 'html.parser')
            
            return {
                "success": True,
                "html": js_result["html"],
                "soup": soup,
                "title": js_result["title"],
                "final_url": js_result["final_url"],
                "method": "playwright"
            }
    
    # Fallback to regular requests
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return {
            "success": True,
            "html": response.text,
            "soup": soup,
            "title": soup.title.string if soup.title else "",
            "final_url": response.url,
            "method": "requests"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "method": "requests"
        }

# =============================================================================
# SMART SCRAPER WITH FALLBACK CHAIN
# =============================================================================

def scrape_url(url: str, timeout: int = 30) -> Dict:
    """
    Smart scraper with 4-tier fallback:
    1. Firecrawl (if API key available)
    2. ScraperAPI (if API key available) 
    3. Apify (if API token available)
    4. BeautifulSoup (always available)
    
    Returns enhanced data with scores
    """
    
    # Try Firecrawl first (best for markdown)
    if os.getenv("FIRECRAWL_API_KEY"):
        print("  🔥 Trying Firecrawl...")
        result = scrape_with_firecrawl(url)
        if result.get("success"):
            return enhance_scraper_data(result, url)
        print(f"  ⚠️ Firecrawl failed: {result.get('error')}")
    
    # Try ScraperAPI second (best for JavaScript)
    if os.getenv("SCRAPERAPI_KEY"):
        print("  🤖 Trying ScraperAPI...")
        result = scrape_with_scraperapi(url)
        if result.get("success"):
            return enhance_scraper_data(result, url)
        print(f"  ⚠️ ScraperAPI failed: {result.get('error')}")
    
    # Try Apify third (best for complex sites)
    if os.getenv("APIFY_API_TOKEN"):
        print("  🕷️ Trying Apify...")
        result = scrape_with_apify(url)
        if result.get("success"):
            return enhance_scraper_data(result, url)
        print(f"  ⚠️ Apify failed: {result.get('error')}")
    
    # Fallback to BeautifulSoup (always works)
    print("  🌐 Using BeautifulSoup fallback...")
    result = scrape_with_beautifulsoup(url, timeout)
    
    if result.get("success"):
        return result  # BeautifulSoup already returns full data
    
    return result  # Return error


def enhance_scraper_data(scraper_result: Dict, url: str) -> Dict:
    """Enhance data from Firecrawl/ScraperAPI/Apify to match BeautifulSoup format"""
    
    # If it's already from BeautifulSoup, return as-is
    if scraper_result.get("source") == "beautifulsoup":
        return scraper_result
    
    # Parse text/markdown to extract more data
    text = scraper_result.get("text", "") or scraper_result.get("markdown", "")
    html = scraper_result.get("html", "")
    
    # Extract headings from markdown or HTML
    h1_tags = []
    h2_h4_tags = []
    
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
        for tag in ['h2', 'h3', 'h4']:
            h2_h4_tags.extend([{'tag': tag, 'text': h.get_text().strip()} for h in soup.find_all(tag)])
    elif text:
        # Parse from markdown
        for line in text.split('\n'):
            if line.startswith('# '):
                h1_tags.append(line.replace('# ', '').strip())
            elif line.startswith('## '):
                h2_h4_tags.append({'tag': 'h2', 'text': line.replace('## ', '').strip()})
    
    # Build enhanced result
    enhanced = {
        **scraper_result,
        "title_length": len(scraper_result.get("title", "")),
        "meta_length": len(scraper_result.get("meta_description", "")),
        "h1_tags": h1_tags,
        "h1_count": len(h1_tags),
        "h2_h4_tags": h2_h4_tags,
        "internal_links_count": text.count('](/') if text else 0,
        "external_links_count": text.count('](http') if text else 0,
        "has_canonical": True,  # Assume yes for modern sites
        "has_schema": False,
        "is_indexable": True,
        "has_og_tags": True,
    }
    
    # Calculate scores
    from config import SCORING_WEIGHTS
    scores = calculate_page_score(enhanced)
    enhanced["scores"] = scores
    
    return enhanced



def calculate_page_score(data: Dict) -> Dict:
    """Calculate SEO scores (same as before)"""
    from config import SCORING_WEIGHTS
    
    scores = {
        "on_page_score": 0,
        "technical_score": 0,
        "content_score": 0,
    }
    
    max_on_page = 0
    max_technical = 0
    max_content = 0
    
    # On-page scoring
    if data.get("title"):
        scores["on_page_score"] += SCORING_WEIGHTS["has_title"]
        max_on_page += SCORING_WEIGHTS["has_title"]
        if 50 <= data.get("title_length", 0) <= 60:
            scores["on_page_score"] += SCORING_WEIGHTS["title_length_optimal"]
        max_on_page += SCORING_WEIGHTS["title_length_optimal"]
    
    if data.get("meta_description"):
        scores["on_page_score"] += SCORING_WEIGHTS["has_meta_description"]
        max_on_page += SCORING_WEIGHTS["has_meta_description"]
        if 150 <= data.get("meta_length", 0) <= 160:
            scores["on_page_score"] += SCORING_WEIGHTS["meta_length_optimal"]
        max_on_page += SCORING_WEIGHTS["meta_length_optimal"]
    
    if data.get("h1_count", 0) > 0:
        scores["on_page_score"] += SCORING_WEIGHTS["has_h1"]
        max_on_page += SCORING_WEIGHTS["has_h1"]
        if data.get("h1_count") == 1:
            scores["on_page_score"] += SCORING_WEIGHTS["single_h1"]
        max_on_page += SCORING_WEIGHTS["single_h1"]
    
    if len(data.get("h2_h4_tags", [])) > 0:
        scores["on_page_score"] += SCORING_WEIGHTS["has_h2"]
        max_on_page += SCORING_WEIGHTS["has_h2"]
    
    # Technical scoring
    if data.get("has_canonical"):
        scores["technical_score"] += SCORING_WEIGHTS["has_canonical"]
    max_technical += SCORING_WEIGHTS["has_canonical"]
    
    if data.get("has_schema"):
        scores["technical_score"] += SCORING_WEIGHTS["has_schema"]
    max_technical += SCORING_WEIGHTS["has_schema"]
    
    if data.get("internal_links_count", 0) > 0:
        scores["technical_score"] += SCORING_WEIGHTS["internal_links"]
    max_technical += SCORING_WEIGHTS["internal_links"]
    
    if data.get("external_links_count", 0) > 0:
        scores["technical_score"] += SCORING_WEIGHTS["external_links"]
    max_technical += SCORING_WEIGHTS["external_links"]
    
    # Content scoring
    word_count = data.get("word_count", 0)
    if word_count >= 800:
        scores["content_score"] += SCORING_WEIGHTS["word_count_adequate"]
    max_content += SCORING_WEIGHTS["word_count_adequate"]
    
    # Normalize to 100
    scores["on_page_score"] = int((scores["on_page_score"] / max_on_page * 100)) if max_on_page > 0 else 0
    scores["technical_score"] = int((scores["technical_score"] / max_technical * 100)) if max_technical > 0 else 0
    scores["content_score"] = int((scores["content_score"] / max_content * 100)) if max_content > 0 else 0
    
    # Overall score
    scores["overall_score"] = int(
        (scores["on_page_score"] * 0.4 + 
         scores["technical_score"] * 0.3 + 
         scores["content_score"] * 0.3)
    )
    
    return scores
