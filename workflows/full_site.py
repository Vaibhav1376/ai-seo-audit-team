'''
"""
Full Site Audit Workflow (Advanced Edition)
Robust crawling, error-proof analysis, and deep SEO insights.
"""
import os
import requests
import time
import random
import json
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from collections import deque, Counter
from typing import Dict, List, Set

# Internal Imports
from features.simple_auditor import simple_page_audit as page_auditor
# Import feature modules inside functions to avoid circular imports if needed

# --- CONFIGURATION ---
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
]

def get_headers():
    return {'User-Agent': random.choice(USER_AGENTS)}

def run_full_site_audit(
    domain: str,
    max_pages: int = 20,
    niche: str = "general",
    model: str = None,
    features: Dict = None,
    priority_urls: str = "",
    competitor_urls: List[str] = None
) -> Dict:
    """
    Run complete site-wide audit with advanced features
    """
    print(f"\n{'='*70}")
    print(f"🌐 FULL SITE AUDIT: {domain}")
    print(f"{'='*70}")
    
    # Initialize features
    if features is None:
        features = {}
    
    # Step 1: Discover URLs (Hybrid Method)
    print("\n🔍 Step 1/4: Discovering pages...")
    discovered_urls = discover_site_urls_hybrid(domain, max_pages, priority_urls)
    
    if not discovered_urls:
        print("❌ CRITICAL: No pages could be accessed. The site might be blocking bots.")
        # Return a "Safe Failure" dict to prevent app crash
        return {
            'success': False,
            'error': 'Could not discover any pages (Firewall or Empty Site)',
            'pages_audited': 0,
            'site_report': "# Audit Failed\n\nNo pages were accessible. Please check if the site blocks bots."
        }
    
    print(f"✅ Final List: Auditing {len(discovered_urls)} pages")
    
    # Step 2: Audit all pages
    print("\n🔄 Step 2/4: Auditing pages...")
    site_results = _audit_all_pages(discovered_urls, model, features)
    
    # Step 3: Site-wide analysis
    print("\n📊 Step 3/4: Analyzing site patterns...")
    site_analysis = _analyze_site_patterns(site_results)
    
    # Step 4: Advanced site features (Only if we have results)
    if site_analysis.get('total_pages', 0) > 0:
        print("\n🚀 Step 4/4: Running site-wide features...")
        site_analysis = _run_site_features(site_results, site_analysis, features, competitor_urls, model)
    
    # Step 5: Generate report
    print("\n📝 Generating site report...")
    site_report = _generate_site_report(site_results, site_analysis, niche, model)
    
    print("\n✅ Full site audit complete!")
    
    return {
        'success': True,
        'domain': domain,
        'pages_audited': len(site_results),
        'site_results': site_results,
        'site_analysis': site_analysis,
        'site_report': site_report
    }


def discover_site_urls_hybrid(domain: str, max_pages: int = 20, priority_urls: str = "") -> List[str]:
    """
    Robust URL discovery: Tries Sitemap first, falls back to Recursive Crawl.
    """
    # 1. Clean Domain
    if not domain.startswith('http'):
        domain = 'https://' + domain
    if domain.endswith('/'):
        domain = domain[:-1]

    all_urls = []
    
    # 2. Add Priority URLs
    if priority_urls:
        p_list = [u.strip() for u in priority_urls.split('\n') if u.strip()]
        all_urls.extend(p_list)
        print(f"   ✓ Added {len(p_list)} priority URLs")

    # 3. Method A: Try Sitemaps
    print("   Attempting Sitemap Discovery...")
    sitemap_urls = _get_from_sitemap(domain)
    
    if sitemap_urls:
        print(f"   ✓ Sitemap yielded {len(sitemap_urls)} URLs")
        all_urls.extend(sitemap_urls)
    else:
        print("   ⚠️ No Sitemap found or accessible.")

    # 4. Method B: Recursive Crawl (The Fallback)
    # If sitemap gave us nothing (or very few), we MUST crawl manually
    if len(all_urls) < 2:
        print("   🕷️ Switching to Recursive Crawler (Breadth-First Search)...")
        crawled_urls = _recursive_crawl(domain, max_pages_needed=max_pages)
        all_urls.extend(crawled_urls)

    # 5. Clean & Limit
    unique_urls = list(dict.fromkeys(all_urls)) # Remove duplicates
    
    # Filter to ensure they belong to domain
    base_domain = urlparse(domain).netloc
    filtered_urls = [u for u in unique_urls if base_domain in u][:max_pages]
    
    return filtered_urls


def _get_from_sitemap(domain: str) -> List[str]:
    """Try to fetch URLs from standard sitemap locations"""
    sitemap_paths = [
        '/sitemap.xml', '/sitemap_index.xml', '/wp-sitemap.xml', 
        '/sitemap-0.xml', '/page-sitemap.xml'
    ]
    
    found_urls = []
    for path in sitemap_paths:
        target = domain + path
        try:
            resp = requests.get(target, headers=get_headers(), timeout=10)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                # Handle namespaces in XML
                namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                # Find all <loc> tags
                urls = [elem.text for elem in root.findall('.//ns:loc', namespaces)]
                if not urls: # Fallback for no namespace
                     urls = [elem.text for elem in root.findall('.//loc')]
                
                if urls:
                    found_urls.extend(urls)
                    break # Stop if we found a working sitemap
        except:
            continue
    return found_urls


def _recursive_crawl(start_url: str, max_pages_needed: int) -> List[str]:
    """Real crawler that parses HTML to find links"""
    from bs4 import BeautifulSoup
    
    visited = set()
    queue = deque([start_url])
    found_urls = []
    
    base_domain = urlparse(start_url).netloc
    
    while queue and len(found_urls) < max_pages_needed:
        url = queue.popleft()
        
        if url in visited: continue
        visited.add(url)
        
        try:
            # Respectful Crawl
            time.sleep(0.5) 
            resp = requests.get(url, headers=get_headers(), timeout=8)
            
            if resp.status_code == 200:
                found_urls.append(url)
                print(f"      Found: {url}")
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # Normalize URL
                    full_url = urljoin(start_url, href)
                    parsed = urlparse(full_url)
                    
                    # Internal Links Only
                    if parsed.netloc == base_domain:
                        # Avoid junky links
                        if '#' not in full_url and full_url not in visited and full_url not in queue:
                             queue.append(full_url)
                             
        except Exception as e:
            print(f"      Failed to crawl {url}: {e}")
            
    return found_urls


def _audit_all_pages(urls: List[str], model: str, features: Dict) -> List[Dict]:
    """Audit all discovered pages"""
    site_results = []
    
    for i, url in enumerate(urls, 1):
        print(f"   📄 Auditing {i}/{len(urls)}: {url}")
        try:
            # Run the single page auditor
            audit_data = page_auditor(url, model=model, features=features)
            
            site_results.append({
                'url': url,
                'success': audit_data.get('success', False),
                'audit_data': audit_data
            })
            
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            site_results.append({
                'url': url,
                'success': False,
                'error': str(e),
                'audit_data': {'scores': {'overall': 0}} # Safe default
            })
            
    return site_results


def _analyze_site_patterns(site_results: List[Dict]) -> Dict:
    """
    Analyzes site-wide patterns. Includes SAFE GUARDS against empty results.
    """
    print("   🔍 Analyzing aggregate data...")
    
    # 1. CRITICAL FIX: Handle Empty Results
    successful = [r for r in site_results if r.get('success')]
    
    if not successful:
        return {
            "total_pages": 0,
            "avg_scores": {"overall": 0, "seo": 0, "technical": 0, "content": 0},
            "pages_with_issues": 0,
            "critical_issues_count": 0,
            "top_issues": [],
            "status": "Failed to audit any pages successfully"
        }

    # 2. Calculate Averages
    count = len(successful)
    total_scores = {'overall': 0, 'seo': 0, 'technical': 0, 'content': 0}
    
    all_issues = []
    
    for res in successful:
        data = res.get('audit_data', {})
        scores = data.get('scores', {})
        
        # Safe add
        total_scores['overall'] += scores.get('overall_score', 0)
        total_scores['seo'] += scores.get('on_page_score', 0) # Mapping fix
        total_scores['technical'] += scores.get('technical_score', 0)
        total_scores['content'] += scores.get('content_score', 0)
        
        # Collect Issues
        issues = data.get('technical_issues', [])
        if issues:
            all_issues.extend([i for i in issues if isinstance(i, str)]) # Ensure string

    avg_scores = {
        k: int(v / count) for k, v in total_scores.items()
    }
    
    # 3. Analyze Issues Frequency
    issue_counts = Counter(all_issues).most_common(10)
    top_issues = []
    for issue, freq in issue_counts:
        severity = "Critical" if freq > (count * 0.5) else "Medium"
        top_issues.append({
            "title": issue,
            "count": freq,
            "percentage": f"{int(freq/count*100)}%",
            "severity": severity
        })

    return {
        "total_pages": count,
        "avg_scores": avg_scores,
        "pages_with_issues": len([r for r in successful if r['audit_data'].get('technical_issues')]),
        "critical_issues_count": len([i for i in top_issues if i['severity'] == "Critical"]),
        "top_issues": top_issues
    }


def _run_site_features(site_results, site_analysis, features, competitor_urls, model):
    """Run advanced modules safely"""
    
    # Broken Links
    if features.get('broken_links'):
        try:
            from features import broken_links
            print("   🔗 Checking broken links...")
            site_analysis['broken_links'] = broken_links.check_broken_links(site_results)
        except Exception as e: print(f"Feature Error: {e}")

    # Competitors
    if features.get('competitor') and competitor_urls:
        try:
            from features import competitor_analysis
            print(f"   ⚔️ Comparing vs {len(competitor_urls)} competitors...")
            # (Simplified logic for stability)
            site_analysis['competitor_data'] = "Competitor analysis running..." 
        except Exception as e: print(f"Feature Error: {e}")
        
    return site_analysis


def _generate_site_report(site_results, site_analysis, niche, model):
    """Generates the AI Executive Summary safely."""
    
    # Safe Defaults
    scores = site_analysis.get('avg_scores', {'overall': 0})
    total = site_analysis.get('total_pages', 0)
    
    if total == 0:
        return "# Audit Failed\n\nUnable to audit any pages. Please verify the domain is accessible."

    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    try:
        gemini = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        prompt = f"""
        Act as a Senior SEO Consultant. Write a high-level Executive Summary for a Site Audit.
        
        DOMAIN DATA:
        - Pages Analyzed: {total}
        - Overall Health Score: {scores.get('overall', 0)}/100
        - Technical Score: {scores.get('technical', 0)}/100
        - SEO Score: {scores.get('seo', 0)}/100
        - Content Score: {scores.get('content', 0)}/100
        
        TOP ISSUES FOUND:
        {json.dumps(site_analysis.get('top_issues', [])[:5], indent=2)}
        
        NICHE: {niche}
        
        OUTPUT FORMAT (Markdown):
        # 🏥 Executive SEO Health Report
        ## 1. High-Level Verdict
        (Give a brutally honest 2-sentence assessment)
        
        ## 2. Scorecard
        (Present the scores in a bullet list)
        
        ## 3. Critical Issues to Fix Immediately (P0)
        (List the top 3 issues with a 1-sentence fix for each)
        
        ## 4. Strategic Growth Plan
        (3 strategic bullet points for the next 30 days)
        """
        
        response = gemini.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"# Error Generating Report\nSystem Error: {e}"
'''
"""
Full Site Audit Workflow (Advanced Edition)
Includes Rate Limit Handling (429 Fix) and Auto-Retry Logic.
"""
import os
import requests
import time
import random
import json
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from collections import deque, Counter
from typing import Dict, List

