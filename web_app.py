"""
AI SEO Audit Agent - Streamlit Web Interface
Updated to work with agent.py and app.py
"""

import streamlit as st
from dotenv import load_dotenv
import os
import json
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import traceback
import time

# ============================================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================================
load_dotenv()

# ============================================================================
# 2. IMPORTS
# ============================================================================

# CMS Integration
from cms_integration.wordpress import WordPressCMS
from cms_integration.shopify import ShopifyCMS
from cms_integration.engine import AutoPilot

# Features
from features.scheduler import AuditScheduler

# Config
from config import NICHE_TEMPLATES, GEMINI_MODELS, DEFAULT_MODEL, MODEL_INFO

# Cache Manager
try:
    from utils.cache_manager import audit_cache
except ImportError:
    audit_cache = None
    print("⚠️ Cache manager not available")

# Content Intelligence
from features.content_intelligence import analyze_serp_competition, generate_content_outline
from features.commercial_apis import get_pagespeed_metrics, get_domain_authority

# Database
from utils.db_manager import save_audit_to_db, init_db as init_audit_db

# Core Logic from app.py
from app import (
    run_full_audit,
    run_batch_audit_with_features,
    run_full_site_audit_with_features,
    analyze_content_gaps,
    research_keywords_with_volumes,
    analyze_keyword_trends,
    generate_content_outline,
    generate_article,
    schedule_audit,
    get_audit_history,
    load_competitors,
    save_competitor,
    load_whitelabel_config,
    save_whitelabel_config,
    get_whitelabel_css,
    create_api_key,
    validate_api_key
)

# Feature Modules
from features.backlink_changes import detect_new_backlinks
from features.toxic_links import detect_toxic_links
from features.competitor_backlinks import analyze_competitor_backlinks
from features.competitor_discovery import discover_competitors, analyze_competitor_strength
from features.traffic_estimates import estimate_traffic, find_traffic_opportunities
from features.link_building import find_link_opportunities, create_outreach_email
from features.rank_tracking import check_multiple_keywords
from features.local_tracking import check_multi_city_rank
from features.serp_features import analyze_serp_features, find_featured_snippet_opportunity
from features.backlink_database import export_backlink_report

# Utils
from utils.pdf_generator import markdown_to_pdf as markdowntopdf
from utils.auth_manager import login_ui
from utils.db import init_db

# ============================================================================
# 3. INITIALIZATION & STATE MANAGEMENT
# ============================================================================

# Initialize Database
if 'db_init' not in st.session_state:
    init_db()
    init_audit_db()
    st.session_state['db_init'] = True

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'authenticated': False,
        'user': None,
        'firecrawl_api_key': os.getenv("FIRECRAWL_API_KEY", ""),
        'google_api_key': os.getenv("GOOGLE_API_KEY", ""),
        'serpapi_key': os.getenv("SERPAPI_KEY", ""),
        'selected_model': GEMINI_MODELS.get(DEFAULT_MODEL, "models/gemini-2.5-flash-lite"),
        'audit_history': [],
        'features_enabled': {
            # Core features only (disable expensive ones)
            "pagespeed": False,
            "image_optimization": True,
            "schema": True,
            "security": False,
            "mobile": True,
            "backlinks": False,
            "cannibalization": False,
            "roi_calculator": False,
            "content_gaps": False,
            "competitor": False,
            "broken_links": False,
            "internal_linking": True
        },
        'api_calls_today': {
            'gemini': 0,
            'firecrawl': 0,
            'google_search': 0
        }
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# Call Initialization
initialize_session_state()

# Load Branding Config
wl_config = load_whitelabel_config()

