"""
Enhanced JavaScript Rendering Scraper
Handles complex JS sites that Firecrawl struggles with
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

def scrape_with_js_rendering(url: str, wait_time: int = 5) -> dict:
    """
    Scrape JS-heavy sites using Selenium with Chrome
    
    Args:
        url: URL to scrape
        wait_time: Seconds to wait for JS to load
        
    Returns:
        Dict with scraped content
    """
    print(f"🌐 Launching headless browser for {url}...")
    
    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Load page
        driver.get(url)
        
        # Wait for JS to execute
        time.sleep(wait_time)
        
        # Scroll to load lazy content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Get rendered HTML
        html = driver.page_source
        current_url = driver.current_url
        
        driver.quit()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract data
        title = soup.title.string if soup.title else ""
        
        meta_desc = ""
        meta_tag = soup.find("meta", {"name": "description"})
        if meta_tag:
            meta_desc = meta_tag.get("content", "")
        
        # Get all text
        text = soup.get_text(separator=' ', strip=True)
        
        # Count elements
        h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
        h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
        
        # Links
        internal_links = []
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith(('http://', 'https://')):
                if url.split('/')[2] in href:
                    internal_links.append(href)
                else:
                    external_links.append(href)
            elif href.startswith('/'):
                internal_links.append(href)
        
        word_count = len(text.split())
        
        print(f"✅ JS rendering complete: {word_count} words extracted")
        
        return {
            "success": True,
            "url": current_url,
            "title": title,
            "meta_description": meta_desc,
            "text": text,
            "html": html,
            "word_count": word_count,
            "h1_tags": h1_tags,
            "h2_h4_tags": h2_tags,
            "internal_links_count": len(set(internal_links)),
            "external_links_count": len(set(external_links)),
            "status_code": 200,
            "method": "selenium"
        }
        
    except Exception as e:
        print(f"❌ JS rendering failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url
        }
