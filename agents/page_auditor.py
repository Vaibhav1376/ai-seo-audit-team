"""
Agent 1: Page SEO Auditor
Scrapes and analyzes individual pages with feature integration
"""
import os
import google.generativeai as genai
import json
from typing import Dict
from firecrawl import FirecrawlApp
from utils.scraper import scrape_url
from config import AGENT_CONFIG
from utils.js_scraper import scrape_with_js_rendering
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")


def pageauditor(url: str, model: str = None, features: Dict = None) -> Dict:
    """Agent 1: Page SEO Auditor with Advanced Features
    
    Args:
        url: URL to audit
        model: Gemini model to use
        features: Dict of enabled features
        
    Returns:
        Dict with audit data and feature results
    """

    print(f"\n{'='*70}")
    print(f"🤖 AGENT 1: Page SEO Auditor")
    print(f"{'='*70}")
    print(f"📱 URL: {url}")
    print(f"📱 Model: {model or AGENT_CONFIG.get('model', 'gemini-1.5-flash')}")
    
    # Initialize features if not provided
    if features is None:
        features = {}
    
    # Step 1: Scrape page
    print("\n🔍 Step 1/3: Scraping page...")
    
    try:
        # Use utils.scraper which handles content extraction better
        scraped_data = scrape_url(url)
        if scraped_data.get('word_count', 0) < 100:
            print("⚠️ Low content detected, trying JS rendering...")
            scraped_data = scrape_with_js_rendering(url, wait_time=5)
        
        # Validate we got content
        if not scraped_data or not scraped_data.get('success'):
            print("❌ Scraping failed - Site may be blocking bots")
            return {
                "success": False,
                "error": "Failed to scrape URL. Site may be blocking bots or URL is invalid.",
                "url": url,
                "scores": _calculate_scores({})
            }
        
        # Check for actual content
        word_count = scraped_data.get('word_count', 0)
        if word_count < 50:
            print(f"⚠️ Low content detected: {word_count} words")
            scraped_data['warning'] = "Scraper extracted minimal content. Results may be incomplete."
        
        print(f"✅ Page scraped successfully!")
        print(f"   - Title: {scraped_data.get('title', 'N/A')[:60]}...")
        print(f"   - Word count: {word_count}")
        print(f"   - Internal links: {scraped_data.get('internal_links_count', 0)}")
        print(f"   - External links: {scraped_data.get('external_links_count', 0)}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return {
            "success": False,
            "error": f"Scraper module not found: {str(e)}",
            "url": url,
            "scores": _calculate_scores({})
        }
        
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return {
            "success": False,
            "error": f"Scraper exception: {str(e)}",
            "url": url,
            "scores": _calculate_scores({})
        }
    
    # Step 2: Run Advanced Features
    print("\n🚀 Running advanced features...")
    scraped_data = _run_features(url, scraped_data, features)
    
    # Step 3: AI Analysis
    print("\n🤖 Step 2/3: AI analysis...")
    audit_data = _analyze_with_ai(scraped_data, model)
    
    # Step 4: Calculate scores
    print("\n📊 Step 3/3: Calculating scores...")
    audit_data['scores'] = _calculate_scores(scraped_data)
    
    print(f"\n✅ Agent 1 Complete!")
    print(f"   Overall Score: {audit_data['scores']['overall_score']}/100")
    print(f"   - Content: {audit_data['scores']['content_score']}/100")
    print(f"   - On-Page: {audit_data['scores']['on_page_score']}/100")
    print(f"   - Technical: {audit_data['scores']['technical_score']}/100")
    
    return audit_data



