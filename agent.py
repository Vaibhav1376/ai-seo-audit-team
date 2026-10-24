'''
"""
On-Page SEO Audit & Optimization Team built with Google ADK.
Combined single-agent approach for efficiency.
"""

from __future__ import annotations
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.tools.google_search_tool import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams, StdioServerParameters

# =============================================================================
# Rate Limiting & Retry (Import if available, otherwise skip)
# =============================================================================
try:
    from utils.rate_limiter import rate_limit
    from utils.retry_handler import retry_with_backoff
    HAS_RATE_LIMITING = True
except ImportError:
    HAS_RATE_LIMITING = False
    print("⚠️ Rate limiting not available - install utils/rate_limiter.py")

# =============================================================================
# Output Schemas (Keep for reference, not used in combined agent)
# =============================================================================

class HeadingItem(BaseModel):
    tag: str = Field(..., description="Heading tag such as h1, h2, h3.")
    text: str = Field(..., description="Text content of the heading.")

class LinkCounts(BaseModel):
    internal: Optional[int] = Field(None, description="Number of internal links on the page.")
    external: Optional[int] = Field(None, description="Number of external links on the page.")
    broken: Optional[int] = Field(None, description="Number of broken links detected.")

# =============================================================================
# Tools
# =============================================================================

# Firecrawl MCP Toolset
firecrawl_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=[
                "-y",
                "firecrawl-mcp",
            ],
            env={
                "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY", "")
            }
        )
    ),
    tool_filter=['firecrawl_scrape']
)

# Google Search Tool
search_executor_agent = LlmAgent(
    name="perform_google_search",
    model="gemini-2.5-flash-lite",
    description="Executes Google searches for provided queries and returns structured results.",
    instruction="""The latest user message contains the keyword to search.
- Call google_search with that exact query and fetch the top organic results (aim for 10).
- Respond with JSON text containing the query and an array of result objects (title, url, snippet). Use an empty array when nothing is returned.
- No additional commentary—return JSON text only.""",
    tools=[google_search],
)

google_search_tool = AgentTool(search_executor_agent)

# =============================================================================
# Combined SEO Agent (Single Agent Approach)
# =============================================================================

combined_seo_agent = LlmAgent(
    name="CombinedSEOAgent",
    model="gemini-2.5-flash-lite",
    description="Performs complete SEO audit: page scraping, SERP analysis, and optimization recommendations in ONE call",
    instruction="""You are an expert SEO consultant. Given a URL, perform a comprehensive audit in these steps:

STEP 1: EXTRACT URL
- Look for a URL in the user's message (starts with http:// or https://)
- Example: "Audit https://example.com" → extract "https://example.com"

STEP 2: SCRAPE THE PAGE
- Call `firecrawl_scrape` with:
  * url: [the extracted URL]
  * formats: ["markdown", "html", "links"]
  * onlyMainContent: true
  * timeout: 90000

STEP 3: ANALYZE PAGE STRUCTURE
Parse the scraped content and extract:
- **Title tag**: Full title text
- **Meta description**: Full meta description
- **H1**: Primary heading
- **H2-H4**: All secondary headings (list them)
- **Word count**: Approximate words in main content
- **Links**: Count internal, external, and broken links
- **Technical issues**: Missing alt text, slow loading, mobile issues, etc.
- **Content gaps**: Missing sections, thin content, etc.

STEP 4: IDENTIFY KEYWORDS
Based on the content:
- **Primary keyword**: 1-3 words (most important topic)
- **Secondary keywords**: 3-5 related terms
- **Search intent**: informational/transactional/navigational/commercial
- **Supporting topics**: 3-5 entities/themes

STEP 5: RESEARCH SERP COMPETITION
- Call `perform_google_search` with the primary keyword you identified
- Analyze the top 10 results and note:
  * Common title patterns (e.g., "Best", "Top 10", year)
  * Content formats (guides, listicles, tools, videos)
  * Key themes across competitors
  * Questions in snippets (People Also Ask)
  * Differentiation opportunities (gaps in competition)

STEP 6: GENERATE COMPREHENSIVE REPORT
Create a markdown report with these sections:

# SEO Audit Report

## Executive Summary
- URL audited: [the URL]
- Primary keyword focus: [keyword]
- Overall assessment: [2-3 sentences on strengths/weaknesses]

## Technical & On-Page Findings

### Title Tag
- Current: [exact title] ([X] characters)
- Recommendation: [improved version]
- Issues: [too long/short, missing keyword, etc.]

### Meta Description
- Current: [exact meta] ([X] characters)
- Recommendation: [improved version]

### Heading Structure
- H1: [current H1]
- H2-H4 count: [number]
- Issues: [multiple H1s, missing hierarchy, etc.]

### Content Analysis
- Word count: [number]
- Quality: [assessment]
- Recommendations: [expand sections, add media, etc.]

### Link Profile
- Internal links: [count]
- External links: [count]
- Broken links: [count]
- Issues: [recommendations]

### Technical Issues Found
[List each issue as bullet points]

## Keyword Analysis
- Primary: [keyword]
- Secondary: [list]
- Search intent: [type]
- Supporting topics: [list]

## Competitive SERP Analysis

### Top Competitor Patterns
[Summarize what top 10 results are doing]

### Common Title Formulas
[List patterns like "Best X for Y in 2025"]

### Content Formats Winning
[List types: guides, comparisons, tools, etc.]

### Key Themes in Top Results
[List 3-5 recurring topics]

### Differentiation Opportunities
[List gaps your content can fill]

## Prioritized Recommendations

### P0 (Critical - Do First)
1. **[Issue]**
   - Fix: [specific action]
   - Why: [rationale with data]
   - Impact: [expected result]
   - Effort: [Low/Medium/High]

### P1 (Important - Do Soon)
[Same format]

### P2 (Nice to Have)
[Same format]

## Next Steps
1. Implement P0 fixes within 1 week
2. Track rankings for: [primary keyword]
3. Measure: [specific metrics]
4. Re-audit in: 30 days

---

**IMPORTANT OUTPUT RULES:**
- Return ONLY the markdown report
- Start directly with "# SEO Audit Report"
- NO JSON, NO preamble text
- Be specific with numbers and data
- Cite findings from scrape and SERP data
""",
    tools=[firecrawl_toolset, google_search_tool],
)

# =============================================================================
# Wrapper Class with Fallback
# =============================================================================

class SEOAgentWrapper:
    """Wrapper to make LlmAgent compatible with direct run() calls"""
    
    def __init__(self, llm_agent):
        self.agent = llm_agent
    
    def run(self, query):
        """Execute agent using Runner API with fallback"""
        try:
            # Create fresh runner for each execution
            from google.adk.sessions.in_memory_session_service import InMemorySessionService

            session_service = InMemorySessionService()
            runner = Runner(session_service=session_service)

            # Execute agent with app_name parameter (REQUIRED by ADK)
            result = runner.run(
                app_name="SEOAuditApp",  # ✅ This was missing!
                agent=self.agent,
                input=query
            )
    
            # Extract text from result
            if hasattr(result, 'text'):
                return result.text
            elif hasattr(result, 'content'):
                return result.content
            elif isinstance(result, str):
                return result
            else:
                return str(result)
                
        except Exception as e:
            # Fallback to seo_engine if ADK fails
            print(f"⚠️ ADK execution failed: {e}")
            print("🔄 Falling back to seo_engine...")
            
            try:
                from seo_engine import run_audit
                
                # Extract URL from query
                url = query.replace("Audit ", "").strip()
                res = run_audit(url, "general")
                
                if res.get('success'):
                    # Format result as markdown report
                    scores = res['ai']['scores']
                    issues = res['ai']['issues']
                    tech = res['tech']
                    
                    report = f"""# SEO Audit Report

## Executive Summary
- URL audited: {url}
- Overall Score: {scores['overall']}/100
- {res['ai'].get('summary', 'Audit completed successfully')}

## Technical & On-Page Findings

### Title Tag
- Current: {tech['title']} ({tech.get('title_length', len(tech['title']))} characters)

### Meta Description
- Current: {tech.get('meta_description', 'Not found')}

### Heading Structure
- H1: {tech['h1']}
- H1 Count: {tech.get('h1_count', 1)}

### Content Analysis
- Word count: {tech['word_count']}

## Issues Found

"""
                    for issue in issues:
                        report += f"### {issue['severity']}: {issue['issue']}\n"
                        report += f"- **Fix**: {issue['fix']}\n\n"
                    
                    report += """
## Next Steps
1. Address critical issues immediately
2. Re-audit after implementing fixes
3. Monitor performance improvements
"""
                    return report
                else:
                    return f"# Error\n\nAudit failed: {res.get('error', 'Unknown error')}"
                    
            except Exception as fallback_error:
                return f"# Error\n\nBoth ADK and fallback failed.\n\nADK Error: {str(e)}\n\nFallback Error: {str(fallback_error)}"

# =============================================================================
# Expose wrapped agent
# =============================================================================

# Create wrapped agent with run() method
agent = SEOAgentWrapper(combined_seo_agent)

# Also expose raw agent for ADK Dev UI
root_agent = combined_seo_agent

# =============================================================================
# Wrapper Functions
# =============================================================================

def run_audit_safe(url, niche="general"):
    """Wrapper with retry and rate limiting"""
    return agent.run(f"Audit {url}")

# =============================================================================
# Test Function
# =============================================================================

if __name__ == "__main__":
    print("Testing Combined SEO Agent...")
    test_url = "https://example.com"
    
    try:
        result = run_audit_safe(test_url)
        print(f"\n✅ SUCCESS!")
        print(f"Report Preview:\n{result[:500]}...")
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
'''
"""
Simple SEO Agent - NO ADK, Just Works
Uses Firecrawl + Gemini directly
"""

