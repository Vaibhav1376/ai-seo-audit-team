"""
Schema Markup Validator
Checks for structured data and validates it
"""
from bs4 import BeautifulSoup
import json
from typing import Dict, List


def validate_schema(url: str, html: str) -> Dict:
    """
    Validate schema markup on page
    
    Args:
        url: Page URL
        html: Page HTML
        
    Returns:
        Dict with schema analysis
    """
    print(f"  📋 Validating schema on {url}...")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all LD+JSON scripts
    schema_scripts = soup.find_all('script', {'type': 'application/ld+json'})
    
    schemas_found = []
    schema_types = []
    issues = []
    recommendations = []
    
    for script in schema_scripts:
        try:
            schema_data = json.loads(script.string)
            schema_type = schema_data.get('@type', 'Unknown')
            schema_types.append(schema_type)
            
            schemas_found.append({
                'type': schema_type,
                'valid': True,
                'data': schema_data
            })
            
        except json.JSONDecodeError:
            issues.append("Invalid JSON-LD syntax found")
            schemas_found.append({
                'type': 'Invalid',
                'valid': False,
                'error': 'JSON parsing error'
            })
    
    # Recommend schemas based on page type
    recommended_schemas = detect_recommended_schemas(url, html, soup)
    
    missing_schemas = [s for s in recommended_schemas if s not in schema_types]
    
    if not schemas_found:
        recommendations.append({
            'priority': 'P1',
            'title': 'No schema markup found',
            'description': 'Add structured data to help search engines understand your content',
            'schemas_to_add': recommended_schemas
        })
    elif missing_schemas:
        recommendations.append({
            'priority': 'P2',
            'title': f'Missing recommended schemas: {", ".join(missing_schemas)}',
            'description': 'Adding these schemas can improve search appearance',
            'schemas_to_add': missing_schemas
        })
    
    return {
        "success": True,
        "has_schema": len(schemas_found) > 0,
        "schema_count": len(schemas_found),
        "schema_types": schema_types,
        "schemas_found": schemas_found,
        "recommended_schemas": recommended_schemas,
        "missing_schemas": missing_schemas,
        "issues": issues,
        "recommendations": recommendations,
        "schema_score": calculate_schema_score(schemas_found, recommended_schemas)
    }


def detect_recommended_schemas(url: str, html: str, soup: BeautifulSoup) -> List[str]:
    """Detect what schemas should be on this page"""
    recommended = ['Organization', 'WebPage']  # Always recommended
    
    # Blog post
    if any(word in url.lower() for word in ['blog', 'post', 'article']):
        recommended.extend(['Article', 'BlogPosting'])
    
    # Product page
    if any(word in url.lower() for word in ['product', 'shop', 'buy']):
        recommended.append('Product')
    
    # About page
    if 'about' in url.lower():
        recommended.append('AboutPage')
    
    # Contact page
    if 'contact' in url.lower():
        recommended.append('ContactPage')
    
    # FAQ page
    if 'faq' in url.lower() or soup.find_all(['details', 'summary']):
        recommended.append('FAQPage')
    
    # Local business
    if soup.find(['address']) or any(word in html.lower() for word in ['phone:', 'email:', 'hours:']):
        recommended.append('LocalBusiness')
    
    return list(set(recommended))  # Remove duplicates


def calculate_schema_score(schemas_found: List, recommended: List) -> int:
    """Calculate schema completeness score"""
    if not recommended:
        return 100
    
    if not schemas_found:
        return 0
    
    valid_schemas = [s for s in schemas_found if s.get('valid')]
    schema_types_found = [s['type'] for s in valid_schemas]
    
    matches = len(set(schema_types_found) & set(recommended))
    score = int((matches / len(recommended)) * 100)
    
    return score
