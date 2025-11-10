"""
🌐 Lawyer-AI (AFIW–ZulfiQode)
Web Intelligence Analysis — Hybrid Web + GPT
v9.0.3
"""

import streamlit as st
import json
import os
from pathlib import Path
from openai import OpenAI
from utils.ui import upload_company_report
from utils.web_search import fetch_web_results
import plotly.express as px
import pandas as pd

import plotly.express as px
import pandas as pd

def create_metrics_dashboard(res, company_name):
    """
    Creates a simple Plotly dashboard for company-level metrics.
    Used in Web Analysis tab for visual summary.
    """
    if not isinstance(res, dict):
        return None

    metrics = {
        "Metric": ["Ethics", "Risk", "CII", "TIT"],
        "Value": [
            res.get("ethical_confidence", 0),
            res.get("risk_confidence", 0),
            res.get("composite_integrity_index", {}).get("cii_score", 0),
            res.get("temporal_integrity_trend", {}).get("tit_value", 0)
        ]
    }

    df = pd.DataFrame(metrics)
    fig = px.bar(
        df,
        x="Metric",
        y="Value",
        color="Value",
        color_continuous_scale="RdYlGn",
        title=f"{company_name} — Comprehensive Metrics Dashboard"
    )
    fig.update_layout(height=400)
    return fig

# ============================================================
# 📊 Metrics Dashboard Creator
# ============================================================
def create_metrics_dashboard(res, company_name):
    """
    Creates a simple Plotly dashboard for company-level metrics.
    Used in Web Analysis tab for visual summary.
    """
    if not isinstance(res, dict):
        return None

    metrics = {
        "Metric": ["Ethics", "Risk", "CII", "TIT"],
        "Value": [
            res.get("ethical_confidence", 0),
            res.get("risk_confidence", 0),
            res.get("composite_integrity_index", {}).get("cii_score", 0),
            res.get("temporal_integrity_trend", {}).get("tit_value", 0)
        ]
    }

    df = pd.DataFrame(metrics)
    fig = px.bar(
        df,
        x="Metric",
        y="Value",
        color="Value",
        color_continuous_scale="RdYlGn",
        title=f"{company_name} — Comprehensive Metrics Dashboard"
    )
    fig.update_layout(height=400)
    return fig


# ============================================================
# 🔑 Safe API Key Loader
# ============================================================
def get_openai_key():
    """Safely get OpenAI API key from secrets or environment variable."""
    try:
        # Only access st.secrets if a secrets.toml file exists anywhere valid
        possible_paths = [
            Path.home() / ".streamlit" / "secrets.toml",
            Path.cwd() / ".streamlit" / "secrets.toml",
            Path.cwd() / "streamlit_app" / ".streamlit" / "secrets.toml",
        ]
        secrets_file_exists = any(p.exists() for p in possible_paths)

        if secrets_file_exists:
            return st.secrets.get("openai_api_key")
    except Exception:
        # Don't let StreamlitSecretNotFoundError stop execution
        pass

    # Fallback to environment variable
    return os.getenv("OPENAI_API_KEY")


# ============================================================
# 🧠 2. Hybrid Web + GPT Analyzer
# ============================================================
def analyze_hybrid(company_name: str, query: str, pdf_summary: str | None = None):
    """Hybrid Web + GPT analysis with enforced JSON output."""
    # 1️⃣ Fetch live web data
    web_snippets = fetch_web_results(company_name, query)
    
    # 2️⃣ Show what GPT actually gets (for verification)
    with st.expander("📰 View Web Sources", expanded=False):
        st.write(web_snippets)

    # 3️⃣ Combine with report (web snippets as primary evidence)
    prompt = f"""
You are Lawyer-AI, a financial ethics and risk analyst.
Base your conclusions *primarily* on the following recent web information
and use the uploaded report only as background.

Return a valid JSON object with:
CII_Score, Risk_Level, Ethical_Flag, Tone, RSI, MA200, Trend, Summary.

--- Web Search Snippets ---
{web_snippets}

--- Uploaded Report Summary ---
{pdf_summary or "No report uploaded."}
"""

    # 4️⃣ Pass context to GPT
    # Use the helper to get the key
    api_key = get_openai_key()

    if not api_key:
        st.error(
            "❌ No OpenAI API key found.\n\n"
            "Please either:\n"
            "1️⃣  Create `.streamlit/secrets.toml` with `openai_api_key = \"sk-...\"`, or\n"
            "2️⃣  Set environment variable `OPENAI_API_KEY`."
        )
        st.stop()
        return {"error": "No OpenAI API key found"}
    
    # Use the new OpenAI client interface
    client = OpenAI(api_key=api_key)
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    
    result = json.loads(completion.choices[0].message.content)
    return result