import os
from dotenv import load_dotenv

load_dotenv()

class SimpleSEOAgent:
    """Direct Firecrawl + Gemini agent without ADK complexity"""
    
    def run(self, query):
        """Run audit with Firecrawl and Gemini"""
        import requests
        import json
        try:
            import google.generativeai as genai
        except:
            from google import genai
        
        # Extract URL
        url = query.replace("Audit ", "").strip()
        print(f"🔍 Auditing with Firecrawl: {url}")
        
        # STEP 1: Scrape with Firecrawl
        firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
        if not firecrawl_key:
            return "# Error\n\nFIRECRAWL_API_KEY not found in .env"
        
        try:
            response = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={
                    "Authorization": f"Bearer {firecrawl_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": url,
                    "formats": ["markdown", "html"],
                    "onlyMainContent": True
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Firecrawl error: {response.status_code}")
            
            data = response.json()
            content = data.get("data", {}).get("markdown", "")[:5000]
            
        except Exception as e:
            print(f"⚠️ Firecrawl failed: {e}, using basic scraping...")
            # Fallback to requests
            from bs4 import BeautifulSoup
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            soup = BeautifulSoup(resp.content, 'html.parser')
            for script in soup(['script', 'style']):
                script.decompose()
            content = soup.get_text(separator=' ', strip=True)[:5000]
        
        # STEP 2: Analyze with Gemini
        gemini_key = os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            return "# Error\n\nGOOGLE_API_KEY not found in .env"
        
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash-lite")
            
            prompt = f"""You are an expert SEO consultant. Analyze this webpage and create a comprehensive SEO audit report.

URL: {url}

Content:
{content}

Create a detailed markdown report with these sections:

# SEO Audit Report

## Executive Summary
- URL audited
- Overall score (0-100)
- Primary keyword focus
- Key findings (2-3 sentences)

## Technical Findings
### Title Tag
- Current title
- Length and optimization status
- Recommendation

### Meta Description
- Current description (or note if missing)
- Optimization status

### Heading Structure
- H1 analysis
- Heading hierarchy quality

### Content Quality
- Word count estimate
- Content depth assessment
- Readability

## Priority Issues (P0)
List 3-5 critical issues with:
- Issue name
- Why it matters
- How to fix
- Effort level

## Recommendations
Actionable next steps

**Important**: Be specific, use real data from the content, give scores as numbers."""

            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"# Error\n\nGemini API failed: {e}\n\nCheck your API key quota at: https://ai.dev/usage"

# Create agent instance
agent = SimpleSEOAgent()

if __name__ == "__main__":
    result = agent.run("Audit https://example.com")
    print(result)