def _run_features(url: str, scraped_data: Dict, features: Dict) -> Dict:
    """Run enabled advanced features"""
    print("\n🚀 Running advanced features...")
    
    # PageSpeed Insights
    if features.get('page_speed'):
        print("   🚀 Running PageSpeed Insights...")
        try:
            from features import page_speed
            scraped_data['page_speed'] = page_speed.get_pagespeed_insights(url)
        except Exception as e:
            print(f"   ⚠️ PageSpeed failed: {e}")
            scraped_data['page_speed'] = {"success": False, "error": str(e)}
    
    # Image Optimization
    if features.get('image_optimization'):
        print("   🖼️ Analyzing images...")
        try:
            from features import image_optimization
            html = scraped_data.get('html', '')
            if html:
                scraped_data['image_analysis'] = image_optimization.analyze_images(url, html)
        except Exception as e:
            print(f"   ⚠️ Image analysis failed: {e}")
            scraped_data['image_analysis'] = {"success": False, "error": str(e)}
    
    # Schema Validation
    if features.get('schema'):
        print("   📋 Validating schema...")
        try:
            from features import schema_validator
            html = scraped_data.get('html', '')
            if html:
                scraped_data['schema_validation'] = schema_validator.validate_schema(url, html)
        except Exception as e:
            print(f"   ⚠️ Schema validation failed: {e}")
            scraped_data['schema_validation'] = {"success": False, "error": str(e)}
    
    # Security Check
    if features.get('security'):
        print("   🔒 Running security check...")
        try:
            from features import security_check
            scraped_data['security_check'] = security_check.check_security(url)
        except Exception as e:
            print(f"   ⚠️ Security check failed: {e}")
            scraped_data['security_check'] = {"success": False, "error": str(e)}
    
    # Mobile Check
    if features.get("mobile"):
        print("Checking mobile-friendliness...")
        try:
            from features import mobile_checker
            scraped_data["mobile_check"] = mobile_checker.check_mobile_friendly(url)
        except Exception as e:
            print(f"Mobile check failed: {e}")
            scraped_data["mobile_check"] = {"success": False, "error": str(e)}

    # Mobile vs Desktop Performance (NEW)
    if features.get('mobile_desktop'):
        print("   📱 Analyzing mobile vs desktop performance...")
        try:
            from features.pagespeed_advanced import analyze_mobile_desktop
            scraped_data['mobile_desktop'] = analyze_mobile_desktop(url)
            
            # Update mobile score based on real data
            if scraped_data['mobile_desktop'].get('mobile', {}).get('score'):
                scraped_data['mobile_score_real'] = scraped_data['mobile_desktop']['mobile']['score']
                
        except Exception as e:
            print(f"   ⚠️ Mobile/Desktop analysis failed: {e}")
            scraped_data['mobile_desktop'] = {"success": False, "error": str(e)}  

    # Topic Clustering (NEW)
    if features.get('topic_clustering'):
        print("   🧠 Clustering topics...")
        try:
            from features.topic_clustering import cluster_topics
            text = scraped_data.get('text', '')
            if len(text) > 100:
                scraped_data['topic_clusters'] = cluster_topics(text, url)
            else:
                scraped_data['topic_clusters'] = {"success": False, "error": "Insufficient content"}
        except Exception as e:
            print(f"   ⚠️ Topic clustering failed: {e}")
            scraped_data['topic_clusters'] = {"success": False, "error": str(e)}    

    # Search Volume (NEW)
    if features.get('search_volume'):
        print("   🔍 Fetching search volume...")
        try:
            from features.search_volume import get_search_volume, get_keyword_suggestions
            
            # Get keywords from scraped data
            primary_kw = scraped_data.get('primary_keyword', '')
            secondary_kws = scraped_data.get('secondary_keywords', [])
            all_keywords = [primary_kw] + secondary_kws if primary_kw else secondary_kws
            
            if all_keywords:
                scraped_data['search_volume'] = get_search_volume(all_keywords[:5])
                scraped_data['keyword_suggestions'] = get_keyword_suggestions(primary_kw if primary_kw else all_keywords)
            
        except Exception as e:
            print(f"   ⚠️ Search volume check failed: {e}")
            scraped_data['search_volume'] = {"success": False, "error": str(e)}
    
    # Seasonal Trends (NEW)
    if features.get('seasonal_trends'):
        print("   📈 Analyzing seasonal trends...")
        try:
            from features.seasonal_trends import analyze_seasonal_trends, get_trending_topics
            
            primary_kw = scraped_data.get('primary_keyword', '')
            secondary_kws = scraped_data.get('secondary_keywords', [])
            keywords = ([primary_kw] + secondary_kws[:4]) if primary_kw else secondary_kws[:5]
            
            if keywords:
                scraped_data['seasonal_trends'] = analyze_seasonal_trends(keywords)
                scraped_data['trending_topics'] = get_trending_topics()
            
        except Exception as e:
            print(f"   ⚠️ Seasonal trends failed: {e}")
            scraped_data['seasonal_trends'] = {"success": False, "error": str(e)}
    
    # Keyword Recommendations (NEW)
    if features.get('keyword_recommendations'):
        print("   💡 Getting keyword recommendations...")
        try:
            from features.competitor_keywords import get_keyword_recommendations
            niche = features.get('niche', 'general')
            scraped_data['keyword_recommendations'] = get_keyword_recommendations(url, niche)
            
        except Exception as e:
            print(f"   ⚠️ Keyword recommendations failed: {e}")
            scraped_data['keyword_recommendations'] = {"success": False, "error": str(e)}

    if features.get('domain_authority'):
        print("   📊 Checking Domain Authority...")
        try:
            from features.domain_authority import get_domain_authority
            scraped_data['domain_metrics'] = get_domain_authority(url)
        except Exception as e:
            print(f"   ⚠️ DA check failed: {e}")
            scraped_data['domain_metrics'] = {"success": False, "error": str(e)}
    
    # Referring Domains (NEW)
    if features.get('referring_domains'):
        print("   🔗 Fetching referring domains...")
        try:
            from features.referring_domains import get_referring_domains
            scraped_data['referring_domains'] = get_referring_domains(url, limit=50)
        except Exception as e:
            print(f"   ⚠️ Referring domains failed: {e}")
            scraped_data['referring_domains'] = {"success": False, "error": str(e)}
    
    # Backlink Profile (NEW)
    if features.get('backlink_profile'):
        print("   🔗 Analyzing backlink profile...")
        try:
            from features.backlink_database import get_backlink_profile
            scraped_data['backlink_profile'] = get_backlink_profile(url, limit=100)
        except Exception as e:
            print(f"   ⚠️ Backlink analysis failed: {e}")
            scraped_data['backlink_profile'] = {"success": False, "error": str(e)}    

    # New Backlinks (NEW)
    if features.get('track_new_backlinks'):
        print("   🆕 Tracking new backlinks...")
        try:
            from features.backlink_changes import detect_new_backlinks
            scraped_data['new_backlinks'] = detect_new_backlinks(url)
        except Exception as e:
            print(f"   ⚠️ New backlinks tracking failed: {e}")
            scraped_data['new_backlinks'] = {"success": False, "error": str(e)}
    
    # Lost Backlinks (NEW)
    if features.get('track_lost_backlinks'):
        print("   ❌ Tracking lost backlinks...")
        try:
            from features.backlink_changes import detect_lost_backlinks
            scraped_data['lost_backlinks'] = detect_lost_backlinks(url)
        except Exception as e:
            print(f"   ⚠️ Lost backlinks tracking failed: {e}")
            scraped_data['lost_backlinks'] = {"success": False, "error": str(e)}
    
    # Toxic Links (NEW)
    if features.get('toxic_links'):
        print("   🦠 Detecting toxic links...")
        try:
            from features.toxic_links import detect_toxic_links
            scraped_data['toxic_links'] = detect_toxic_links(url)
        except Exception as e:
            print(f"   ⚠️ Toxic link detection failed: {e}")
            scraped_data['toxic_links'] = {"success": False, "error": str(e)}

    return scraped_data


