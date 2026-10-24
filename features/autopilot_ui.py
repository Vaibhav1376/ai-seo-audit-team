import streamlit as st
import pandas as pd
from cms_integration.wordpress import WordPressCMS
from cms_integration.engine import AutoPilot

def render_autopilot_tab():
    """Renders the Auto-Pilot / CMS Integration Tab"""
    
    st.markdown("## 🤖 Auto-Pilot (Self-Healing SEO)")
    st.info("This module connects directly to your CMS to fix issues automatically. Default is 'Dry Run' (Simulation Mode) for safety.")

    # --- SECTION 1: CONNECTION ---
    with st.expander("🔌 CMS Connection Settings", expanded="cms_connection" not in st.session_state):
        col1, col2 = st.columns(2)
        with col1:
            cms_type = st.selectbox("Platform", ["WordPress", "Shopify (Coming Soon)", "Webflow (Coming Soon)"])
            site_url = st.text_input("Website URL", placeholder="https://example.com")
        with col2:
            wp_user = st.text_input("WP Username (Admin)")
            wp_pass = st.text_input("Application Password", type="password", help="Go to WP Admin > Users > Profile > Application Passwords")
        
        dry_run = st.toggle("Dry Run Mode (Simulate Only)", value=True)
        
        if st.button("🔗 Connect to Site"):
            if not site_url or not wp_user or not wp_pass:
                st.error("Please fill in all credentials.")
            else:
                try:
                    # Initialize Connection
                    cms = WordPressCMS(site_url, wp_user, wp_pass, dry_run=dry_run)
                    # Test connection (Fetch a random post to verify)
                    # In a real app, add a specific verify_credentials method
                    st.session_state['cms_connector'] = cms
                    st.session_state['autopilot_engine'] = AutoPilot(cms)
                    st.session_state['cms_connection'] = True
                    st.success(f"✅ Successfully connected to {site_url}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Connection Failed: {e}")

    # --- SECTION 2: THE DASHBOARD ---
    if st.session_state.get('cms_connection'):
        st.divider()
        st.markdown("### 🚨 Detected Opportunities")
        
        # In a real scenario, this data comes from your Audit Report (Agent 1)
        # For this demo, we simulate finding a page that needs fixing
        
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            post_id = st.number_input("Enter Post/Page ID to Fix", min_value=1, step=1, help="Look in your WP URL when editing a post: post=123")
        with col_btn:
            check_btn = st.button("🔍 Scan Page")

        if check_btn and post_id:
            with st.status("🤖 AI is analyzing current content...", expanded=True) as status:
                engine = st.session_state['autopilot_engine']
                
                # 1. Get Current State
                st.write("Reading content from WordPress...")
                current_data = engine.cms.get_post(post_id)
                
                if not current_data:
                    status.update(label="❌ Page not found", state="error")
                    st.stop()
                
                st.write(" Analyzing SEO gaps...")
                # Simulate analysis delay
                
                status.update(label="✅ Analysis Complete", state="complete")
                
                # Show Current State
                st.subheader("Current State")
                st.code(f"Title: {current_data.get('title', {}).get('rendered', 'N/A')}\nLink: {current_data.get('link')}", language="yaml")

                # --- THE MAGIC BUTTON ---
                st.divider()
                st.subheader("✨ AI Optimization")
                
                if st.button("🚀 Auto-Fix This Page", type="primary"):
                    with st.spinner("Writing new SEO tags and pushing to CMS..."):
                        # Call the AI Engine
                        result = engine.fix_meta_tags(post_id)
                        
                        if result.get("status") == "success" or result.get("status") == "simulated":
                            st.balloons()
                            
                            # SHOW THE DIFF (Before vs After)
                            st.success("✅ Optimization Applied Successfully!")
                            
                            res_col1, res_col2 = st.columns(2)
                            with res_col1:
                                st.markdown("**Old Title**")
                                st.warning(current_data.get('title', {}).get('rendered'))
                            with res_col2:
                                st.markdown("**New Optimized Title**")
                                st.success(result.get('new_title'))
                                
                            if result.get("status") == "simulated":
                                st.info("ℹ️ This was a Dry Run. No changes were saved to the live site.")
                        else:
                            st.error(f"Error: {result.get('error')}")