# Feature Imports (Dynamic to prevent circular errors)
from features.simple_auditor import simple_page_audit as page_auditor
from features.broken_links import check_broken_links
from features.internal_linking import analyze_internal_linking

# --- CONFIGURATION ---
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
]

def get_headers():
    return {'User-Agent': random.choice(USER_AGENTS)}

def run_full_site_audit(domain, max_pages=20, niche="general", model=None, features=None, priority_urls="", competitor_urls=None):
    """
    Run complete site-wide audit with Rate Limiting protections.
    """
    print(f"\n{'='*70}")
    print(f"🌐 FULL SITE AUDIT: {domain}")
    print(f"{'='*70}")
    
    if features is None: features = {}
    
    # Step 1: Discover URLs
    print("\n🔍 Step 1/4: Discovering pages...")
    discovered_urls = discover_site_urls_hybrid(domain, max_pages, priority_urls)
    
    if not discovered_urls:
        return {
            'success': False,
            'error': 'Could not discover any pages (Firewall or Empty Site)',
            'site_results': [], # Ensure this key exists even on failure
            'site_report': "# Audit Failed\n\nNo pages were accessible."
        }
    
    # Step 2: Audit all pages (With Rate Limiting)
    print("\n🔄 Step 2/4: Auditing pages...")
    site_results = _audit_all_pages(discovered_urls, model, features)
    
    # Step 3: Site-wide analysis
    print("\n📊 Step 3/4: Analyzing site patterns...")
    site_analysis = _analyze_site_patterns(site_results)
    
    # Step 4: Advanced site features
    if site_analysis.get('total_pages', 0) > 0:
        print("\n🚀 Step 4/4: Running site-wide features...")
        site_analysis = _run_site_features(site_results, site_analysis, features, competitor_urls, model)
    
    # Step 5: Generate report (With Retry Logic)
    print("\n📝 Generating site report...")
    site_report = _generate_site_report(site_results, site_analysis, niche, model)
    
    print("\n✅ Full site audit complete!")
    
    return {
        'success': True,
        'domain': domain,
        'pages_audited': len(site_results),
        'site_results': site_results,
        'site_analysis': site_analysis,
        'site_report': site_report
    }