def _analyze_with_ai(scraped_data: Dict, model: str = None) -> Dict:
    """Analyze scraped data with Gemini AI"""
    
    # Configure Gemini
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model_name = model or os.getenv("SELECTED_MODEL", AGENT_CONFIG.get('model', 'gemini-1.5-flash'))
    gemini_model = genai.GenerativeModel(
        model_name=model_name,
        generation_config={"temperature": AGENT_CONFIG.get('temperature', 0.2)}
    )
    
    # Build enhanced prompt
    prompt = f"""You are a Senior SEO Consultant analyzing a webpage. Be specific and actionable.

# PAGE DATA:
- URL: {scraped_data.get('url')}
- Title: {scraped_data.get('title', 'Missing')}
- Meta Description: {scraped_data.get('meta_description', 'Missing')}
- Word Count: {scraped_data.get('word_count', 0)}
- H1 Tags: {scraped_data.get('h1_tags', [])}
- Internal Links: {scraped_data.get('internal_links_count', 0)}
- External Links: {scraped_data.get('external_links_count', 0)}

# CONTENT SAMPLE:
{scraped_data.get('text', 'No content extracted')[:1500]}...

# YOUR TASK:
Analyze this page and provide insights in JSON format.

IMPORTANT: 
- If word count is 0 or very low, state: "Content extraction failed or page blocks scrapers"
- Be honest about quality - don't inflate scores
- Provide 3-5 specific, actionable recommendations

Return ONLY valid JSON (no markdown):
{{
    "primary_keyword": "main topic keyword",
    "secondary_keywords": ["keyword1", "keyword2", "keyword3"],
    "technical_issues": ["specific issue 1", "specific issue 2"],
    "content_quality_score": 75,
    "content_feedback": "2-3 sentence assessment of content quality and relevance",
    "top_3_recommendations": [
        "Specific action 1",
        "Specific action 2", 
        "Specific action 3"
    ]
}}
"""
    
    try:
        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean JSON from markdown
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].strip()
        else:
            json_str = response_text
        
        ai_analysis = json.loads(json_str)
        
        # Merge with scraped data
        audit_data = {**scraped_data, **ai_analysis, "success": True}
        return audit_data
        
    except Exception as e:
        print(f"⚠️ AI analysis failed: {e}")
        return {
            **scraped_data,
            "primary_keyword": "Not determined",
            "secondary_keywords": [],
            "technical_issues": ["AI analysis unavailable"],
            "content_quality_score": 50,
            "content_feedback": f"AI analysis failed: {str(e)}",
            "top_3_recommendations": ["Fix scraper", "Retry analysis", "Check API key"],
            "success": True
        }


