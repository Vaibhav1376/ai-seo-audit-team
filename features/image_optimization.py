"""
Image Optimization Analyzer
Finds oversized images, missing alt tags, format issues
"""
from bs4 import BeautifulSoup
import requests
from typing import Dict, List


def analyze_images(url: str, html: str) -> Dict:
    """
    Analyze all images on a page
    
    Args:
        url: Page URL
        html: Page HTML
        
    Returns:
        Dict with image issues and recommendations
    """
    print(f"  🖼️  Analyzing images on {url}...")
    
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img')
    
    issues = {
        'missing_alt': [],
        'oversized_images': [],
        'wrong_format': [],
        'lazy_loading_missing': [],
    }
    
    recommendations = []
    
    for img in images:
        src = img.get('src', '')
        alt = img.get('alt', '')
        loading = img.get('loading', '')
        
        # Check alt text
        if not alt:
            issues['missing_alt'].append(src)
        
        # Check lazy loading
        if not loading or loading != 'lazy':
            issues['lazy_loading_missing'].append(src)
        
        # Check format (if URL suggests old format)
        if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            if '.webp' not in src.lower():
                issues['wrong_format'].append({
                    'src': src,
                    'suggestion': 'Convert to WebP format for better compression'
                })
        
        # Try to check image size (if URL is accessible)
        if src.startswith('http'):
            try:
                head = requests.head(src, timeout=3)
                size = int(head.headers.get('content-length', 0))
                
                if size > 100000:  # >100KB
                    issues['oversized_images'].append({
                        'src': src,
                        'size_kb': int(size / 1024),
                        'recommendation': f'Compress image - current size: {int(size/1024)}KB'
                    })
            except:
                pass
    
    # Generate recommendations
    if issues['missing_alt']:
        recommendations.append({
            'priority': 'P0',
            'issue': f"{len(issues['missing_alt'])} images missing alt text",
            'impact': 'Accessibility and SEO',
            'fix': 'Add descriptive alt text to all images'
        })
    
    if issues['oversized_images']:
        recommendations.append({
            'priority': 'P1',
            'issue': f"{len(issues['oversized_images'])} images over 100KB",
            'impact': 'Page speed and user experience',
            'fix': 'Compress images using tools like TinyPNG or ImageOptim'
        })
    
    if issues['wrong_format']:
        recommendations.append({
            'priority': 'P1',
            'issue': f"{len(issues['wrong_format'])} images not using modern formats",
            'impact': 'Page speed - WebP is 25-35% smaller',
            'fix': 'Convert images to WebP format'
        })
    
    if issues['lazy_loading_missing']:
        recommendations.append({
            'priority': 'P2',
            'issue': f"{len(issues['lazy_loading_missing'])} images without lazy loading",
            'impact': 'Initial page load time',
            'fix': 'Add loading="lazy" attribute to images below fold'
        })
    
    return {
        "success": True,
        "total_images": len(images),
        "issues": issues,
        "recommendations": recommendations,
        "optimization_score": calculate_image_score(issues, len(images))
    }


def calculate_image_score(issues: Dict, total_images: int) -> int:
    """Calculate image optimization score 0-100"""
    if total_images == 0:
        return 100
    
    deductions = 0
    
    # Missing alt = -5 per image
    deductions += len(issues['missing_alt']) * 5
    
    # Oversized = -3 per image
    deductions += len(issues['oversized_images']) * 3
    
    # Wrong format = -2 per image
    deductions += len(issues['wrong_format']) * 2
    
    # Missing lazy loading = -1 per image
    deductions += len(issues['lazy_loading_missing']) * 1
    
    score = max(0, 100 - deductions)
    return score