# ============================================================
# 🧩 3. Streamlit Main Tab
# ============================================================
def main():
    st.header("🌐 Web Intelligence Analysis (Hybrid)")
    st.caption("Combine uploaded report data with live web intelligence and GPT reasoning.")

    # ---- Mode Selection ----
    mode = st.radio(
        "Analysis Mode:",
        ["Hybrid Web + GPT", "GPT only", "Local only"],
        horizontal=True,
        key="analysis_mode_web"
    )

    # ---- Upload Section (persistent) ----
    uploaded_file = upload_company_report()

    # ---- Query Input ----
    query = st.text_input(
        "Custom search query (optional):",
        "what is its price trend and RSI MA 200",
        key="custom_query_web"
    )

    # ---- Company ----
    company_name = st.text_input("Company name:", "Hascol Petroleum", key="company_name_web")

    # ---- Run Button ----
    if st.button("🔍 Run Analysis", use_container_width=True):
        with st.spinner("Analyzing... please wait"):
            pdf_summary = "Summary extracted from uploaded report" if uploaded_file else None

            if mode == "Hybrid Web + GPT":
                result = analyze_hybrid(company_name, query, pdf_summary)
            elif mode == "GPT only":
                result = analyze_hybrid(company_name, "", pdf_summary)
            else:
                result = {"Summary": "Local analysis not yet implemented."}

            st.session_state["web_analysis_result"] = result

    # ---- Display Results ----
    if "web_analysis_result" in st.session_state:
        res = st.session_state["web_analysis_result"]

        st.success(f"✅ Analysis complete for **{company_name}**")

        # --- Create Tabs for Different Views ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard", 
            "📈 Technical Analysis", 
            "🎯 Metrics Overview",
            "📋 Raw Data"
        ])

        with tab1:
            st.subheader("📊 Comprehensive Metrics Dashboard")
            
            # Main Dashboard
            dashboard_fig = create_metrics_dashboard(res, company_name)
            st.plotly_chart(dashboard_fig, use_container_width=True)
            
            # Summary Chart
            st.subheader("📊 Key Metrics Summary")
            summary_fig = create_summary_chart(res)
            st.plotly_chart(summary_fig, use_container_width=True)
            
            # Key Metrics Cards
            st.subheader("📊 Key Metrics")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("CII Score", res.get("CII_Score", "0/100"))
            c2.metric("Risk Level", res.get("Risk_Level", "N/A"))
            c3.metric("Ethical Flag", res.get("Ethical_Flag", "N/A"))
            c4.metric("Tone", res.get("Tone", "N/A"))

        with tab2:
            st.subheader("📈 Technical Indicators Analysis")
            
            # Technical Indicators Dashboard
            rsi = res.get("RSI", "50")
            ma200 = res.get("MA200", "0")
            trend = res.get("Trend", "neutral")
            
            tech_fig = create_technical_indicators(rsi, ma200, trend)
            st.plotly_chart(tech_fig, use_container_width=True)
            
            # Technical Metrics
            st.subheader("📈 Technical Indicators")
            t1, t2, t3 = st.columns(3)
            t1.metric("RSI", res.get("RSI", "N/A"))
            t2.metric("MA-200", res.get("MA200", "N/A"))
            t3.metric("Trend", res.get("Trend", "N/A"))

        with tab3:
            st.subheader("🎯 Detailed Metrics Analysis")
            
            # CII Score Gauge
            col1, col2 = st.columns(2)
            with col1:
                cii_fig = create_cii_gauge(res.get("CII_Score", 0), company_name)
                st.plotly_chart(cii_fig, use_container_width=True)
            
            # Risk Distribution
            with col2:
                risk_fig = create_risk_distribution(res.get("Risk_Level", "Medium"))
                st.plotly_chart(risk_fig, use_container_width=True)
            
            # Ethics-Risk Matrix
            ethics_fig = create_ethics_risk_matrix(
                res.get("Ethical_Flag", "Questionable"),
                res.get("Risk_Level", "Medium")
            )
            st.plotly_chart(ethics_fig, use_container_width=True)
            
            # Summary
            st.subheader("📝 Summary")
            st.write(res.get("Summary", "No summary available."))

        with tab4:
            st.subheader("📋 Raw Analysis Data")
            st.json(res)
            
            # Download JSON
            json_str = json.dumps(res, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"{company_name}_analysis.json",
                mime="application/json"
            )


# ============================================================
# 🚀 Run (for standalone debug)
# ============================================================
if __name__ == "__main__":
    print("✅ create_metrics_dashboard loaded successfully")
    main()