def _calculate_scores(scraped_data):
    """
    Calculate realistic SEO scores (0-100) based on actual data.
    """
    # Initialize
    tech_score = 50  # Start at 50 (neutral)
    content_score = 50
    onpage_score = 50
    mobile_score = 80  # Assume decent mobile unless proven otherwise
    
    try:
        # Extract data
        word_count = scraped_data.get('word_count', 0)
        internal_links = scraped_data.get('internal_links_count', 0)
        external_links = scraped_data.get('external_links_count', 0)
        title = scraped_data.get('title', '')
        meta_desc = scraped_data.get('meta_description', '')
        h1_tags = scraped_data.get('h1_tags', [])
        
        # === CONTENT SCORE (0-100) ===
        # Based on word count and depth
        if word_count > 2000:
            content_score = 95
        elif word_count > 1000:
            content_score = 85
        elif word_count > 500:
            content_score = 70
        elif word_count > 200:
            content_score = 55
        elif word_count > 50:
            content_score = 40
        else:
            content_score = 20  # Very thin content
        
        # === ON-PAGE SCORE (0-100) ===
        onpage_score = 0
        
        # Title tag (30 points)
        if title:
            if 30 <= len(title) <= 60:
                onpage_score += 30
            elif len(title) > 0:
                onpage_score += 20
        
        # Meta description (25 points)
        if meta_desc:
            if 120 <= len(meta_desc) <= 160:
                onpage_score += 25
            elif len(meta_desc) > 0:
                onpage_score += 15
        
        # H1 tag (20 points)
        if h1_tags and len(h1_tags) > 0:
            onpage_score += 20
        
        # Internal linking (25 points)
        if internal_links > 10:
            onpage_score += 25
        elif internal_links > 5:
            onpage_score += 15
        elif internal_links > 0:
            onpage_score += 10
        
        # === TECHNICAL SCORE (0-100) ===
        tech_score = 50  # Base
        
        # Has content
        if word_count > 100:
            tech_score += 20
        
        # Good link ratio
        if internal_links > 0 and external_links > 0:
            ratio = internal_links / (internal_links + external_links)
            if 0.5 <= ratio <= 0.8:  # Healthy internal:external ratio
                tech_score += 15
        
        # Has meta tags
        if title and meta_desc:
            tech_score += 15
        
        tech_score = min(100, tech_score)
        
        # === OVERALL SCORE ===
        # Weighted average
        overall = int(
            (content_score * 0.35) +
            (onpage_score * 0.30) +
            (tech_score * 0.25) +
            (mobile_score * 0.10)
        )
        
    except Exception as e:
        print(f"⚠️ Scoring error: {e}")
        # Fallback
        content_score = 50
        onpage_score = 50
        tech_score = 50
        overall = 50
    
    return {
        "content_score": int(content_score),
        "on_page_score": int(onpage_score),
        "onpage_score": int(onpage_score),  # Compatibility
        "technical_score": int(tech_score),
        "mobile_score": int(mobile_score),
        "overall_score": int(overall),
        "overall": int(overall)  # Compatibility
    }