# ============================================================================
# 4. PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=wl_config.get("brand_name", "AI SEO Audit Pro"),
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS
st.markdown(get_whitelabel_css(wl_config), unsafe_allow_html=True)
st.markdown("""
<style>
    /* SaaS Market UI Tweaks */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0066CC !important;
        color: white !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Scheduler
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = AuditScheduler()
    st.session_state.scheduler.start()

# ============================================================================
# 5. AUTHENTICATION GATEKEEPER
# ============================================================================

if not st.session_state.get('authenticated', False):
    if not login_ui():
        st.info("👋 Welcome! Please log in or sign up via the sidebar to start your SEO Audit.")
        st.stop()

# User is logged in
user = st.session_state.user

# ============================================================================
# 6. SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    # Branding
    if wl_config.get("logo_path"):
        st.image(wl_config["logo_path"], width=200)
    else:
        st.markdown(f"# 🚀 {wl_config.get('brand_name', 'AI SEO Audit Pro')}")
    
    # User Profile Card
    st.success(f"👤 **{user['username']}**")
    st.info(f"💳 Credits: **{user['credits']}**")
    st.markdown("---")
    
    # API Key Inputs
    with st.expander("🔑 API Keys", expanded=not st.session_state.google_api_key):
        google_key = st.text_input("Google Gemini API", value=st.session_state.google_api_key, type="password", key="google_key_input")
        if google_key:
            st.session_state.google_api_key = google_key
            os.environ["GOOGLE_API_KEY"] = google_key
            try:
                genai.configure(api_key=google_key)
            except:
                pass
        
        st.text_input("SerpAPI Key", value=os.getenv("SERPAPI_KEY", ""), key="sidebar_serp_key", type="password")
        st.text_input("Firecrawl Key", value=os.getenv("FIRECRAWL_API_KEY", ""), key="sidebar_fire_key", type="password")
        st.text_input("Moz Access ID", value=os.getenv("MOZ_ACCESS_ID", ""), key="sidebar_moz_id")
        st.text_input("Moz Secret", value=os.getenv("MOZ_SECRET_KEY", ""), key="sidebar_moz_secret", type="password")
    
    # Model Selection
    st.subheader("🤖 AI Brain")
    selected_model_name = st.selectbox(
        "Select Model",
        options=list(GEMINI_MODELS.keys()),
        index=0
    )
    st.session_state.selected_model = GEMINI_MODELS[selected_model_name]
    
    # Niche Selection
    st.subheader("🎯 Niche")
    selected_niche = st.selectbox("Business Type", list(NICHE_TEMPLATES.keys()), format_func=lambda x: x.title())
    
    st.markdown("---")
    
    # API Usage Dashboard
    st.subheader("📊 API Usage Today")
    col1, col2 = st.columns(2)
    col1.metric("Gemini", st.session_state.api_calls_today['gemini'])
    col2.metric("Firecrawl", st.session_state.api_calls_today['firecrawl'])
    
    if st.button("Reset Counters", key="reset_api_counters"):
        st.session_state.api_calls_today = {'gemini': 0, 'firecrawl': 0, 'google_search': 0}
        st.rerun()
    
    st.markdown("---")
    
    # Feature Control
    st.subheader("🎛️ Feature Control")
    with st.expander("Advanced Features"):
        st.session_state.features_enabled['backlinks'] = st.checkbox(
            "Backlink Analysis",
            value=False,
            help="⚠️ Makes extra API calls"
        )
        st.session_state.features_enabled['competitor'] = st.checkbox(
            "Competitor Analysis",
            value=False,
            help="⚠️ Makes extra API calls"
        )
        st.session_state.features_enabled['pagespeed'] = st.checkbox(
            "PageSpeed Insights",
            value=False,
            help="⚠️ Uses Google API quota"
        )
    
    st.markdown("---")
    
    # CMS Connector
    with st.expander("🔌 CMS Connection"):
        cms_platform = st.selectbox("Platform", ["WordPress", "Shopify"])
        cms_url = st.text_input("Site URL", placeholder="https://mysite.com")
        cms_user = st.text_input("Username/Token")
        cms_pass = st.text_input("App Password", type="password")
        dry_run_mode = st.toggle("Dry Run (Safe Mode)", value=True)
        
        if st.button("Connect CMS", key="connect_cms_btn"):
            try:
                if cms_platform == "WordPress":
                    conn = WordPressCMS(cms_url, cms_user, cms_pass, dry_run=dry_run_mode)
                else:
                    conn = ShopifyCMS(cms_url, cms_pass, dry_run=dry_run_mode)
                st.session_state['autopilot'] = AutoPilot(conn)
                st.success(f"✅ Connected to {cms_platform}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

# ============================================================================
# 7. MAIN DASHBOARD UI
# ============================================================================

tabs = st.tabs([
    "🚀 Audit Central",
    "🤖 Auto-Pilot",
    "⚔️ Competitors",
    "🔑 Keywords & Content",
    "🔗 Backlinks",
    "📊 Rank Tracker",
    "⚙️ Settings"
])

# ============================================================================
# TAB 1: AUDIT CENTRAL
# ============================================================================

with tabs[0]:
    st.markdown("## 🚀 Audit Command Center")
    
    # Audit Mode Selection
    audit_mode = st.radio(
        "Select Audit Mode",
        ["Single Page", "Batch (List)", "Full Site Crawl"],
        horizontal=True,
        help="Single: Deep audit of one URL. Batch: List of URLs. Full Site: Crawl internal links."
    )
    
    st.divider()
    
    # --- MODE 1: SINGLE PAGE AUDIT ---
    if audit_mode == "Single Page":
        url_input = st.text_input("Enter URL", placeholder="https://example.com", key="single_url_input")
        
        if st.button("Run Audit 🚀", type="primary", key="single_page_audit_btn"):
            if url_input:
                # Check cache first
                cached_result = None
                if audit_cache:
                    cached_result = audit_cache.get(url_input, selected_niche)
                
                if cached_result:
                    st.info("📦 Using cached result (less than 24 hours old)")
                    result = cached_result
                else:
                    # Run audit
                    with st.spinner("🔍 Running deep analysis (15-30s)..."):
                        # Track API calls
                        st.session_state.api_calls_today['gemini'] += 1
                        st.session_state.api_calls_today['firecrawl'] += 1
                        
                        # Run audit using app.py
                        try:
                            report, result, serp_data = run_full_audit(
                                url_input,
                                selected_niche,
                                st.session_state.selected_model,
                                st.session_state.features_enabled
                            )
                            
                            if result.get('success'):
                                # Cache the result
                                if audit_cache:
                                    audit_cache.set(url_input, selected_niche, result)
                                
                                # Save to DB
                                try:
                                    score = result.get('scores', {}).get('overall_score', 0)
                                    save_audit_to_db(url_input, score, result)
                                except:
                                    pass
                            else:
                                st.error(f"❌ Audit Failed: {result.get('error')}")
                                st.stop()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            st.stop()
                
                # Display results
                if result.get('success'):
                    st.success("✅ Audit Complete")
                    
                    # Scorecard
                    c1, c2, c3 = st.columns(3)
                    scores = result.get('scores', {})
                    c1.metric("Overall Score", f"{scores.get('overall_score', 0)}/100")
                    c2.metric("Technical", f"{scores.get('technical_score', 0)}/100")
                    c3.metric("Content", f"{scores.get('content_score', 0)}/100")
                    
                    st.divider()

                    # Display Critical Issues Section
                    if result.get('technical_issues') and len(result['technical_issues']) > 0:
                        st.markdown("### 📋 Critical Issues Found")
                        
                        # Handle both dict and string formats
                        real_issues = []
                        for issue in result['technical_issues']:
                            # If issue is a dictionary
                            if isinstance(issue, dict):
                                if issue.get('issue') and len(issue.get('issue', '')) > 10:
                                    if 'See report' not in str(issue.get('fix', '')):
                                        real_issues.append(issue)
                            
                            # If issue is a string (fallback)
                            elif isinstance(issue, str) and len(issue) > 10:
                                real_issues.append({
                                    'severity': 'Medium',
                                    'issue': issue,
                                    'fix': 'See full report for details'
                                })
                        
                        if real_issues:
                            for issue in real_issues[:5]:
                                # Get severity emoji
                                severity = issue.get('severity', 'Medium') if isinstance(issue, dict) else 'Medium'
                                severity_emoji = {
                                    'Critical': '🔴',
                                    'High': '🟠',
                                    'Medium': '🟡',
                                    'Low': '🟢'
                                }.get(severity, '🔵')
                                
                                # Get issue text
                                issue_text = issue.get('issue', issue) if isinstance(issue, dict) else str(issue)
                                
                                # Display issue
                                st.markdown(f"{severity_emoji} **{severity}**: {issue_text}")
                                
                                # Display fix if available
                                if isinstance(issue, dict) and issue.get('fix'):
                                    if 'See report' not in issue['fix'] and 'See full report' not in issue['fix']:
                                        st.caption(f"💡 Fix: {issue['fix']}")
                                
                                st.markdown("")  # Spacing
                        else:
                            st.info("✅ No critical issues found. See full report for optimization opportunities.")
                    else:
                        st.info("✅ No critical issues detected.")

                    st.markdown("---")

                    # Full report
                    st.markdown("### 📊 Full Report")
                    report_text = result.get('report', result.get('ai_report', 'No report available'))
                    st.markdown(report_text)
                    
                    # Generate PDF
                    st.divider()
                    try:
                        from utils.pdf_generator import generate_pdf
                        pdf_bytes = generate_pdf(report_text)
                        
                        if pdf_bytes:
                            st.download_button(
                                "📄 Download PDF Report",
                                data=pdf_bytes,
                                file_name=f"audit_{url_input.replace('https://', '').replace('/', '_')}.pdf",
                                mime="application/pdf"
                            )
                    except Exception as e:
                        st.warning(f"PDF generation unavailable: {e}")
            else:
                st.warning("⚠️ Please enter a URL")
    
    # --- MODE 2: BATCH AUDIT ---
    elif audit_mode == "Batch (List)":
        st.info("Paste a list of URLs to audit them sequentially.")
        
        # Add delay control
        col1, col2 = st.columns([3, 1])
        urls_text = col1.text_area(
            "Enter URLs (one per line)",
            height=150,
            placeholder="https://site1.com\nhttps://site2.com"
        )
        delay_seconds = col2.number_input(
            "Delay (sec)",
            min_value=2,
            max_value=10,
            value=3,
            help="Wait time between audits to avoid rate limits"
        )
        
        if st.button("Run Batch Audit 🚀", key="batch_audit_btn"):
            urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
            
            if urls:
                progress_bar = st.progress(0)
                results_container = st.container()
                batch_data = []
                
                for i, url in enumerate(urls):
                    with results_container:
                        st.write(f"⏳ Auditing {i+1}/{len(urls)}: {url}...")
                    
                    # Check cache first
                    cached = None
                    if audit_cache:
                        cached = audit_cache.get(url, selected_niche)
                    
                    if cached:
                        score = cached.get('scores', {}).get('overall_score', 0)
                        status = "✅ Cached"
                    else:
                        try:
                            # Track API calls
                            st.session_state.api_calls_today['gemini'] += 1
                            st.session_state.api_calls_today['firecrawl'] += 1
                            
                            # Run audit
                            report, data, _ = run_full_audit(
                                url,
                                selected_niche,
                                st.session_state.selected_model,
                                {}
                            )
                            score = data.get('scores', {}).get('overall_score', 0)
                            status = "✅ Success"
                            
                            # Cache result
                            if audit_cache:
                                audit_cache.set(url, selected_niche, data)
                            
                        except Exception as e:
                            score = 0
                            status = f"❌ {str(e)[:30]}"
                    
                    batch_data.append({"URL": url, "Score": score, "Status": status})
                    progress_bar.progress((i + 1) / len(urls))
                    
                    # Wait before next audit (except last one)
                    if i < len(urls) - 1:
                        time.sleep(delay_seconds)
                
                # Show Final Table
                st.success("✅ Batch Audit Complete!")
                df = pd.DataFrame(batch_data)
                st.dataframe(df, use_container_width=True)
                
                # Export CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Results (CSV)", csv, "batch_audit.csv", "text/csv")
            else:
                st.warning("⚠️ Please enter at least one URL")
    
    # --- MODE 3: FULL SITE CRAWL ---
    elif audit_mode == "Full Site Crawl":
        st.warning("⚠️ This mode crawls internal links. It may take a few minutes.")
        
        c1, c2 = st.columns([3, 1])
        domain_input = c1.text_input("Domain to Crawl", placeholder="https://example.com")
        max_pages = c2.number_input("Max Pages", min_value=1, max_value=50, value=10)
        
        if st.button("Start Full Site Audit 🕷️", type="primary", key="full_site_audit_btn"):
            if domain_input:
                with st.status("🚀 Launching Crawler...", expanded=True) as status:
                    st.write("🕷️ Initializing crawler...")
                    
                    # Call Backend
                    res = run_full_site_audit_with_features(
                        domain_input,
                        max_pages,
                        selected_niche,
                        st.session_state.selected_model,
                        st.session_state.features_enabled
                    )
                    
                    if res.get('success'):
                        status.update(label="✅ Crawl Complete!", state="complete", expanded=False)
                        
                        # Metrics
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Pages Analyzed", res.get('pages_audited', 0))
                        
                        site_scores = res.get('site_analysis', {}).get('avg_scores', {})
                        m2.metric("Avg. Health Score", f"{site_scores.get('overall_score', 0)}/100")
                        m3.metric("Critical Issues", res.get('site_analysis', {}).get('critical_issues_count', 0))
                        
                        st.divider()
                        
                        # Display Report
                        st.markdown("### 📝 Executive Site Report")
                        report_text = res.get('site_report', "No report generated.")
                        st.markdown(report_text)
                        
                        # Download PDF
                        st.divider()
                        try:
                            pdf_bytes = markdowntopdf(report_text, wl_config.get('brand_name', 'Audit Agent'))
                            if pdf_bytes:
                                st.download_button(
                                    label="📥 Download Site Audit PDF",
                                    data=pdf_bytes,
                                    file_name="full_site_audit.pdf",
                                    mime="application/pdf"
                                )
                        except:
                            st.warning("PDF generation unavailable")
                    else:
                        status.update(label="❌ Crawl Failed", state="error")
                        st.error(f"Error: {res.get('error')}")
            else:
                st.warning("Please enter a domain")

# ============================================================================
# TAB 2: AUTO-PILOT
# ============================================================================

with tabs[1]:
    st.markdown("## 🤖 Auto-Pilot (Self-Healing SEO)")
    st.info("Directly fix SEO issues on your WordPress or Shopify site using AI.")
    
    if 'autopilot' not in st.session_state:
        st.warning("⚠️ Please connect your CMS in the Sidebar first.")
    else:
        st.success(f"✅ Connected to CMS. Mode: {'Dry Run' if st.session_state.autopilot.cms.dry_run else 'Live Action'}")
        
        col1, col2 = st.columns([3, 1])
        post_id = col1.text_input("Enter Post/Page ID to Fix", help="Found in your WP URL (e.g. post=123)")
        
        if col2.button("🔍 Analyze & Fix", key="autopilot_fix_btn"):
            if post_id:
                engine = st.session_state['autopilot']
                with st.status("🤖 AI Auto-Pilot Working...", expanded=True) as status:
                    st.write("📖 Reading content from CMS...")
                    result = engine.fix_meta_tags(post_id)
                    
                    if result.get("status") in ["success", "simulated"]:
                        status.update(label="✅ Fix Applied!", state="complete")
                        st.balloons()
                        
                        c1, c2 = st.columns(2)
                        c1.info(f"**Generated Title:**\n{result.get('generated_data', {}).get('title')}")
                        c2.success(f"**Status:** {result.get('status').upper()}")
                        
                        if result.get('status') == 'simulated':
                            st.caption("ℹ️ This was a dry run. Disable 'Dry Run' in sidebar to save changes.")
                    else:
                        status.update(label="❌ Failed", state="error")
                        st.error(result.get('error'))

# ============================================================================
# TAB 3: COMPETITORS
# ============================================================================

with tabs[2]:
    st.markdown("## ⚔️ Competitor Intelligence")
    comp_mode = st.radio("Mode", ["Compare 2 Sites", "Auto-Discover Competitors"], horizontal=True)
    
    if comp_mode == "Compare 2 Sites":
        c1, c2 = st.columns(2)
        my_url = c1.text_input("Your URL", key="comp_my_url")
        their_url = c2.text_input("Competitor URL", key="comp_their_url")
        
        if st.button("Compare Sites", key="compare_sites_btn"):
            try:
                from workflows.competitor_analysis import run_competitor_analysis
                with st.spinner("Analyzing rivalry..."):
                    st.session_state.comp_result = run_competitor_analysis(my_url, their_url, st.session_state.selected_model)
            except ImportError:
                st.error("Competitor analysis module not available")
        
        if 'comp_result' in st.session_state:
            res = st.session_state.comp_result
            st.markdown(res.get('comparison', 'No comparison available'))
            
            if res.get('comparison'):
                st.download_button(
                    label="📥 Download Competitor Analysis",
                    data=res['comparison'],
                    file_name=f"competitor_analysis.md",
                    mime="text/markdown"
                )
    else:
        disc_url = st.text_input("Your URL for Discovery")
        if st.button("Find Competitors", key="find_competitors_btn"):
            with st.spinner("Scanning SERPs..."):
                res = discover_competitors(disc_url)
                if res.get('success'):
                    for comp in res.get('top_competitors', [])[:5]:
                        st.write(f"🛑 **{comp.get('domain', 'Unknown')}**")

# ============================================================================
# TAB 4: KEYWORDS & CONTENT
# ============================================================================

with tabs[3]:
    st.markdown("## 🧠 AI Content Strategy")
    mode = st.radio("Choose Tool", ["Competitor Gap Analysis", "AI Content Writer"], horizontal=True)
    
    if mode == "Competitor Gap Analysis":
        st.info("Analyze the Top 10 Google results to find content gaps.")
        c_kw = st.text_input("Target Keyword", placeholder="e.g. sustainable energy trends")
        
        if st.button("Analyze Competition", key="analyze_comp_btn"):
            if c_kw:
                with st.spinner("Reading Top 10 Google Results..."):
                    res = analyze_serp_competition(c_kw)
                    if res.get("success"):
                        st.markdown("### 🕵️♂️ Strategic Analysis")
                        st.markdown(res.get('analysis', 'No analysis available'))
                    else:
                        st.error(f"Analysis Failed: {res.get('error')}")
            else:
                st.warning("Please enter a keyword")
    
    elif mode == "AI Content Writer":
        st.info("Generate SEO-optimized outlines.")
        topic = st.text_input("Article Topic", placeholder="e.g. How to install solar panels")
        tone = st.selectbox("Tone", ["Professional", "Casual", "Urgent", "Educational"])
        
        if st.button("Generate Outline", key="generate_outline_btn"):
            if topic:
                with st.spinner("🤖 Drafting outline..."):
                    outline = generate_content_outline(topic, None)
                    if outline and "Error" not in outline:
                        st.markdown("### 📝 AI Generated Outline")
                        st.markdown(outline)
                        st.download_button("📥 Download Outline", outline, file_name="outline.md")
                    else:
                        st.error(outline or "Failed to generate outline")
            else:
                st.warning("Please enter a topic")
# ============================================================================
# TAB 5: BACKLINKS
# ============================================================================

with tabs[4]:
    st.markdown("## 🔗 Backlink Monitor")
    bl_url = st.text_input("Target Domain", key="bl_domain")
    
    col1, col2, col3 = st.columns(3)
    
    if col1.button("Check New Links", key="check_new_links_btn"):
        res = detect_new_backlinks(bl_url)
        st.write(res)
    
    if col2.button("Audit Toxic Links", key="audit_toxic_btn"):
        res = detect_toxic_links(bl_url)
        if res.get('success'):
            st.error(f"Found {res.get('toxic_count', 0)} Toxic Links!")
    
    if col3.button("Find Opportunities", key="find_opp_btn"):
        res = find_link_opportunities(selected_niche, "guest_post")
        if res.get('success'):
            st.success(f"Found {len(res.get('opportunities', []))} Opportunities")

# ============================================================================
# TAB 6: RANK TRACKING
# ============================================================================

with tabs[5]:
    st.markdown("## 📊 Rank Tracker")
    rt_url = st.text_input("Domain to Track", key="rt_url", placeholder="example.com")
    kws = st.text_area("Keywords (one per line)", placeholder="best seo tools\nseo audit agent", key="rank_kws")
    
    if st.button("Check Rankings", type="primary", key="check_rankings_btn"):
        if rt_url and kws:
            kw_list = [k.strip() for k in kws.split('\n') if k.strip()]
            with st.spinner("🕵️ Checking Google positions..."):
                st.session_state.rank_results = check_multiple_keywords(rt_url, kw_list)
        else:
            st.warning("Please enter both a domain and at least one keyword")
    
    if 'rank_results' in st.session_state:
        res = st.session_state.rank_results
        if res.get('success'):
            c1, c2, c3 = st.columns(3)
            c1.metric("Keywords Tracked", len(res.get('results', [])))
            c2.metric("Ranked ✅", res.get('ranked_keywords', 0))
            avg_pos = res.get('average_position') or 0
            c3.metric("Avg. Position", round(avg_pos, 1))
            
            df = pd.DataFrame(res.get('results', []))
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Ranking Report (CSV)",
                data=csv,
                file_name=f"rankings_{rt_url.replace('.', '_')}.csv",
                mime="text/csv"
            )

# ============================================================================
# TAB 7: SETTINGS & BILLING
# ============================================================================

with tabs[6]:
    st.markdown("## ⚙️ Settings")
    
    # API Key Generator
    st.markdown("### 🔐 API Key Generator")
    email = st.text_input("User Email", key="api_email")
    tier = st.selectbox("Plan Tier", ["free", "pro", "agency"])
    
    if st.button("Generate Key", key="gen_api_key_btn"):
        key_res = create_api_key(email, tier)
        if key_res.get('success'):
            st.success(f"API Key: `{key_res.get('api_key', '')}`")
        else:
            st.error(f"Failed: {key_res.get('error', 'Unknown error')}")
    
    st.markdown("---")
    
    # White Labeling
    st.markdown("### 🎨 White-Label Branding")
    bn = st.text_input("Brand Name", value=wl_config.get('brand_name', 'AI SEO Audit Pro'))
    color = st.color_picker("Brand Color", value=wl_config.get('primary_color', '#0066CC'))
    
    if st.button("Save Branding", key="save_branding_btn"):
        save_whitelabel_config({"brand_name": bn, "primary_color": color})
        st.success("Saved! Refresh to see changes.")
    
    st.markdown("---")
    
    # Billing
    st.markdown("## 💳 Subscription & Billing")
    st.info(f"Current Plan: **{user.get('plan_tier', 'FREE').upper()}** | Credits: **{user.get('credits', 0)}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Starter Pack\n* **10 Credits**\n* Standard Support\n* **$29**")
        if st.button("Buy 10 Credits", key="buy_10_credits_btn"):
            try:
                from utils.billing import create_checkout_session
                url = create_checkout_session(user['id'], user.get('email', ''), "starter")
                st.link_button("Go to Secure Checkout 💳", url)
            except ImportError:
                st.error("Billing module not available")
    
    with col2:
        st.markdown("### Agency Pro\n* **100 Credits**\n* Priority Support\n* **$99**")
        if st.button("Buy 100 Credits", key="buy_100_credits_btn"):
            try:
                from utils.billing import create_checkout_session
                url = create_checkout_session(user['id'], user.get('email', ''), "agency")
                st.link_button("Go to Secure Checkout 💳", url)
            except ImportError:
                st.error("Billing module not available")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
col1, col2 = st.columns(2)
col1.caption(f"Powered by **{wl_config.get('brand_name', 'AI SEO Audit')}**")
col2.caption(f"AI Model: `{st.session_state.selected_model.replace('models/', '')}`")
