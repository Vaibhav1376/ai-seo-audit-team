"""
Security Headers & HTTPS Check
Validates security best practices
"""
import requests
from typing import Dict, List
import ssl
import socket
from urllib.parse import urlparse


def check_security(url: str) -> Dict:
    """
    Check security headers and HTTPS configuration
    
    Args:
        url: URL to check
        
    Returns:
        Dict with security analysis
    """
    print(f"  🔒 Checking security for {url}...")
    
    issues = []
    recommendations = []
    headers_found = {}
    
    try:
        # Get headers
        response = requests.get(url, timeout=10)
        headers = response.headers
        
        # Check HTTPS
        is_https = url.startswith('https://')
        
        if not is_https:
            issues.append({
                'severity': 'Critical',
                'issue': 'Site not using HTTPS',
                'impact': 'Security risk, SEO penalty, browser warnings',
                'fix': 'Install SSL certificate and redirect HTTP to HTTPS'
            })
        
        # Check security headers
        security_headers = {
            'Strict-Transport-Security': {
                'present': 'Strict-Transport-Security' in headers,
                'importance': 'High',
                'description': 'Forces HTTPS connections'
            },
            'X-Content-Type-Options': {
                'present': 'X-Content-Type-Options' in headers,
                'importance': 'Medium',
                'description': 'Prevents MIME type sniffing'
            },
            'X-Frame-Options': {
                'present': 'X-Frame-Options' in headers,
                'importance': 'High',
                'description': 'Prevents clickjacking attacks'
            },
            'Content-Security-Policy': {
                'present': 'Content-Security-Policy' in headers,
                'importance': 'High',
                'description': 'Prevents XSS and injection attacks'
            },
            'X-XSS-Protection': {
                'present': 'X-XSS-Protection' in headers,
                'importance': 'Low',
                'description': 'Legacy XSS protection'
            },
            'Referrer-Policy': {
                'present': 'Referrer-Policy' in headers,
                'importance': 'Medium',
                'description': 'Controls referrer information'
            }
        }
        
        for header, info in security_headers.items():
            headers_found[header] = info
            
            if not info['present'] and info['importance'] in ['High', 'Critical']:
                issues.append({
                    'severity': info['importance'],
                    'issue': f"Missing {header} header",
                    'impact': info['description'],
                    'fix': f"Add {header} header to server configuration"
                })
        
        # Check SSL certificate (if HTTPS)
        if is_https:
            ssl_info = check_ssl_certificate(url)
            if ssl_info.get('issues'):
                issues.extend(ssl_info['issues'])
        
        # Check mixed content
        if is_https:
            # Note: Would need to parse HTML to check for http:// resources
            pass
        
        # Calculate security score
        security_score = calculate_security_score(is_https, headers_found, issues)
        
        return {
            "success": True,
            "url": url,
            "is_https": is_https,
            "security_headers": headers_found,
            "issues": issues,
            "recommendations": generate_security_recommendations(issues),
            "security_score": security_score
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Security check failed: {str(e)}"
        }


def check_ssl_certificate(url: str) -> Dict:
    """Check SSL certificate validity"""
    issues = []
    
    try:
        hostname = urlparse(url).netloc
        context = ssl.create_default_context()
        
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Could check expiration date here
                # notAfter = cert.get('notAfter')
                
                return {"valid": True, "issues": []}
                
    except ssl.SSLError as e:
        issues.append({
            'severity': 'Critical',
            'issue': 'SSL certificate error',
            'impact': str(e),
            'fix': 'Renew or fix SSL certificate'
        })
        return {"valid": False, "issues": issues}
    except Exception:
        return {"valid": False, "issues": []}


def calculate_security_score(is_https: bool, headers: Dict, issues: List) -> int:
    """Calculate security score 0-100"""
    score = 100
    
    if not is_https:
        score -= 50  # Major penalty
    
    # Penalty for missing headers
    for header, info in headers.items():
        if not info['present']:
            if info['importance'] == 'High':
                score -= 10
            elif info['importance'] == 'Medium':
                score -= 5
    
    # Penalty for critical issues
    for issue in issues:
        if issue['severity'] == 'Critical':
            score -= 15
        elif issue['severity'] == 'High':
            score -= 10
    
    return max(0, score)


def generate_security_recommendations(issues: List) -> List[Dict]:
    """Generate actionable security recommendations"""
    recommendations = []
    
    if not issues:
        return [{'title': 'Security looks good!', 'description': 'No major security issues found'}]
    
    # Group by severity
    critical = [i for i in issues if i['severity'] == 'Critical']
    high = [i for i in issues if i['severity'] == 'High']
    
    if critical:
        recommendations.append({
            'priority': 'P0',
            'title': f'{len(critical)} critical security issues',
            'description': 'Fix these immediately',
            'issues': critical
        })
    
    if high:
        recommendations.append({
            'priority': 'P1',
            'title': f'{len(high)} high-priority security issues',
            'description': 'Fix within 1 week',
            'issues': high
        })
    
    return recommendations