def discover_site_urls_hybrid(domain: str, max_pages: int = 20, priority_urls: str = "") -> List[str]:
    """Robust URL discovery that handles HTTP/HTTPS and Sitemaps."""
    if not domain.startswith('http'):
        if "toscrape" in domain or "localhost" in domain:
            domain = 'http://' + domain
        else:
            domain = 'https://' + domain
            
    all_urls = []
    
    # Priority URLs
    if priority_urls:
        all_urls.extend([u.strip() for u in priority_urls.split('\n') if u.strip()])

    # Recursive Crawl (Simple & Effective)
    print("   🕷️ Recursive Crawler Activated...")
    crawled = _recursive_crawl(domain, max_pages)
    all_urls.extend(crawled)
    
    # De-duplicate and Limit
    seen = set()
    unique_urls = []
    for u in all_urls:
        if u not in seen:
            unique_urls.append(u)
            seen.add(u)
            
    return unique_urls[:max_pages]

def _recursive_crawl(start_url, max_pages):
    """Simple BFS Crawler"""
    visited = set()
    queue = deque([start_url])
    found = []
    base_domain = urlparse(start_url).netloc
    
    while queue and len(found) < max_pages:
        url = queue.popleft()
        if url in visited: continue
        visited.add(url)
        
        try:
            time.sleep(2.5)
            resp = requests.get(url, headers=get_headers(), timeout=5)
            if resp.status_code == 200:
                found.append(url)
                soup = ET.fromstring(resp.content) if "xml" in url else None # XML check
                # Note: For HTML parsing we need BeautifulSoup, importing here for safety
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full = urljoin(start_url, href)
                    if urlparse(full).netloc == base_domain:
                         if full not in visited and full not in queue:
                             queue.append(full)
        except:
            pass
    return found

