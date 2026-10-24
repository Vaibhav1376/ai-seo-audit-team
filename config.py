"""Configuration settings"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# COMPLETE GEMINI MODEL LIST - ALL VERSIONS (1.0 → 3.0)
# ============================================================================

GEMINI_MODELS = {
    
    # ========== GEMINI 1.5 SERIES ==========
    "Gemini 1.5 Pro": "models/gemini-1.5-pro",
    "Gemini 1.5 Pro Latest": "models/gemini-1.5-pro-latest",
    "Gemini 1.5 Pro-001": "models/gemini-1.5-pro-001",
    "Gemini 1.5 Pro-002": "models/gemini-1.5-pro-002",
    "Gemini 1.5 Flash": "models/gemini-1.5-flash",
    "Gemini 1.5 Flash Latest": "models/gemini-1.5-flash-latest",
    "Gemini 1.5 Flash-001": "models/gemini-1.5-flash-001",
    "Gemini 1.5 Flash-002": "models/gemini-1.5-flash-002",
    "Gemini 1.5 Flash Lite": "models/gemini-1.5-flash-lite",
    "Gemini 1.5 Flash-8B": "models/gemini-1.5-flash-8b",
    "Gemini 1.5 Flash-8B Latest": "models/gemini-1.5-flash-8b-latest",
    
    # ========== GEMINI 2.0 SERIES ==========
    "Gemini 2.0 Flash": "models/gemini-2.0-flash",
    "Gemini 2.0 Flash Exp": "models/gemini-2.0-flash-exp",
    "Gemini 2.0 Flash Lite": "models/gemini-2.0-flash-lite",
    "Gemini 2.0 Flash Thinking Exp 1219": "models/gemini-2.0-flash-thinking-exp-1219",
    "Gemini 2.0 Flash Thinking Exp 01-21": "models/gemini-2.0-flash-thinking-exp-01-21",
    "Gemini 2.0 Pro Exp": "models/gemini-2.0-pro-exp",
    
    # ========== GEMINI 2.5 SERIES ==========
    "Gemini 2.5 Pro": "models/gemini-2.5-pro",
    "Gemini 2.5 Pro Exp": "models/gemini-2.5-pro-exp",
    "Gemini 2.5 Flash": "models/gemini-2.5-flash",
    "Gemini 2.5 Flash Exp": "models/gemini-2.5-flash-exp",
    "Gemini 2.5 Flash Lite": "models/gemini-2.5-flash-lite",
    
    # ========== GEMINI 3.0 SERIES (Latest) ==========
    "Gemini 3.0 Flash": "models/gemini-3.0-flash",
    "Gemini 3.0 Flash Exp": "models/gemini-3.0-flash-exp",
    "Gemini 3.0 Flash Lite": "models/gemini-3.0-flash-lite",
    "Gemini 3.0 Pro": "models/gemini-3.0-pro",
    "Gemini 3.0 Pro Exp": "models/gemini-3.0-pro-exp",
    "Gemini 3.0 Ultra": "models/gemini-3.0-ultra",
    
    # ========== EXPERIMENTAL MODELS ==========
    "Gemini Exp 1206": "models/gemini-exp-1206",
    "Gemini Exp 1121": "models/gemini-exp-1121",
    "Gemini Exp 1114": "models/gemini-exp-1114",
    "Gemini Exp 0827": "models/gemini-exp-0827",
    
    # ========== SPECIALIZED MODELS ==========
    "LearnLM 1.5 Pro Exp": "models/learnlm-1.5-pro-experimental",
    "Gemma 2 2B": "models/gemma-2-2b-it",
    "Gemma 2 9B": "models/gemma-2-9b-it",
    "Gemma 2 27B": "models/gemma-2-27b-it",
    
    # ========== RECOMMENDED ==========
    "⭐ Recommended (1.5 Flash)": "models/gemini-1.5-flash",
    "🚀 Latest (3.0 Flash)": "models/gemini-3.0-flash",
    "💎 Most Powerful (3.0 Ultra)": "models/gemini-3.0-ultra",
}

# Default model
DEFAULT_MODEL = "⭐ Recommended (1.5 Flash)"

MODEL_CATEGORIES = {
    "⭐ Recommended": [
        "Gemini 2.5 Flash",
        "Gemini 2.5 Pro",
    ],
    "🚀 Latest (2.0 - 3.0)": [
        "Gemini 3.0 Flash",
        "Gemini 3.0 Pro",
        "Gemini 2.5 Flash Exp",
        "Gemini 2.0 Flash Exp",
    ],
    "📦 Gemini 1.5 Series": [
        "Gemini 1.5 Flash",
        "Gemini 1.5 Flash-002",
        "Gemini 1.5 Flash-8B",
        "Gemini 1.5 Flash Lite",
        "Gemini 1.5 Pro",
        "Gemini 1.5 Pro-002",
    ],
    "⚡ Gemini 2.0 Series": [
        "Gemini 2.0 Flash",
        "Gemini 2.0 Flash Exp",
        "Gemini 2.0 Flash Lite",
        "Gemini 2.0 Pro Exp",
    ],
}

# Model info
MODEL_INFO = {
    "Gemini 1.5 Flash": {"speed": "⚡⚡⚡⚡⚡", "capability": "🧠🧠🧠🧠", "cost": "💰", "description": "⭐ Best balance"},
    "Gemini 1.5 Pro": {"speed": "⚡⚡⚡", "capability": "🧠🧠🧠🧠🧠", "cost": "💰💰💰", "description": "Most capable"},
    "Gemini 2.5 Flash": {"speed": "⚡⚡⚡⚡⚡", "capability": "🧠🧠🧠🧠", "cost": "💰💰", "description": "Fast mid-tier"},
    "Gemini 3.0 Flash": {"speed": "⚡⚡⚡⚡⚡", "capability": "🧠🧠🧠🧠🧠", "cost": "💰💰", "description": "🚀 Latest"},
    "Gemini 3.0 Pro": {"speed": "⚡⚡⚡⚡", "capability": "🧠🧠🧠🧠🧠", "cost": "💰💰💰💰", "description": "🎯 Best reasoning"},
    "Gemini 3.0 Ultra": {"speed": "⚡⚡⚡", "capability": "🧠🧠🧠🧠🧠", "cost": "💰💰💰💰💰", "description": "👑 Ultimate"},
}

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
MOZ_ACCESS_ID = os.getenv("MOZ_ACCESS_ID")
MOZ_SECRET_KEY = os.getenv("MOZ_SECRET_KEY")
DATAFORSEO_LOGIN = os.getenv("DATAFORSEO_LOGIN")
DATAFORSEO_PASSWORD = os.getenv("DATAFORSEO_PASSWORD")

# Feature flags
ENABLE_SERP_INTEGRATION = True
ENABLE_CONTENT_GAP = True
ENABLE_BACKLINKS = True
ENABLE_MOBILE_CHECK = True
ENABLE_KEYWORD_RESEARCH = True
ENABLE_INTERNAL_LINKING = True
ENABLE_COMPETITOR_TRACKING = True
ENABLE_SCHEDULED_AUDITS = True
ENABLE_AI_CONTENT_WRITER = True
ENABLE_WHITE_LABEL = True
ENABLE_MULTI_LANGUAGE = True
ENABLE_API_ACCESS = True
ENABLE_JS_RENDERING = True
ENABLE_SEASONAL_TRENDS = True

DEFAULT_BRAND = {
    "brand_name": "AI SEO Audit Pro",
    "tagline": "Professional SEO Audits Powered by Advanced AI",
    "primary_color": "#1f77b4",
    "secondary_color": "#ff7f0e",
    "accent_color": "#2ca02c",
    "logo_url": "",
    "custom_css": "",
    "footer_text": "Built with Google Gemini • Streamlit • Python",
    "show_powered_by": True
}

# ============================================================================
# AGENT CONFIGURATION (REQUIRED)
# ============================================================================

AGENT_CONFIG = {
    "temperature": 0.2,          # <--- ADD THIS LINE (Low temp for factual audits)
    "max_tokens": 4000,          # <--- Add this too just in case
    "page_auditor": {
        "name": "SEO Page Auditor",
        "role": "Technical SEO Analyst",
        "goal": "Analyze web pages for SEO issues and opportunities",
        "backstory": "Expert in technical SEO with 10+ years experience auditing websites"
    },
    "serp_analyst": {
        "name": "SERP Analyst",
        "role": "Search Results Analyst",
        "goal": "Analyze search engine results and competitor strategies",
        "backstory": "Specialist in competitive analysis and search intent understanding"
    },
    "strategy_writer": {
        "name": "SEO Strategy Writer",
        "role": "SEO Content Strategist",
        "goal": "Create actionable SEO recommendations and reports",
        "backstory": "Senior SEO consultant who translates technical data into clear strategies"
    },
    "content_analyzer": {
        "name": "Content Gap Analyzer",
        "role": "Content Analyst",
        "goal": "Identify content gaps and opportunities",
        "backstory": "Content strategist specialized in competitive content analysis"
    },
    "content_writer": {
        "name": "AI Content Writer",
        "role": "SEO Content Creator",
        "goal": "Generate SEO-optimized content outlines and articles",
        "backstory": "Professional content writer with expertise in SEO and audience engagement"
    }
}

# Niche-specific configurations
NICHE_CONFIGS = {
    "general": {
        "focus_areas": ["technical_seo", "content", "on_page", "user_experience"],
        "priority": "balanced"
    },
    "ecommerce": {
        "focus_areas": ["product_optimization", "schema_markup", "site_speed", "mobile"],
        "priority": "conversion"
    },
    "blog": {
        "focus_areas": ["content_quality", "readability", "internal_linking", "keywords"],
        "priority": "content"
    },
    "local": {
        "focus_areas": ["local_seo", "google_business", "citations", "reviews"],
        "priority": "local_visibility"
    },
    "saas": {
        "focus_areas": ["technical_seo", "conversion", "user_experience", "security"],
        "priority": "technical"
    }
}

NICHE_TEMPLATES = {
    "general": {
        "name": "General Website",
        "prompt_modifier": "Focus on overall SEO health, technical performance, and content quality.",
        "priority_checks": ["technical_seo", "on_page", "content", "mobile", "speed"],
        "target_audience": "General web users"
    },
    "ecommerce": {
        "name": "E-Commerce Store",
        "prompt_modifier": "Focus on product page optimization, conversion rate, site speed, mobile experience, and schema markup.",
        "priority_checks": ["product_optimization", "schema", "speed", "mobile", "conversion"],
        "target_audience": "Online shoppers"
    },
    "blog": {
        "name": "Blog/Content Site",
        "prompt_modifier": "Focus on content quality, readability, keyword optimization, and internal linking.",
        "priority_checks": ["content_quality", "readability", "keywords", "internal_linking"],
        "target_audience": "Readers and information seekers"
    },
    "local": {
        "name": "Local Business",
        "prompt_modifier": "Focus on local SEO signals, Google Business Profile, NAP consistency, and reviews.",
        "priority_checks": ["local_seo", "google_business", "citations", "reviews", "mobile"],
        "target_audience": "Local customers"
    },
    "saas": {
        "name": "SaaS Product",
        "prompt_modifier": "Focus on technical SEO, conversion optimization, security, and user experience.",
        "priority_checks": ["technical_seo", "conversion", "security", "ux", "landing_pages"],
        "target_audience": "B2B/B2C software users"
    },
    "news": {
        "name": "News/Magazine",
        "prompt_modifier": "Focus on article freshness, AMP, Core Web Vitals, and structured data.",
        "priority_checks": ["freshness", "amp", "core_web_vitals", "social", "schema"],
        "target_audience": "News readers"
    },
    "portfolio": {
        "name": "Portfolio Site",
        "prompt_modifier": "Focus on visual presentation, mobile responsiveness, and load speed.",
        "priority_checks": ["design", "mobile", "speed", "accessibility"],
        "target_audience": "Potential clients/employers"
    },
    "affiliate": {
        "name": "Affiliate Site",
        "prompt_modifier": "Focus on content depth, comparison tables, and trust signals.",
        "priority_checks": ["content_depth", "comparisons", "trust_signals", "conversion"],
        "target_audience": "Product researchers"
    }
}

# Niche-specific recommendations
NICHE_RECOMMENDATIONS = {
    "ecommerce": [
        "Implement product schema markup",
        "Optimize product images with WebP format",
        "Add customer reviews with schema",
        "Improve mobile checkout experience",
        "Implement breadcrumb navigation"
    ],
    "blog": [
        "Add author schema markup",
        "Implement article structured data",
        "Optimize for featured snippets",
        "Improve internal linking between posts",
        "Add social sharing buttons"
    ],
    "local": [
        "Claim and optimize Google Business Profile",
        "Ensure NAP consistency across web",
        "Build local citations",
        "Encourage customer reviews",
        "Add LocalBusiness schema"
    ],
    "saas": [
        "Optimize landing pages for conversion",
        "Implement SoftwareApplication schema",
        "Add trust badges and security indicators",
        "Optimize sign-up flow",
        "Implement proper SSL/HTTPS"
    ]
}

SCORING_WEIGHTS = {
 "has_title": 10,
    "title_length_optimal": 10,  # 50-60 chars
    "has_meta_description": 10,
    "meta_length_optimal": 10,  # 150-160 chars
    "has_h1": 15,
    "single_h1": 5,
    "has_h2": 5,
    "word_count_adequate": 15,  # 800+ words
    "internal_links": 5,
    "external_links": 5,
    "has_canonical": 5,
    "has_schema": 5,
}
