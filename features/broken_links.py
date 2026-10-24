'''
"""
Internal Linking Analyzer
Maps site structure and recommends linking improvements
"""
from typing import Dict, List
from collections import defaultdict, Counter
from urllib.parse import urlparse


def analyze_internal_linking(site_results: List[Dict]) -> Dict:
    """
    Analyze internal link structure across site
    
    Args:
        site_results: List of site audit results
        
    Returns:
        Internal linking analysis
    """
    print(f"\n🔗 Analyzing internal linking structure...")
    
    # Build link graph
    link_graph = defaultdict(list)  # source -> [targets]
    incoming_links = defaultdict(list)  # target -> [sources]
    all_urls = []
    
    for result in site_results:
        if not result.get('success'):
            continue
        
        page_url = result.get('url')
        all_urls.append(page_url)
        
        html = result.get('audit_data', {}).get('html', '')
        if not html:
            continue
        
        # Extract internal links
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        base_domain = urlparse(page_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            
            # Check if internal
            if href.startswith('/') or base_domain in href:
                # Normalize URL
                from urllib.parse import urljoin
                target_url = urljoin(page_url, href)
                
                link_graph[page_url].append(target_url)
                incoming_links[target_url].append(page_url)
    
    # Find issues
    orphaned_pages = [url for url in all_urls if url not in incoming_links or len(incoming_links[url]) == 0]
    
    # Pages with few outbound links
    weak_linkers = {url: len(links) for url, links in link_graph.items() if len(links) < 3}
    
    # Most linked pages (authority pages)
    most_linked = sorted(
        [(url, len(sources)) for url, sources in incoming_links.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Pages with many outbound links (potential hub pages)
    hub_pages = sorted(
        [(url, len(targets)) for url, targets in link_graph.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Calculate depth (distance from homepage)
    homepage = next((url for url in all_urls if url.endswith('/') or url.count('/') == 3), all_urls[0] if all_urls else None)
    page_depths = calculate_page_depths(link_graph, homepage) if homepage else {}
    
    deep_pages = [(url, depth) for url, depth in page_depths.items() if depth > 3]
    
    # Generate recommendations
    recommendations = generate_linking_recommendations(
        orphaned_pages,
        weak_linkers,
        deep_pages,
        most_linked
    )
    
    return {
        "success": True,
        "total_pages": len(all_urls),
        "total_internal_links": sum(len(targets) for targets in link_graph.values()),
        "avg_links_per_page": int(sum(len(targets) for targets in link_graph.values()) / len(all_urls)) if all_urls else 0,
        "orphaned_pages": orphaned_pages,
        "orphaned_count": len(orphaned_pages),
        "weak_linkers": weak_linkers,
        "weak_linkers_count": len(weak_linkers),
        "most_linked_pages": most_linked,
        "hub_pages": hub_pages,
        "deep_pages": deep_pages,
        "deep_pages_count": len(deep_pages),
        "page_depths": page_depths,
        "recommendations": recommendations,
        "linking_score": calculate_linking_score(
            len(orphaned_pages),
            len(weak_linkers),
            len(deep_pages),
            len(all_urls)
        )
    }


def calculate_page_depths(link_graph: Dict, homepage: str) -> Dict[str, int]:
    """Calculate how many clicks from homepage (BFS)"""
    from collections import deque
    
    depths = {homepage: 0}
    queue = deque([homepage])
    visited = set([homepage])
    
    while queue:
        current = queue.popleft()
        current_depth = depths[current]
        
        for target in link_graph.get(current, []):
            if target not in visited:
                visited.add(target)
                depths[target] = current_depth + 1
                queue.append(target)
    
    return depths


def generate_linking_recommendations(
    orphaned: List,
    weak: Dict,
    deep: List,
    authority: List
) -> List[Dict]:
    """Generate internal linking recommendations"""
    recommendations = []
    
    if orphaned:
        recommendations.append({
            'priority': 'P0',
            'title': f'Fix {len(orphaned)} orphaned pages',
            'description': 'These pages have no internal links pointing to them',
            'action': 'Add contextual internal links from related pages',
            'pages': orphaned[:10]
        })
    
    if weak:
        recommendations.append({
            'priority': 'P1',
            'title': f'{len(weak)} pages with weak internal linking',
            'description': 'Pages with fewer than 3 outbound internal links',
            'action': 'Add 3-5 relevant internal links to each page',
            'sample_pages': list(weak.keys())[:5]
        })
    
    if deep:
        recommendations.append({
            'priority': 'P1',
            'title': f'{len(deep)} pages buried too deep',
            'description': 'Pages more than 3 clicks from homepage',
            'action': 'Link important deep pages from higher-level pages',
            'deepest_pages': [{'url': url, 'depth': depth} for url, depth in sorted(deep, key=lambda x: x[1], reverse=True)[:5]]
        })
    
    if authority:
        recommendations.append({
            'priority': 'P2',
            'title': 'Leverage authority pages',
            'description': f'Top {len(authority)} most-linked pages',
            'action': 'These pages have authority - consider linking from them to boost other pages',
            'authority_pages': [{'url': url, 'incoming_links': count} for url, count in authority[:5]]
        })
    
    if not orphaned and not weak and not deep:
        recommendations.append({
            'title': 'Internal linking structure is solid',
            'description': 'No major linking issues detected'
        })
    
    return recommendations


def calculate_linking_score(orphaned: int, weak: int, deep: int, total: int) -> int:
    """Calculate internal linking quality score (0-100)"""
    if total == 0:
        return 100
    
    orphaned_penalty = (orphaned / total) * 30
    weak_penalty = (weak / total) * 20
    deep_penalty = (deep / total) * 20
    
    score = 100 - orphaned_penalty - weak_penalty - deep_penalty
    
    return max(0, int(score))
'''
"""
Broken Link Checker (Advanced)
Identifies dead pages (404s), server errors (5xx), and connection failures.
"""

def check_broken_links(site_results, max_checks=50):
    """
    Analyzes crawl results to identify broken pages.
    """
    broken_report = {
        "total_broken": 0,
        "broken_list": [],
        "server_errors": [],
        "timeouts": [],
        "status": "Analysis Complete"
    }

    if not site_results:
        return broken_report

    for page in site_results:
        url = page.get('url', 'Unknown')
        error = str(page.get('error', ''))
        
        # 1. Check for explicit 404s (Not Found)
        if "404" in error or "Not Found" in error:
            broken_report["broken_list"].append({
                "url": url,
                "type": "404 Not Found",
                "action": "Remove link or redirect to relevant content"
            })
            
        # 2. Check for Server Errors (500s)
        elif "500" in error or "502" in error or "503" in error:
            broken_report["server_errors"].append({
                "url": url,
                "type": "Server Error (5xx)",
                "action": "Check server logs or hosting configuration"
            })
            
        # 3. Check for Connection/Timeout issues
        elif "Connection" in error or "Timeout" in error:
            broken_report["timeouts"].append({
                "url": url,
                "type": "Connection Failed",
                "action": "Verify URL is correct and accessible"
            })

    # Summary Count
    broken_report["total_broken"] = (
        len(broken_report["broken_list"]) + 
        len(broken_report["server_errors"]) + 
        len(broken_report["timeouts"])
    )

    return broken_report