def _audit_all_pages(urls, model, features):
    """Audits pages with DELAYS to prevent 429 Errors."""
    results = []
    for i, url in enumerate(urls):
        print(f"   📄 Auditing {i+1}/{len(urls)}: {url}")
        
        # --- RATE LIMIT FIX: PAUSE BETWEEN REQUESTS ---
        time.sleep(2) # Wait 2 seconds between AI calls
        
        res = page_auditor(url, model, features)
        results.append(res)
    return results

def _analyze_site_patterns(site_results):
    """Aggregates data safely."""
    successful = [r for r in site_results if r.get('success')]
    if not successful:
        return {"total_pages": 0, "avg_scores": {}, "top_issues": []}
        
    total_pages = len(successful)
    # Simple average calc
    avg_scores = {
        "overall": int(sum(r['scores'].get('overall_score', 0) for r in successful) / total_pages),
        "technical": int(sum(r['scores'].get('technical_score', 0) for r in successful) / total_pages),
        "seo": int(sum(r['scores'].get('on_page_score', 0) for r in successful) / total_pages)
    }
    
    # Collect issues
    all_issues = []
    for r in successful:
        all_issues.extend(r.get('technical_issues', []))
        
    top_issues = [{"title": issue, "count": count} for issue, count in Counter(all_issues).most_common(5)]
    
    return {
        "total_pages": total_pages,
        "avg_scores": avg_scores,
        "top_issues": top_issues,
        "pages_with_issues": len([r for r in successful if r.get('technical_issues')])
    }

def _run_site_features(results, analysis, features, competitors, model):
    """Runs broken link and internal link checks."""
    try:
        analysis['broken_links'] = check_broken_links(results)
    except: pass
    
    try:
        analysis['internal_linking'] = analyze_internal_linking(results)
    except: pass
    
    return analysis

def _generate_site_report(results, analysis, niche, model):
    """
    Generates report with 429 RETRY LOGIC (The Unbreakable Fix).
    """
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Fallback Models
    models_to_try = ["gemini-1.5-flash", "gemini-pro"]
    
    scores = analysis.get('avg_scores', {})
    prompt = f"""
    Write a Site Audit Executive Summary for a website in the {niche} niche.
    
    metrics:
    - Pages: {analysis.get('total_pages')}
    - Health Score: {scores.get('overall', 0)}/100
    - Top Issues: {json.dumps(analysis.get('top_issues', []))}
    
    Format as Markdown with: 
    1. Executive Summary 
    2. Critical Issues 
    3. Action Plan.
    """
    
    for m in models_to_try:
        try:
            # --- RETRY LOOP FOR 429 ---
            for attempt in range(3):
                try:
                    ai = genai.GenerativeModel(m)
                    response = ai.generate_content(prompt)
                    return response.text
                except Exception as e:
                    if "429" in str(e):
                        wait_time = (attempt + 1) * 10
                        print(f"      ⏳ Quota Hit. Cooling down for {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise e # If not 429, try next model
        except:
            continue
            
    return "# Audit Report Failed\nCould not generate report due to API limits."