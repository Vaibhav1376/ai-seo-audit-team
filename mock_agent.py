"""
Mock SEO Agent - Works without API quota
Returns realistic demo data for testing
"""

import time
from datetime import datetime

class MockAgent:
    """Demo agent that doesn't use API calls"""
    
    def run(self, query):
        """Generate mock audit report"""
        
        # Extract URL
        url = query.replace("Audit ", "").strip()
        
        # Simulate thinking time
        time.sleep(2)
        
        # Generate realistic mock report
        report = f"""# SEO Audit Report (DEMO MODE)

⚠️ **DEMO MODE ACTIVE** - API quota exceeded. [Get new API key](https://aistudio.google.com/app/apikey)

## Executive Summary
- **URL Audited:** {url}
- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Overall Health Score:** 72/100 (Demo)
- **Primary Keyword Focus:** "website optimization"
- **Search Intent:** Informational

### Quick Assessment
This is a demo audit generated without API calls. The page shows moderate SEO health with several optimization opportunities. Critical fixes needed in meta descriptions and heading structure.

---

## Technical & On-Page Findings

### Title Tag Analysis
- **Current:** Example Domain (14 characters)
- **Status:** ⚠️ Too short - Missing keyword
- **Recommendation:** Expand to 50-60 characters, include primary keyword
- **Ideal Example:** "Example Domain - Your Source for Website Examples | 2025"

### Meta Description
- **Current:** Missing or too short
- **Status:** ❌ Critical Issue
- **Length:** 0 characters (needs 150-160)
- **Recommendation:** Add compelling meta description with call-to-action
- **Example:** "Discover example websites and best practices for web development. Learn from real-world demos and improve your site's user experience today."

### Heading Structure
- **H1:** Found (1 heading)
- **H2 Count:** 3 headings
- **H3-H4 Count:** 5 headings
- **Status:** ✅ Good hierarchy
- **Issues:** 
  - H1 should include primary keyword
  - Add more H2 sections for better content structure

### Content Analysis
- **Word Count:** ~487 words
- **Reading Level:** Grade 8 (Good)
- **Content Quality:** Moderate
- **Keyword Density:** 1.2% (Optimal: 1-2%)
- **Issues Found:**
  - Content is thin - aim for 1000+ words for informational pages
  - Missing multimedia elements (images, videos)
  - No internal links to related content
  - Lacking clear call-to-action

### Link Profile
- **Internal Links:** 3
- **External Links:** 1
- **Broken Links:** 0
- **Status:** ⚠️ Needs improvement
- **Recommendations:**
  - Add 5-10 internal links to related pages
  - Include 2-3 authoritative external sources
  - Implement breadcrumb navigation

### Technical Issues Found
1. **Missing Alt Text** - 2 images without alt attributes
2. **No Structured Data** - Add Schema.org markup for better SERP display
3. **Slow Load Time** - Estimated 3.2s (aim for <2s)
4. **Mobile Responsiveness** - Not optimized for mobile devices
5. **No Canonical Tag** - Risk of duplicate content issues
6. **Missing XML Sitemap** - Not found at /sitemap.xml
7. **No robots.txt** - Create to guide search engine crawling
8. **SSL Certificate** - ✅ HTTPS enabled (Good!)

---

## Keyword Analysis

### Primary Keyword
- **Keyword:** "example website"
- **Monthly Search Volume:** ~12,000 (Demo data)
- **Difficulty:** Medium (45/100)
- **Current Ranking:** Not in top 100

### Secondary Keywords
- "website examples"
- "demo website"
- "sample web page"
- "test website design"
- "example domain"

### Search Intent
- **Type:** Informational
- **User Goal:** Looking for website examples and demos
- **Content Match:** 70% aligned

### Supporting Topics
- Web design principles
- HTML/CSS examples
- Website templates
- Domain registration
- Web hosting basics

---

## Competitive SERP Analysis (Demo Data)

### Top Competitor Patterns
Based on mock SERP analysis, top-ranking pages for "example website" show:
- Average word count: 1,800 words
- Multiple screenshots and visual examples
- Comprehensive tutorials and guides
- Strong internal linking structure
- Featured snippets present in 40% of results

### Common Title Formulas
1. "25+ Best Example Websites for [Year]"
2. "Example Websites: Complete Guide with Screenshots"
3. "Top Website Examples for Inspiration | [Brand]"
4. "How to Create Example Websites: Step-by-Step Guide"

### Content Formats Winning
- **Long-form guides** (60%)
- **Listicles with examples** (25%)
- **Video tutorials** (10%)
- **Interactive demos** (5%)

### Key Themes in Top Results
1. Visual examples with screenshots
2. Step-by-step tutorials
3. Code snippets and technical details
4. Comparison tables
5. Download/template sections

### Differentiation Opportunities
- Create interactive website builder tool
- Add live preview functionality
- Offer downloadable templates
- Include industry-specific examples
- Add video walkthroughs

---

## Prioritized Recommendations

### P0 - Critical (Do This Week)

#### 1. Add Meta Description
- **Fix:** Write compelling 155-character meta description
- **Why:** Missing meta = poor CTR in search results
- **Impact:** +15% CTR improvement expected
- **Effort:** Low (10 minutes)
- **How To:** Add this to `<head>`: `<meta name="description" content="your text here">`

#### 2. Optimize Title Tag
- **Fix:** Expand to 50-60 characters with primary keyword
- **Why:** Title is main ranking signal and SERP display
- **Impact:** Better rankings + CTR
- **Effort:** Low (5 minutes)

#### 3. Fix Alt Text on Images
- **Fix:** Add descriptive alt text to all 2 images
- **Why:** Accessibility + image SEO
- **Impact:** Improved accessibility score + image search visibility
- **Effort:** Low (15 minutes)

---

### P1 - Important (Do This Month)

#### 4. Expand Content to 1000+ Words
- **Fix:** Add 3-5 new sections with detailed explanations
- **Why:** Thin content hurts rankings
- **Impact:** Potential to rank for 10+ additional long-tail keywords
- **Effort:** Medium (2-3 hours)

#### 5. Implement Schema Markup
- **Fix:** Add Organization/WebPage schema
- **Why:** Enhanced SERP display (rich snippets)
- **Impact:** +20% CTR from rich results
- **Effort:** Medium (1 hour)

#### 6. Improve Internal Linking
- **Fix:** Add 5-8 contextual internal links
- **Why:** Helps crawling, distributes link equity, improves UX
- **Impact:** Better crawl efficiency + user engagement
- **Effort:** Low (30 minutes)

---

### P2 - Nice to Have (Do Next Quarter)

#### 7. Add Multimedia Elements
- **Fix:** Embed 2-3 videos, 5+ images, 1 infographic
- **Why:** Increases dwell time and engagement
- **Impact:** Reduced bounce rate
- **Effort:** High (4-5 hours)

#### 8. Create FAQ Section
- **Fix:** Add 5-10 frequently asked questions
- **Why:** Targets "People Also Ask" opportunities
- **Impact:** Potential featured snippet
- **Effort:** Medium (1 hour)

#### 9. Implement Table of Contents
- **Fix:** Add sticky ToC with jump links
- **Why:** Improves UX for long content
- **Impact:** Better user engagement metrics
- **Effort:** Medium (1 hour)

---

## Next Steps

### Immediate Actions (Today)
1. ✅ Fix meta description
2. ✅ Update title tag
3. ✅ Add image alt text

### This Week
4. Get new API key from: https://aistudio.google.com/app/apikey
5. Update `.env` file with new key
6. Run real audit to get accurate data
7. Implement schema markup
8. Add internal links

### This Month
9. Expand content to 1000+ words
10. Add multimedia elements
11. Create FAQ section
12. Monitor rankings weekly

### Tracking Metrics
- Monitor organic traffic (Google Analytics)
- Track keyword rankings (Google Search Console)
- Check CTR improvements (Search Console)
- Measure bounce rate changes (Analytics)
- Re-audit in 30 days

---

## API Quota Status

⚠️ **DEMO MODE ACTIVE**

**Current Status:** API quota exceeded  
**Reset Time:** Check at https://ai.dev/usage?tab=rate-limit  
**Actions:**
1. Get new free API key: https://aistudio.google.com/app/apikey
2. Or wait for quota reset (24 hours)
3. Update `.env` file with: `GOOGLE_API_KEY=your_new_key`

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Mode:** Demo (No API calls used)  
**Agent:** Mock SEO Analyzer v1.0

*This is a demonstration report. For accurate, real-time SEO analysis with live competitor data and SERP insights, please configure a valid API key.*
"""
        
        return report

# Create agent instance
agent = MockAgent()

# Test function
if __name__ == "__main__":
    print("Testing Mock Agent...")
    result = agent.run("Audit https://example.com")
    print("\n" + "="*70)
    print(result)
    print("="*70)
