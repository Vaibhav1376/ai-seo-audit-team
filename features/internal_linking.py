'''
from typing import Dict, List
from collections import defaultdict
import networkx as nx

def analyze_internal_linking(site_results: List[Dict]) -> Dict:
    """Analyze internal link structure across site"""
    
    print("Analyzing internal link structure...")
    
    # Build site graph
    G = nx.DiGraph()
    
    url_to_data = {}
    
    for result in site_results:
        if not result.get("success"):
            continue
        
        url = result.get("url")
        audit = result.get("auditdata", {})
        
        url_to_data[url] = audit
        
        # Add node
        G.add_node(url, 
            title=audit.get("title", ""),
            score=audit.get("scores", {}).get("overall_score", 0)
        )
        
        # Add edges for internal links
        internal_links = audit.get("internal_links", [])
        for link in internal_links:
            if link in url_to_data:
                G.add_edge(url, link)
    
    # Analyze graph
    analysis = {
        "total_pages": len(G.nodes()),
        "total_internal_links": len(G.edges()),
        "avg_links_per_page": len(G.edges()) / max(len(G.nodes()), 1)
    }
    
    # Find orphan pages (no incoming links)
    orphans = [node for node in G.nodes() if G.in_degree(node) == 0]
    analysis["orphan_pages"] = len(orphans)
    analysis["orphan_urls"] = orphans[:10]
    
    # Find hub pages (many outgoing links)
    hubs = sorted(G.nodes(), key=lambda x: G.out_degree(x), reverse=True)[:10]
    analysis["hub_pages"] = [
        {"url": url, "outgoing_links": G.out_degree(url)}
        for url in hubs
    ]
    
    # Find authority pages (many incoming links)
    authorities = sorted(G.nodes(), key=lambda x: G.in_degree(x), reverse=True)[:10]
    analysis["authority_pages"] = [
        {"url": url, "incoming_links": G.in_degree(url)}
        for url in authorities
    ]
    
    # Calculate PageRank
    try:
        pagerank = nx.pagerank(G)
        top_pr = sorted(pagerank.items(), key=lambda x: x, reverse=True)[:10][1]
        analysis["top_pagerank"] = [
            {"url": url, "pagerank": round(pr, 4)}
            for url, pr in top_pr
        ]
    except:
        analysis["top_pagerank"] = []
    
    # Suggest internal links
    suggestions = generate_link_suggestions(G, url_to_data, orphans)
    analysis["link_suggestions"] = suggestions
    
    return {
        "success": True,
        **analysis
    }

def generate_link_suggestions(G: nx.DiGraph, url_data: Dict, orphans: List[str]) -> List[Dict]:
    """Generate internal link suggestions"""
    
    suggestions = []
    
    # Link orphan pages to relevant hubs
    hubs = sorted(G.nodes(), key=lambda x: G.out_degree(x), reverse=True)[:5]
    
    for orphan in orphans[:10]:
        orphan_title = url_data.get(orphan, {}).get("title", "")
        orphan_keywords = url_data.get(orphan, {}).get("primary_keyword", "").split()
        
        # Find best hub to link from
        best_hub = None
        best_score = 0
        
        for hub in hubs:
            hub_title = url_data.get(hub, {}).get("title", "")
            hub_keywords = url_data.get(hub, {}).get("primary_keyword", "").split()
            
            # Simple relevance score
            common = set(orphan_keywords) & set(hub_keywords)
            score = len(common)
            
            if score > best_score:
                best_score = score
                best_hub = hub
        
        if best_hub:
            suggestions.append({
                "from_url": best_hub,
                "to_url": orphan,
                "reason": "Link orphan page to relevant hub",
                "priority": "P0",
                "suggested_anchor": orphan_title[:50]
            })
    
    return suggestions[:20]

def detect_broken_internal_links(site_results: List[Dict]) -> Dict:
    """Find broken internal links"""
    
    all_urls = set()
    all_links = set()
    
    for result in site_results:
        if result.get("success"):
            url = result.get("url")
            all_urls.add(url)
            
            internal_links = result.get("auditdata", {}).get("internal_links", [])
            all_links.update(internal_links)
    
    # Find links pointing to non-existent pages
    broken = all_links - all_urls
    
    return {
        "success": True,
        "broken_count": len(broken),
        "broken_links": list(broken)[:50]
    }
'''
"""
Internal Linking Analyzer (Optimized)
Maps site structure, finds orphans, and recommends improvements.
"""
from typing import Dict, List
from collections import defaultdict, Counter, deque
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def analyze_internal_linking(site_results: List[Dict]) -> Dict:
    """
    Analyze internal link structure across site.
    """
    print(f"\n🔗 Analyzing internal linking structure...")
    
    # 1. Initialize Graph
    link_graph = defaultdict(list)      # Source -> [Targets]
    incoming_links = defaultdict(list)  # Target -> [Sources]
    all_urls = []
    
    # 2. Build Graph from Results
    for result in site_results:
        page_url = result.get('url')
        if not page_url: continue
        
        all_urls.append(page_url)
        
        # Robust Data Extraction: Try 'audit_data' then raw 'html'
        # The universal crawler stores data in 'audit_data'
        audit_data = result.get('audit_data', {})
        
        # If we have raw HTML (from full scrape), use it
        html_content = audit_data.get('html_content', '') 
        
        # Fallback: If no HTML, we rely on the crawler's memory if available
        # (For this specific feature to work perfectly, the crawler needs to pass content)
        if not html_content:
            # Skip graph building for this page if no content
            continue

        soup = BeautifulSoup(html_content, 'html.parser')
        base_domain = urlparse(page_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            
            # Filter Logic
            is_internal = False
            if href.startswith('/'): # Relative link
                is_internal = True
            elif base_domain in href: # Absolute internal link
                is_internal = True
                
            if is_internal:
                # Normalize
                target_url = urljoin(page_url, href)
                # Remove anchors (#section) to avoid duplicates
                if '#' in target_url:
                    target_url = target_url.split('#')[0]
                
                # Add to graph
                link_graph[page_url].append(target_url)
                incoming_links[target_url].append(page_url)
    
    # 3. Analyze Graph Data
    
    # Orphans: Pages that exist but have 0 incoming links (excluding homepage)
    homepage = all_urls[0] if all_urls else ""
    orphaned_pages = [
        url for url in all_urls 
        if url != homepage and (url not in incoming_links or len(incoming_links[url]) == 0)
    ]
    
    # Weak Linkers: Pages pointing to very few others
    weak_linkers = {url: len(links) for url, links in link_graph.items() if len(links) < 3}
    
    # Authority: Pages with most incoming links
    most_linked = sorted(
        [(url, len(sources)) for url, sources in incoming_links.items()],
        key=lambda x: x[1], reverse=True
    )[:10]
    
    # Depth Calculation (BFS)
    page_depths = calculate_page_depths(link_graph, homepage) if homepage else {}
    deep_pages = [(url, depth) for url, depth in page_depths.items() if depth > 3]
    
    # 4. Generate Recommendations
    recommendations = generate_linking_recommendations(
        orphaned_pages, weak_linkers, deep_pages, most_linked
    )
    
    return {
        "success": True,
        "total_pages": len(all_urls),
        "total_internal_links": sum(len(targets) for targets in link_graph.values()),
        "orphaned_count": len(orphaned_pages),
        "orphaned_pages": orphaned_pages,
        "weak_linkers_count": len(weak_linkers),
        "deep_pages_count": len(deep_pages),
        "top_authority_pages": most_linked,
        "recommendations": recommendations,
        "linking_score": calculate_linking_score(
            len(orphaned_pages), len(weak_linkers), len(deep_pages), len(all_urls)
        )
    }

def calculate_page_depths(link_graph: Dict, homepage: str) -> Dict[str, int]:
    """Calculate distance from homepage using BFS"""
    depths = {homepage: 0}
    queue = deque([homepage])
    visited = set([homepage])
    
    while queue:
        current = queue.popleft()
        current_depth = depths[current]
        
        for target in link_graph.get(current, []):
            if target not in visited:
                # Only count depth for pages in our crawl list to avoid infinite graphs
                visited.add(target)
                depths[target] = current_depth + 1
                queue.append(target)
    return depths

def generate_linking_recommendations(orphaned, weak, deep, authority):
    """Generate human-readable advice"""
    recs = []
    
    if orphaned:
        recs.append({
            "priority": "P0 (Critical)",
            "issue": f"{len(orphaned)} Orphaned Pages Found",
            "fix": "Link to these pages from relevant content immediately. Search engines cannot find them."
        })
    
    if deep:
        recs.append({
            "priority": "P1 (Important)",
            "issue": f"{len(deep)} Deeply Buried Pages (>3 clicks)",
            "fix": "Move these pages higher in the hierarchy or link from the navigation menu."
        })
        
    if weak:
        recs.append({
            "priority": "P2 (Optimization)",
            "issue": f"{len(weak)} Pages have few internal links",
            "fix": "Add 'Related Posts' or contextual links to these pages to pass authority."
        })
        
    return recs

def calculate_linking_score(orphaned, weak, deep, total):
    if total == 0: return 0
    score = 100
    score -= (orphaned * 5) # Heavy penalty for orphans
    score -= (deep * 3)
    score -= (weak * 1)
    return max(0, score)