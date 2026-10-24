import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Competitor Analysis", page_icon="🎯", layout="wide")

st.title("🎯 Competitor Tracking Dashboard")

# Initialize
if "competitors" not in st.session_state:
    st.session_state.competitors = {}

# Sidebar - Add Competitors
with st.sidebar:
    st.subheader("Add Competitor")
    
    comp_name = st.text_input("Competitor Name")
    comp_url = st.text_input("Competitor URL")
    
    if st.button("Add Competitor"):
        if comp_name and comp_url:
            st.session_state.competitors[comp_name] = {
                "url": comp_url,
                "added_date": datetime.now().isoformat(),
                "last_audit": None
            }
            
            # Save to file
            os.makedirs("competitor_data", exist_ok=True)
            with open("competitor_data/competitors.json", "w") as f:
                json.dump(st.session_state.competitors, f, indent=2)
            
            st.success(f"Added {comp_name}")
    
    st.markdown("---")
    st.subheader("Tracked Competitors")
    for name in st.session_state.competitors.keys():
        if st.button(f"🗑️ {name}", key=f"del_{name}"):
            del st.session_state.competitors[name]
            st.rerun()

# Load saved competitors
if os.path.exists("competitor_data/competitors.json"):
    with open("competitor_data/competitors.json", "r") as f:
        st.session_state.competitors = json.load(f)

# Main area
if not st.session_state.competitors:
    st.info("👈 Add competitors in the sidebar to start tracking")
else:
    # Show competitor list
    st.subheader("Competitor Overview")
    
    comp_data = []
    for name, data in st.session_state.competitors.items():
        comp_data.append({
            "Competitor": name,
            "URL": data["url"],
            "Last Audit": data.get("last_audit", "Never"),
            "Status": "🟢 Tracked" if data.get("last_audit") else "🔴 Not Audited"
        })
    
    df = pd.DataFrame(comp_data)
    st.dataframe(df, use_container_width=True)
    
    # Run comparison
    st.markdown("---")
    st.subheader("Run Comparison")
    
    your_url = st.text_input("Your Website URL", key="your_url")
    
    if st.button("🚀 Run Competitor Analysis", type="primary"):
        if your_url:
            from workflows import run_single_page_audit
            
            progress = st.progress(0)
            status = st.empty()
            
            results = {}
            
            # Audit your site
            status.text("Auditing your website...")
            progress.progress(10)
            
            report, your_audit, _ = run_single_page_audit(
                your_url,
                model=st.session_state.get("selectedmodel")
            )
            results["Your Site"] = your_audit
            
            # Audit competitors
            total = len(st.session_state.competitors)
            for i, (name, data) in enumerate(st.session_state.competitors.items()):
                status.text(f"Auditing {name}...")
                progress.progress(10 + int((i+1)/total * 80))
                
                try:
                    _, comp_audit, _ = run_single_page_audit(
                        data["url"],
                        model=st.session_state.get("selectedmodel")
                    )
                    results[name] = comp_audit
                    
                    # Update last audit
                    st.session_state.competitors[name]["last_audit"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                except Exception as e:
                    st.warning(f"Failed to audit {name}: {e}")
            
            progress.progress(100)
            status.text("Analysis complete!")
            
            # Save comparison
            with open("competitor_data/last_comparison.json", "w") as f:
                json.dump({
                    "date": datetime.now().isoformat(),
                    "results": {k: v.get("scores", {}) for k, v in results.items()}
                }, f, indent=2)
            
            st.session_state.comparison_results = results
            st.rerun()
    
    # Display comparison results
    if "comparison_results" in st.session_state:
        st.markdown("---")
        st.subheader("📊 Comparison Results")
        
        results = st.session_state.comparison_results
        
        # Score comparison table
        comparison_data = []
        for name, audit in results.items():
            scores = audit.get("scores", {})
            comparison_data.append({
                "Site": name,
                "Overall": scores.get("overall_score", 0),
                "On-Page": scores.get("onpage_score", 0),
                "Technical": scores.get("technical_score", 0),
                "Content": scores.get("content_score", 0),
                "Mobile": scores.get("mobile_score", 0)
            })
        
        df_comp = pd.DataFrame(comparison_data)
        
        # Highlight your site
        def highlight_your_site(row):
            return ['background-color: lightgreen' if row['Site'] == 'Your Site' else '' for _ in row]
        
        st.dataframe(
            df_comp.style.apply(highlight_your_site, axis=1),
            use_container_width=True
        )
        
        # Bar chart
        st.markdown("### Score Comparison")
        chart_data = df_comp.set_index("Site")[["Overall", "On-Page", "Technical", "Content", "Mobile"]]
        st.bar_chart(chart_data)
        
        # Radar chart (if plotly available)
        try:
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            categories = ["Overall", "On-Page", "Technical", "Content", "Mobile"]
            
            for _, row in df_comp.iterrows():
                fig.add_trace(go.Scatterpolar(
                    r=[row["Overall"], row["On-Page"], row["Technical"], row["Content"], row["Mobile"]],
                    theta=categories,
                    fill='toself',
                    name=row["Site"]
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title="Competitive Radar Chart"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except:
            pass
        
        # Strengths & Weaknesses
        st.markdown("---")
        st.subheader("🎯 Competitive Analysis")
        
        your_scores = results["Your Site"].get("scores", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💪 Your Strengths**")
            for metric in ["overall_score", "onpage_score", "technical_score", "content_score", "mobile_score"]:
                your_val = your_scores.get(metric, 0)
                comp_vals = [r.get("scores", {}).get(metric, 0) for r in results.values()]
                avg_comp = sum(comp_vals) / len(comp_vals) if comp_vals else 0
                
                if your_val > avg_comp:
                    st.write(f"✅ {metric.replace('_', ' ').title()}: {your_val} vs {int(avg_comp)} avg")
        
        with col2:
            st.markdown("**⚠️ Areas to Improve**")
            for metric in ["overall_score", "onpage_score", "technical_score", "content_score", "mobile_score"]:
                your_val = your_scores.get(metric, 0)
                comp_vals = [r.get("scores", {}).get(metric, 0) for r in results.values()]
                avg_comp = sum(comp_vals) / len(comp_vals) if comp_vals else 0
                
                if your_val < avg_comp:
                    gap = int(avg_comp - your_val)
                    st.write(f"❌ {metric.replace('_', ' ').title()}: {your_val} (gap: {gap})")
