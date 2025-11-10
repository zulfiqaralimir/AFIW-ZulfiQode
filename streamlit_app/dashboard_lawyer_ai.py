"""
Streamlit Dashboard for Lawyer-AI v9.0
Simplified dashboard that supports PDF upload and visualizes all analysis results
"""
import streamlit as st
import requests
import pandas as pd
import time
import io

# ---------------------------
# CONFIGURATION
# ---------------------------
API_URL = "http://127.0.0.1:8000/lawyer_ai/analyze"
st.set_page_config(page_title="Lawyer-AI Financial Ethics & Risk Analyzer", layout="wide")

st.title("⚖️ Lawyer-AI Financial Ethics & Risk Analyzer (AFIW–ZulfiQode)")

st.markdown(
    "Upload a company's **annual report (PDF)** — Lawyer-AI will extract text and numeric data, "
    "fetch technical and news insights, and produce a structured analysis."
)

# ---------------------------
# FILE UPLOAD
# ---------------------------
uploaded = st.file_uploader("📂 Upload Company Annual Report (PDF)", type=["pdf"])

if uploaded:
    with st.spinner("🔍 Analyzing report — please wait..."):
        # Read PDF bytes
        pdf_bytes = uploaded.read()
        
        # Extract text from PDF (simple extraction for now)
        # In production, this would be done server-side
        try:
            import fitz
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            extracted_text = "\n".join(page.get_text("text") for page in doc)
            doc.close()
        except Exception as e:
            st.error(f"Failed to extract text from PDF: {str(e)}")
            extracted_text = ""
        
        # Get company name from filename
        company_name = uploaded.name.split('.')[0].upper()
        
        # Prepare request payload
        payload = {
            "text": extracted_text,
            "company_name": company_name,
            "include_news": True,
            "include_feedback": True,
            "include_conclusion": True,
            "use_agents": True  # Use agent orchestration
        }
        
        # Make API request
        try:
            res = requests.post(API_URL, json=payload, timeout=120)
            res.raise_for_status()
            response_data = res.json()
            
            # Extract analysis from response
            if "analysis" in response_data:
                data = response_data["analysis"]
            else:
                data = response_data
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API Error: {str(e)}")
            st.stop()

    st.success(f"✅ Analysis complete for **{company_name}**")

    # ---------------------------
    # OVERVIEW
    # ---------------------------
    st.header("📊 Overview Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    tone = data.get("tone", "neutral")
    tone_conf = data.get("tone_confidence", 0)
    col1.metric("Tone", tone.capitalize(), f"{tone_conf}%")
    
    ethical = data.get("ethical_flag", "questionable")
    ethical_conf = data.get("ethical_confidence", 0)
    col2.metric("Ethics", ethical.capitalize(), f"{ethical_conf}%")
    
    risk = data.get("risk_level", "moderate")
    risk_conf = data.get("risk_confidence", 0)
    col3.metric("Risk", risk.capitalize(), f"{risk_conf}%")
    
    auth = data.get("source_authenticity", "authentic")
    auth_conf = data.get("authenticity_confidence", 0)
    col4.metric("Source Authenticity", auth.capitalize(), f"{auth_conf}%")

    summary = data.get("summary", "No summary available")
    st.markdown(f"**Summary:** {summary}")

    # ---------------------------
    # TECHNICAL INDICATORS
    # ---------------------------
    st.header("📈 Technical Indicators (TradingView)")
    tech = data.get("technical_analysis", {})
    if tech and tech.get("technical_confidence", 0) > 0:
        st.markdown(f"**Data Source:** {tech.get('source', 'N/A')}")
        
        data_link = tech.get("data_link", "")
        if data_link:
            st.markdown(f"[🔗 View on TradingView]({data_link})")

        ma_200 = tech.get("ma_200")
        if ma_200:
            st.metric("MA-200", ma_200)
        else:
            st.info("MA-200 data not available")
            
        rsi_data = tech.get("rsi_14_last_10_days", [])
        if rsi_data:
            rsi_df = pd.DataFrame(rsi_data)
            if not rsi_df.empty and "date" in rsi_df.columns and "value" in rsi_df.columns:
                st.line_chart(rsi_df.set_index("date")["value"], height=200)
        
        trend_summary = tech.get("trend_summary", "No trend data available")
        st.markdown(f"**Trend Summary:** {trend_summary}")
    else:
        st.warning("⚠️ Technical data unavailable from TradingView.")

    # ---------------------------
    # BUSINESS CYCLE CONTEXT
    # ---------------------------
    st.header("🏦 Business-Cycle Context")
    cycle = data.get("business_cycle_context", {})
    col1, col2, col3 = st.columns(3)
    
    phase = cycle.get("current_phase", "N/A")
    phase_conf = cycle.get("phase_confidence", "")
    col1.metric("Phase", phase.capitalize(), phase_conf)
    
    alignment_score = cycle.get("cycle_alignment_score", 0)
    col2.metric("Cycle Alignment Score", alignment_score)
    
    cycle_conf = cycle.get("cycle_confidence_score", 0)
    col3.metric("Confidence", cycle_conf)
    
    interpretation = cycle.get("interpretation", "N/A")
    st.markdown(f"**Interpretation:** {interpretation}")

    # ---------------------------
    # OPERATIONAL METRICS
    # ---------------------------
    st.header("💰 Operational & Financial Metrics")
    op_metrics = data.get("operational_metrics", {})
    ocf = op_metrics.get("operational_cash_flow", {})
    gme = op_metrics.get("gross_margin_effect", {})

    col1, col2 = st.columns(2)
    
    ocf_value = ocf.get("ocf_value", "N/A")
    ocf_conf = ocf.get("ocf_confidence", 0)
    col1.metric("Operational Cash Flow", ocf_value, f"{ocf_conf}%")
    ocf_trend = ocf.get("ocf_trend", "N/A")
    ocf_interp = ocf.get("interpretation", "")
    col1.markdown(f"**Trend:** {ocf_trend}  \n**Interpretation:** {ocf_interp}")

    gme_percent = gme.get("gross_margin_percent", 0)
    gme_conf = gme.get("gme_confidence", 0)
    col2.metric("Gross Margin %", f"{gme_percent}%", f"{gme_conf}%")
    gme_trend = gme.get("gme_trend", "N/A")
    gme_interp = gme.get("interpretation", "")
    col2.markdown(f"**Trend:** {gme_trend}  \n**Interpretation:** {gme_interp}")

    # ---------------------------
    # COMPOSITE INTEGRITY INDEX
    # ---------------------------
    st.header("🧮 Composite Integrity Index (CII)")
    cii = data.get("composite_integrity_index", {})
    cii_score = cii.get("cii_score", 0)
    cii_class = cii.get("cii_class", "N/A")
    
    st.metric("CII Score", cii_score, cii_class)
    st.progress(cii_score / 100)
    
    calc_basis = cii.get("calculation_basis", "")
    st.caption(f"Calculation Basis: {calc_basis}")
    
    cii_interp = cii.get("interpretation", "")
    st.markdown(f"**Interpretation:** {cii_interp}")

    # ---------------------------
    # TEMPORAL INTEGRITY TREND
    # ---------------------------
    st.header("📆 Temporal Integrity Trend (TIT)")
    tit = data.get("temporal_integrity_trend", {})
    tit_value = tit.get("tit_value", 0)
    tit_class = tit.get("tit_class", "N/A")
    
    st.metric("ΔCII (TIT Value)", tit_value, tit_class)
    
    trend_dir = tit.get("trend_direction", "N/A")
    obs_period = tit.get("observation_period", "N/A")
    st.markdown(f"**Trend:** {trend_dir}  \n**Observation Period:** {obs_period}")
    
    tit_interp = tit.get("interpretation", "")
    st.markdown(f"**Interpretation:** {tit_interp}")

    # ---------------------------
    # FUTURE PERFORMANCE PERSPECTIVE
    # ---------------------------
    st.header("🔮 Future Performance Perspective (FPP)")
    fpp = data.get("future_performance_perspective", {})
    
    col1, col2 = st.columns(2)
    
    outlook = fpp.get("outlook", "N/A")
    fpp_conf = fpp.get("confidence", 0)
    col1.metric("Outlook", outlook.capitalize(), f"{fpp_conf}%")
    
    forward_risk = fpp.get("forward_risk_level", "N/A")
    col2.metric("Forward Risk", forward_risk.capitalize())
    
    drivers = fpp.get("drivers", [])
    if drivers:
        st.markdown(f"**Drivers:** {', '.join(drivers)}")
    
    fpp_interp = fpp.get("interpretation", "")
    st.markdown(f"**Interpretation:** {fpp_interp}")

    # ---------------------------
    # NEWS RSS FEED
    # ---------------------------
    st.header("📰 News Feed & External Signals")
    
    # Check for news in external_sources or news_rss
    news_items = []
    if "external_sources" in data:
        news_items = data["external_sources"].get("news_rss", [])
    elif "news_rss" in data:
        news_items = data["news_rss"]
    
    if news_items:
        for n in news_items:
            title = n.get("title", "No title")
            source = n.get("source", "Unknown source")
            summary = n.get("summary", "")
            link = n.get("link", "")
            published = n.get("published", "")
            
            st.markdown(f"**{title}** — *{source}*")
            if published:
                st.caption(f"Published: {published}")
            if summary:
                st.markdown(f"> {summary}")
            if link:
                st.markdown(f"[Read More]({link})")
            st.divider()
    else:
        st.info("No relevant news articles found.")

    # ---------------------------
    # HALLUCINATION & HUMAN FEEDBACK
    # ---------------------------
    st.header("🧠 Reliability & Feedback Metrics")
    
    hm = data.get("hallucination_metrics", {})
    if hm:
        col1, col2, col3, col4 = st.columns(4)
        
        bias = hm.get("bias", 0)
        col1.metric("Bias", bias)
        
        variance = hm.get("variance", 0)
        col2.metric("Variance", variance)
        
        hall_score = hm.get("hallucination_score", 0)
        col3.metric("Hallucination Score", hall_score)
        
        ci = hm.get("confidence_interval", "N/A")
        col4.metric("CI", ci)
        
        dist_shape = hm.get("distribution_shape", "N/A")
        st.markdown(f"**Distribution:** {dist_shape}")
        
        hm_interp = hm.get("interpretation", "")
        st.markdown(f"**Interpretation:** {hm_interp}")
    else:
        st.info("Hallucination metrics not available.")

    # Human Feedback
    hf = data.get("human_feedback", {})
    if hf:
        st.subheader("🗣️ Human Feedback Summary")
        hf_conclusion = hf.get("conclusion", "")
        if hf_conclusion:
            st.markdown(hf_conclusion)
        else:
            st.info("No human feedback conclusion available.")
    
    # Also check response_data for conclusion
    if "conclusion" in response_data:
        st.subheader("📝 Analysis Conclusion")
        st.markdown(response_data["conclusion"])

    # ---------------------------
    # TEMPORAL INTEGRITY TREND VISUALIZATION
    # ---------------------------
    st.header("📊 Integrity Trend Visualization")
    
    try:
        from app.integrations.plotly_visuals import render_integrity_trend
        
        # Create sample data for visualization (in production, fetch from Neo4j)
        integrity_data = {
            "date": pd.date_range(start="2024-01-01", periods=12, freq="M"),
            "CII": [cii_score] * 12,  # Use current CII score
            "TIT": [tit_value] * 12   # Use current TIT value
        }
        integrity_df = pd.DataFrame(integrity_data)
        
        fig = render_integrity_trend(integrity_df)
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.info("Plotly visuals module not available. Install required dependencies.")
    except Exception as e:
        st.warning(f"Could not render integrity trend: {str(e)}")

    st.success("✅ Full analysis rendered successfully!")

