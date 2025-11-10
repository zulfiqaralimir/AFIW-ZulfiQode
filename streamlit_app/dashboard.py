import streamlit as st
import requests
import pandas as pd
import time
import os
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


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


API_URL = "http://127.0.0.1:8000/lawyer_ai/analyze"
FEEDBACK_API_URL = "http://127.0.0.1:8000/lawyer_ai/feedback"
NEO4J_API_URL = "http://127.0.0.1:8000/neo4j"

st.set_page_config(page_title="AFIW–ZulfiQode | Lawyer-AI Analyzer", layout="wide")

# -----------------------------
# 🖼️ Sidebar with Logo & Navigation
# -----------------------------
with st.sidebar:
    logo_path = os.path.join("streamlit_app", "static", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        st.markdown("### 🏢 AFIW–ZulfiQode")
    st.markdown("## AFIW–ZulfiQode")
    st.markdown("_Agentic Financial Intelligence Wrapper_")
    st.markdown("**By Zulfiqar Ali Mir**")
    st.markdown("---")
    st.markdown("### 📂 Navigation")
    choice = st.radio(
        "Go to",
        ["Upload Files", "Analyze Report", "⚖️ Lawyer-AI Analysis", "📄 PDF Analysis", "🌐 Web Analysis", "📊 View Reports", "ℹ️ About"]
    )

# -----------------------------
# 📂 Upload Files
# -----------------------------
if choice == "Upload Files":
    st.title("AFIW–ZulfiQode- Financial, Ethics & Risk Analyzer (9.0)")
    
    # Purpose Section
    st.markdown("""
    ### 🎯 Purpose
    Evaluate corporate **ethics, risk, operations, and financial health** using governance data, 
    **Movement Indicators, Volatility, and National Macro Cycles**. Output is structured with 
    confidence scoring for **Neo4j, Prometheus and Grafana**.
    """)
    
    st.markdown("---")
    st.markdown("Upload a single **annual report PDF** — Lawyer-AI will analyze ethics, risk, and financial indicators automatically.")
    
    # Import shared uploader
    from utils.ui import upload_company_report, get_analysis_result, format_ethical_flag, format_metric_value

    uploaded = upload_company_report()

    if uploaded:
        # Check if analysis result already exists in session
        analysis_key = f"upload_analysis_{uploaded.name}"
        if analysis_key not in st.session_state:
            with st.spinner("🔍 Analyzing report... please wait"):
                files = {"file": (uploaded.name, uploaded, "application/pdf")}
                res = requests.post(API_URL, files=files)

            if res.status_code == 200:
                data = res.json()
                # Store analysis result in session state
                st.session_state[analysis_key] = data
                st.session_state[f"{analysis_key}_company"] = uploaded.name.split('.')[0]
            else:
                st.error(f"❌ API Error {res.status_code}: {res.text}")
                data = None
        else:
            # Use existing analysis result
            data = st.session_state[analysis_key]
            st.info("📊 Using previously analyzed results. Upload a new file to refresh.")
        
        if data:
            company_name = st.session_state.get(f"{analysis_key}_company", uploaded.name.split('.')[0])
            st.success(f"✅ Analysis complete for **{company_name}**")
            
            # Store analysis_id for feedback
            analysis_id = data.get("metadata", {}).get("analysis_id", company_name)
            st.session_state['analysis_id'] = analysis_id
            st.session_state['company_name'] = company_name
            
            # Summary
            if "summary" in data:
                st.markdown(f"**📋 Summary:** {data['summary']}")

            # -----------------------------
            # 📑 Create Tabs for Different Analyses
            # -----------------------------
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Core Metrics", 
                "👔 Management Analysis", 
                "📰 News Trend Analysis", 
                "🕸 Neo4j Graph", 
                "📋 Full Analysis"
            ])

            # -----------------------------
            # TAB 1: Core Evaluation Metrics
            # -----------------------------
            with tab1:
                # -----------------------------
                # 📊 Core Evaluation Metrics Table
                # -----------------------------
                st.header("📊 Core Evaluation Metrics")
                core_metrics = {
                    "Dimension": ["Tone", "Ethical Flag", "Risk Level", "Source Authenticity"],
                    "Value": [
                        format_metric_value(data.get("tone", "N/A")),
                        format_ethical_flag(data.get("ethical_flag", "N/A")),
                        format_metric_value(data.get("risk_level", "N/A")),
                        format_metric_value(data.get("source_authenticity", "N/A"))
                    ],
                    "Confidence": [
                        f"{data.get('tone_confidence', 0)}%",
                        f"{data.get('ethical_confidence', 0)}%",
                        f"{data.get('risk_confidence', 0)}%",
                        f"{data.get('authenticity_confidence', 0)}%"
                    ]
                }
                df_core = pd.DataFrame(core_metrics)
                st.table(df_core)
                
                # Company Feedback based on Core Metrics
                tone_val = data.get("tone", "neutral")
                ethical_val = data.get("ethical_flag", "questionable")
                risk_val = data.get("risk_level", "moderate")
                auth_val = data.get("source_authenticity", "authentic")
            
                # Explanation with Company Feedback
                st.markdown(f"""
                **💡 Understanding Core Metrics:**
                These four dimensions form the foundation of our analysis. **Tone** reflects the sentiment 
                and communication style in the report, while **Ethical Flag** indicates governance integrity. 
                **Risk Level** assesses financial and reputational exposure, and **Source Authenticity** 
                validates the reliability of the information. Together, they provide a comprehensive view 
                of the company's ethical and risk profile. **Company Feedback:** The company demonstrates a 
                **{tone_val} tone** with **{ethical_val} ethical standards** and **{risk_val} risk exposure**. 
                The **{auth_val} source authenticity** indicates {'reliable information sources' if auth_val == 'authentic' else 'potential information concerns'}.
                """)

                # -----------------------------
                # 📈 Technical Analysis Table
                # -----------------------------
                st.header("📈 Technical Analysis")
                tech = data.get("technical_analysis", {})
                tech_data = {
                    "Metric": ["Source", "MA-200", "Technical Confidence", "Trend Summary"],
                    "Value": [
                        tech.get("source", "N/A"),
                        str(tech.get("ma_200", "N/A")) if tech.get("ma_200") is not None else "Not Available",
                        f"{tech.get('technical_confidence', 0)}%",
                        tech.get("trend_summary", "N/A")
                    ]
                }
                df_tech = pd.DataFrame(tech_data)
                st.table(df_tech)
                
                # Handle missing data from investing.com and psx.com.pk
                tech_source = tech.get("source", "N/A")
                if "investing.com" not in str(tech_source).lower() and "psx.com.pk" not in str(tech_source).lower():
                    st.warning("⚠️ **Moving Average 200 (MA-200) and RSI data are missing from investing.com and psx.com.pk** for the mentioned company. This may affect technical analysis accuracy.")
                
                # RSI Data Table
                rsi_data = tech.get("rsi_14_last_10_days", [])
                if rsi_data:
                    st.subheader("RSI(14) Last 10 Days")
                    df_rsi = pd.DataFrame(rsi_data)
                    st.table(df_rsi)
                else:
                    st.info("ℹ️ RSI(14) data not available from investing.com or psx.com.pk.")
                
                # Company Feedback based on Technical Analysis
                tone_val_tech = data.get("tone", "neutral")
                risk_val_tech = data.get("risk_level", "moderate")
                cii_score_tech = data.get("composite_integrity_index", {}).get("cii_score", 0)
                
                # Explanation with Company Feedback
                st.markdown(f"""
                **💡 Understanding Technical Analysis:**
                Technical indicators like **Moving Average 200 (MA-200)** and **RSI(14)** help us understand 
                market momentum and trend direction. We source this data from **investing.com and psx.com.pk** 
                to provide accurate technical analysis. When these indicators are available, they provide valuable 
                insights into stock performance. **Company Feedback:** Based on the technical analysis, the company 
                shows a **{tone_val_tech} tone** with **{risk_val_tech} risk level**. With a CII score of **{cii_score_tech}**, 
                the company's technical indicators suggest {'strong market positioning' if cii_score_tech > 70 else 'moderate market positioning' if cii_score_tech > 50 else 'weak market positioning'}.
                """)

                # -----------------------------
                # 🔄 Business Cycle Context Table
                # -----------------------------
                st.header("🔄 Business Cycle Context")
                bc = data.get("business_cycle_context", {})
                cycle_data = {
                    "Metric": [
                        "Current Phase",
                        "Phase Confidence",
                        "Cycle Confidence Score",
                        "Cycle Alignment Score",
                        "Cycle Alignment Class",
                        "Interpretation"
                    ],
                    "Value": [
                        bc.get("current_phase", "N/A"),
                        bc.get("phase_confidence", "N/A"),
                        f"{bc.get('cycle_confidence_score', 0)}%",
                        f"{bc.get('cycle_alignment_score', 0)}%",
                        bc.get("cycle_alignment_class", "N/A"),
                        bc.get("interpretation", "N/A")
                    ]
                }
                df_cycle = pd.DataFrame(cycle_data)
                st.table(df_cycle)
                
                # Company Feedback based on Business Cycle
                phase = bc.get("current_phase", "N/A")
                alignment_score = bc.get("cycle_alignment_score", 0)
                alignment_class = bc.get("cycle_alignment_class", "N/A")
                
                # Explanation with Company Feedback
                st.markdown(f"""
                **💡 Understanding Business Cycle Context:**
                Companies don't operate in isolation—they're influenced by **national macroeconomic cycles**. 
                Our analysis aligns the company's performance with Pakistan's 10-year business cycles, showing 
                whether the company is **bullish or bearish** relative to the national economic phase. This 
                **Cycle Alignment Score** helps predict how well-positioned the company is for future growth. 
                **Company Feedback:** The company is currently in a **{phase} phase** with a **{alignment_class}** 
                alignment score of **{alignment_score}%**. This suggests {'strong alignment with national economic trends' if alignment_score > 70 else 'moderate alignment' if alignment_score > 50 else 'weak alignment with national economic trends'}.
                """)

                # -----------------------------
                # 💰 Operational Metrics Table
                # -----------------------------
                st.header("💰 Operational Metrics")
                op_metrics = data.get("operational_metrics", {})
                
                # OCF Table
                ocf = op_metrics.get("operational_cash_flow", {})
                ocf_data = {
                    "Metric": ["OCF Value", "OCF Trend", "OCF Confidence", "Interpretation"],
                    "Value": [
                        ocf.get("ocf_value", "N/A"),
                        ocf.get("ocf_trend", "N/A"),
                        f"{ocf.get('ocf_confidence', 0)}%",
                        ocf.get("interpretation", "N/A")
                    ]
                }
                df_ocf = pd.DataFrame(ocf_data)
                st.subheader("Operational Cash Flow (OCF)")
                st.table(df_ocf)
                
                # GME Table
                gme = op_metrics.get("gross_margin_effect", {})
                gme_data = {
                    "Metric": ["Gross Margin %", "GME Trend", "GME Confidence", "Interpretation"],
                    "Value": [
                        f"{gme.get('gross_margin_percent', 0)}%",
                        gme.get("gme_trend", "N/A"),
                        f"{gme.get('gme_confidence', 0)}%",
                        gme.get("interpretation", "N/A")
                    ]
                }
                df_gme = pd.DataFrame(gme_data)
                st.subheader("Gross Margin Effect (GME)")
                st.table(df_gme)
                
                # Company Feedback based on Operational Metrics
                ocf_trend = ocf.get("ocf_trend", "N/A")
                gme_trend = gme.get("gme_trend", "N/A")
                ocf_value = ocf.get("ocf_value", "N/A")
                gme_percent = gme.get("gross_margin_percent", 0)
                
                # Explanation with Company Feedback
                st.markdown(f"""
                **💡 Understanding Operational Metrics:**
                **Operational Cash Flow (OCF)** tells us if the company can sustain operations through internal 
                cash generation—a critical indicator of financial health. **Gross Margin Effect (GME)** reveals 
                pricing power and cost efficiency. Together, these metrics show whether the company has strong 
                operational fundamentals or faces cash flow challenges. **Company Feedback:** The company shows 
                **{ocf_trend} OCF** with a value of **{ocf_value}** and **{gme_trend} gross margins** at **{gme_percent}%**. 
                This indicates {'strong operational health' if ocf_trend == 'positive' and gme_trend == 'expanding' else 'moderate operational health' if ocf_trend == 'positive' or gme_trend == 'expanding' else 'operational challenges'}.
                """)

                # -----------------------------
                # 🧮 Composite Integrity Index Table
                # -----------------------------
                st.header("🧮 Composite Integrity Index (CII)")
                cii = data.get("composite_integrity_index", {})
                cii_data = {
                    "Metric": ["CII Score", "CII Class", "Calculation Basis", "Interpretation"],
                    "Value": [
                        f"{cii.get('cii_score', 0)}/100",
                        cii.get("cii_class", "N/A"),
                        cii.get("calculation_basis", "N/A"),
                        cii.get("interpretation", "N/A")
                    ]
                }
                df_cii = pd.DataFrame(cii_data)
                st.table(df_cii)
                st.progress(cii.get("cii_score", 0) / 100)
                
                # Company Feedback based on CII
                cii_score = cii.get("cii_score", 0)
                cii_class = cii.get("cii_class", "N/A")
                
                # Explanation with Company Feedback
                st.markdown(f"""
                **💡 Understanding Composite Integrity Index (CII):**
                The **CII** is our flagship metric, combining **Ethics (35%), Risk (25%), Technical (20%), and 
                Cycle Alignment (20%)**. A high CII score indicates strong ethical-financial stability, while 
                a low score suggests governance concerns. This single number helps stakeholders quickly assess 
                the company's overall integrity profile. **Company Feedback:** The company has a **CII score of {cii_score}** 
                classified as **{cii_class}**. This indicates {'excellent ethical-financial stability' if cii_score > 80 else 'good stability' if cii_score > 60 else 'moderate stability' if cii_score > 40 else 'governance concerns'}.
                """)

                # -----------------------------
                # 📆 Temporal Integrity Trend Table
                # -----------------------------
                st.header("📆 Temporal Integrity Trend (TIT)")
                tit = data.get("temporal_integrity_trend", {})
                tit_data = {
                    "Metric": [
                        "CII Previous",
                        "CII Current",
                        "TIT Value",
                        "TIT Class",
                        "Trend Direction",
                        "Observation Period",
                        "Interpretation"
                    ],
                    "Value": [
                        str(tit.get("cii_previous", "N/A")),
                        str(tit.get("cii_current", "N/A")),
                        str(tit.get("tit_value", "N/A")),
                        tit.get("tit_class", "N/A"),
                        tit.get("trend_direction", "N/A"),
                        tit.get("observation_period", "N/A"),
                        tit.get("interpretation", "N/A")
                    ]
                }
                df_tit = pd.DataFrame(tit_data)
                st.table(df_tit)
                
                # Company Feedback based on TIT
                tit_value = tit.get("tit_value", 0)
                tit_class = tit.get("tit_class", "N/A")
                trend_dir = tit.get("trend_direction", "N/A")
                
                # Explanation with Company Feedback
                st.markdown(f"""
                **💡 Understanding Temporal Integrity Trend (TIT):**
                **TIT** measures quarter-to-quarter changes in integrity by comparing current and previous 
                **CII scores**. A positive TIT means the company is improving its ethical and financial 
                standing, while a negative trend indicates deterioration. This helps identify whether 
                governance is strengthening or weakening over time. **Company Feedback:** The company shows 
                a **TIT value of {tit_value}** classified as **{tit_class}** with a **{trend_dir} trend direction**. 
                This suggests {'improving governance and financial standing' if tit_class == 'Improving' else 'stable performance' if tit_class == 'Stable' else 'declining governance and financial standing'}.
                """)

                # -----------------------------
                # 🔮 Future Performance Perspective Table
                # -----------------------------
                st.header("🔮 Future Performance Perspective (FPP)")
                fpp = data.get("future_performance_perspective", {})
                fpp_data = {
                    "Metric": ["Outlook", "Forward Risk Level", "Confidence", "Interpretation"],
                    "Value": [
                        fpp.get("outlook", "N/A"),
                        fpp.get("forward_risk_level", "N/A"),
                        f"{fpp.get('confidence', 0)}%",
                        fpp.get("interpretation", "N/A")
                    ]
                }
                df_fpp = pd.DataFrame(fpp_data)
                st.table(df_fpp)
                
                # FPP Drivers
                drivers = fpp.get("drivers", [])
                if drivers:
                    st.subheader("Key Drivers")
                    drivers_df = pd.DataFrame({"Driver": drivers})
                    st.table(drivers_df)
                
                # Company Feedback based on FPP
                outlook = fpp.get("outlook", "N/A")
                forward_risk = fpp.get("forward_risk_level", "N/A")
                fpp_confidence = fpp.get("confidence", 0)
                
                # Explanation with Company Feedback
                st.markdown(f"""
                **💡 Understanding Future Performance Perspective (FPP):**
                **FPP** provides a forward-looking assessment based on combined ethical, financial, and 
                technical indicators. It considers factors like **revenue recovery, debt reduction, and 
                regulatory support** to predict future direction. This helps stakeholders understand not 
                just where the company is now, but where it's likely heading. **Company Feedback:** The company 
                has an **{outlook} outlook** with **{forward_risk} forward risk** and **{fpp_confidence}% confidence**. 
                This suggests {'positive future prospects' if outlook == 'improving' else 'stable future prospects' if outlook == 'stable' else 'challenging future prospects'}.
                """)

                # -----------------------------
                # 🧠 Hallucination Metrics Table
                # -----------------------------
                st.header("🧠 Hallucination Metrics")
                hm = data.get("hallucination_metrics", {})
                if hm:
                    hall_data = {
                        "Metric": [
                            "Bias",
                            "Variance",
                            "Confidence Interval",
                            "Distribution Shape",
                            "Hallucination Score",
                            "Interpretation"
                        ],
                        "Value": [
                            str(hm.get("bias", "N/A")),
                            str(hm.get("variance", "N/A")),
                            hm.get("confidence_interval", "N/A"),
                            hm.get("distribution_shape", "N/A"),
                            f"{hm.get('hallucination_score', 0)}/100",
                            hm.get("interpretation", "N/A")
                        ]
                    }
                    df_hall = pd.DataFrame(hall_data)
                    st.table(df_hall)
                    
                    # Company Feedback based on Hallucination Metrics
                    hall_score = hm.get("hallucination_score", 0)
                    bias = hm.get("bias", 0)
                    variance = hm.get("variance", 0)
                    
                    # Explanation with Company Feedback
                    st.markdown(f"""
                    **💡 Understanding Hallucination Metrics:**
                    These metrics validate the **reliability and factual accuracy** of our AI analysis. 
                    **Bias** measures systematic errors, **Variance** shows output stability, and the 
                    **Hallucination Score** provides an overall reliability rating. A high score means 
                    the analysis is grounded in facts, while a low score indicates potential misinformation. 
                    **Company Feedback:** The analysis has a **Hallucination Score of {hall_score}** with 
                    **bias of {bias}** and **variance of {variance}**. This indicates {'high reliability and factual accuracy' if hall_score > 80 else 'moderate reliability' if hall_score > 60 else 'potential reliability concerns'}.
                    """)

                # -----------------------------
                # 📰 PSX News Feed Analysis
                # -----------------------------
                st.header("📰 PSX News Feed Analysis")
                news_items = []
                if "external_sources" in data and "news_rss" in data["external_sources"]:
                    news_items = data["external_sources"]["news_rss"]
                elif "news_rss" in data:
                    if isinstance(data["news_rss"], list):
                        news_items = data["news_rss"]
                    elif isinstance(data["news_rss"], dict) and "items" in data["news_rss"]:
                        news_items = data["news_rss"]["items"]
                
                if news_items:
                    news_data = []
                    for item in news_items:
                        news_data.append({
                            "Title": item.get("title", "N/A"),
                            "Source": item.get("source", "N/A"),
                            "Date": item.get("date", item.get("published", "N/A")),
                            "Sentiment": item.get("sentiment", "N/A"),
                            "Category": item.get("category", "N/A")
                        })
                    df_news = pd.DataFrame(news_data)
                    st.table(df_news)
                    
                    # News Trend Analysis
                    st.subheader("📊 News Trend Analysis")
                    sentiments = [item.get("sentiment", "neutral") for item in news_items if item.get("sentiment")]
                    if sentiments:
                        sentiment_counts = pd.Series(sentiments).value_counts()
                        st.bar_chart(sentiment_counts)
                    
                    # News Conclusion
                    if "news_rss" in data and isinstance(data["news_rss"], dict):
                        news_score = data["news_rss"].get("news_score", "N/A")
                        news_conf = data["news_rss"].get("news_confidence", "N/A")
                        st.info(f"**News Score:** {news_score}/100 | **News Confidence:** {news_conf}%")
                    
                    # Company Feedback based on News
                    positive_count = sentiments.count("positive") if sentiments else 0
                    negative_count = sentiments.count("negative") if sentiments else 0
                    neutral_count = sentiments.count("neutral") if sentiments else 0
                    total_news = len(sentiments) if sentiments else 0
                    
                    # Explanation with Company Feedback
                    st.markdown(f"""
                    **💡 Understanding PSX News Feed Analysis:**
                    We analyze **PSX (Pakistan Stock Exchange) news feeds** to understand public sentiment and 
                    trending topics related to the company. This helps identify **positive or negative news trends**, 
                    regulatory issues, or market developments that might not be reflected in the annual report. 
                    The sentiment analysis provides context for how the company is perceived in the broader market. 
                    **Company Feedback:** Out of **{total_news} news articles** analyzed from PSX, **{positive_count} are positive**, 
                    **{negative_count} are negative**, and **{neutral_count} are neutral**. This suggests {'positive market perception' if positive_count > negative_count else 'negative market perception' if negative_count > positive_count else 'neutral market perception'}.
                    """)
                else:
                    st.info("ℹ️ No news articles found from PSX. News Feed analysis will be performed when PSX news data is available.")
                    st.markdown("""
                    **💡 Understanding PSX News Feed Analysis:**
                    **PSX (Pakistan Stock Exchange) News Feed** analysis helps us understand public sentiment 
                    and trending topics. When PSX news data is available, we analyze trends and sentiment to 
                    provide additional context beyond the annual report, helping identify market perceptions and 
                    potential risks.
                    """)

                # -----------------------------
                # 👤 Human Feedback Section
                # -----------------------------
                st.header("👤 Human Feedback")
                hf = data.get("human_feedback", {})
                if hf:
                    hf_data = {
                        "Metric": [
                            "HF Quality Score",
                            "Ethics Delta",
                            "Risk Delta",
                            "Authenticity Delta"
                        ],
                        "Value": [
                            f"{hf.get('hf_quality_score', 0)}/100",
                            str(hf.get("hf_adjustments", {}).get("ethics_delta", "N/A")),
                            str(hf.get("hf_adjustments", {}).get("risk_delta", "N/A")),
                            str(hf.get("hf_adjustments", {}).get("authenticity_delta", "N/A"))
                        ]
                    }
                    df_hf = pd.DataFrame(hf_data)
                    st.table(df_hf)
                    
                    # Human Feedback Signals
                    signals = hf.get("signals", [])
                    if signals:
                        st.subheader("Feedback Signals")
                        signals_data = []
                        for sig in signals:
                            signals_data.append({
                                "Rater ID": sig.get("rater_id", "N/A"),
                                "Dimension": sig.get("dimension", "N/A"),
                                "Signal": sig.get("signal", "N/A"),
                                "Quality Weight": sig.get("q_weight", "N/A"),
                                "Comment": sig.get("comment", "N/A")
                            })
                        df_signals = pd.DataFrame(signals_data)
                        st.table(df_signals)
                    
                    # Company Feedback based on Human Feedback
                    hf_score = hf.get("hf_quality_score", 0)
                    ethics_delta = hf.get("hf_adjustments", {}).get("ethics_delta", 0)
                    risk_delta = hf.get("hf_adjustments", {}).get("risk_delta", 0)
                    
                    # Explanation with Company Feedback
                    st.markdown(f"""
                    **💡 Understanding Human Feedback:**
                    **Human feedback** allows domain experts to validate and adjust our AI analysis. The 
                    **Quality Score** reflects the overall reliability of feedback, while **Delta values** 
                    show how human input has adjusted the original metrics. This creates a **collaborative 
                    AI-human analysis** that improves accuracy over time. **Company Feedback:** The human 
                    feedback has a **Quality Score of {hf_score}** with **ethics delta of {ethics_delta}** 
                    and **risk delta of {risk_delta}**. This suggests {'strong validation from experts' if hf_score > 80 else 'moderate validation' if hf_score > 60 else 'limited expert validation'}.
                    """)
                else:
                    st.info("ℹ️ No human feedback available yet.")
                    st.markdown("""
                    **💡 Understanding Human Feedback:**
                    **Human feedback** allows domain experts to validate and improve our AI analysis. 
                    When available, feedback helps adjust metrics and provides real-world context that 
                    enhances the accuracy of our assessments.
                    """)
                
                # Human Feedback Submission Form
                st.subheader("💬 Submit Your Feedback")
                with st.form("feedback_form"):
                    feedback_type = st.selectbox(
                        "Feedback Type",
                        ["accuracy", "relevance", "completeness", "ethics", "risk", "other"]
                    )
                    feedback_score = st.slider("Quality Score (0-100)", 0, 100, 85)
                    feedback_comment = st.text_area("Your Comments", height=100, placeholder="Share your insights about this analysis...")
                    
                    submitted = st.form_submit_button("Submit Feedback")
                    
                    if submitted:
                        try:
                            feedback_payload = {
                                "analysis_id": analysis_id,
                                "feedback_type": feedback_type,
                                "feedback_data": {
                                    "score": feedback_score,
                                    "notes": "User feedback from Streamlit dashboard"
                                },
                                "comments": feedback_comment,
                                "user_id": st.session_state.get("user_id", "anonymous")
                            }
                            
                            feedback_res = requests.post(FEEDBACK_API_URL, json=feedback_payload, timeout=10)
                            
                            if feedback_res.status_code == 200:
                                st.success("✅ Feedback submitted successfully! Thank you for improving our analysis.")
                            elif feedback_res.status_code == 404:
                                # Store feedback locally if API endpoint not found
                                import json
                                feedback_dir = "feedback_data"
                                os.makedirs(feedback_dir, exist_ok=True)
                                feedback_file = os.path.join(feedback_dir, f"{analysis_id}_feedback.json")
                                with open(feedback_file, "w") as f:
                                    json.dump(feedback_payload, f, indent=2)
                                st.success("✅ Feedback saved locally! (API endpoint not available)")
                            else:
                                st.error(f"❌ Failed to submit feedback: {feedback_res.text}")
                        except requests.exceptions.RequestException as e:
                            # Store feedback locally if API is unavailable
                            try:
                                import json
                                feedback_dir = "feedback_data"
                                os.makedirs(feedback_dir, exist_ok=True)
                                feedback_file = os.path.join(feedback_dir, f"{analysis_id}_feedback.json")
                                with open(feedback_file, "w") as f:
                                    json.dump(feedback_payload, f, indent=2)
                                st.success("✅ Feedback saved locally! (API unavailable)")
                            except Exception as save_error:
                                st.error(f"❌ Error saving feedback: {str(save_error)}")
                        except Exception as e:
                            st.error(f"❌ Error submitting feedback: {str(e)}")

                # -----------------------------
                # 📝 Conclusion Section
                # -----------------------------
                st.header("📝 Analysis Conclusion")
                conclusion = data.get("conclusion", "")
                if conclusion:
                    st.markdown(f"**{conclusion}**")
                else:
                    st.info("No conclusion available.")
                
                # Company Feedback based on Conclusion
                conclusion_text = conclusion if conclusion else "No conclusion available"
                cii_score_concl = data.get("composite_integrity_index", {}).get("cii_score", 0)
                risk_val_concl = data.get("risk_level", "moderate")
                
                # Explanation with Company Feedback
                st.markdown(f"""
                **💡 Understanding the Conclusion:**
                The **conclusion** synthesizes all analytical dimensions into a clear, actionable summary. 
                It combines insights from ethics, risk, operations, technical indicators, and market context 
                to provide stakeholders with a comprehensive understanding of the company's current state 
                and future prospects. **Company Feedback:** Based on the comprehensive analysis, the company 
                shows a **CII score of {cii_score_concl}** with **{risk_val_concl} risk level**. The conclusion indicates 
                {'strong overall performance' if cii_score_concl > 70 and risk_val_concl == 'low' else 'moderate performance' if cii_score_concl > 50 else 'areas requiring attention'}.
                """)

            # -----------------------------
            # TAB 2: Management Analysis
            # -----------------------------
            with tab2:
                st.header("👔 Management Analysis")
                
                # Extract management-related metrics
                management_metrics = {
                    "Aspect": [
                        "Leadership Tone",
                        "Strategic Vision",
                        "Risk Management",
                        "Operational Efficiency",
                        "Financial Transparency",
                        "Stakeholder Communication",
                        "Governance Structure",
                        "Ethical Standards"
                    ],
                    "Assessment": [
                        str(data.get("tone", "N/A")).title(),
                        "Strong" if data.get("composite_integrity_index", {}).get("cii_score", 0) > 70 else "Moderate" if data.get("composite_integrity_index", {}).get("cii_score", 0) > 50 else "Weak",
                        str(data.get("risk_level", "N/A")).title(),
                        "Efficient" if data.get("operational_metrics", {}).get("operational_cash_flow", {}).get("ocf_trend", "") == "positive" else "Challenged",
                        "Transparent" if data.get("source_authenticity", "") == "authentic" else "Questionable",
                        "Effective" if data.get("tone_confidence", 0) > 70 else "Limited",
                        "Robust" if data.get("ethical_flag", "") == "ethical" else "Needs Improvement",
                        str(data.get("ethical_flag", "N/A")).title()
                    ],
                    "Confidence": [
                        f"{data.get('tone_confidence', 0)}%",
                        f"{data.get('composite_integrity_index', {}).get('cii_score', 0)}%",
                        f"{data.get('risk_confidence', 0)}%",
                        f"{data.get('operational_metrics', {}).get('operational_cash_flow', {}).get('ocf_confidence', 0)}%",
                        f"{data.get('authenticity_confidence', 0)}%",
                        f"{data.get('tone_confidence', 0)}%",
                        f"{data.get('ethical_confidence', 0)}%",
                        f"{data.get('ethical_confidence', 0)}%"
                    ]
                }
                
                df_management = pd.DataFrame(management_metrics)
                st.table(df_management)
                
                # Management Analysis Visualization
                st.subheader("📊 Management Confidence Scores")
                fig_management = px.bar(
                    df_management, 
                    x="Aspect", 
                    y="Confidence",
                    color="Confidence",
                    color_continuous_scale="RdYlGn",
                    title="Management Analysis Confidence Scores"
                )
                fig_management.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_management, use_container_width=True)
                
                # Overall Management Score
                avg_confidence = sum([
                    data.get('tone_confidence', 0),
                    data.get('composite_integrity_index', {}).get('cii_score', 0),
                    data.get('risk_confidence', 0),
                    data.get('operational_metrics', {}).get('operational_cash_flow', {}).get('ocf_confidence', 0),
                    data.get('authenticity_confidence', 0),
                    data.get('ethical_confidence', 0)
                ]) / 6
                
                st.metric("Overall Management Confidence", f"{avg_confidence:.1f}%")
                st.progress(avg_confidence / 100)
                
                # Explanation
                st.markdown(f"""
                **💡 Understanding Management Analysis:**
                We analyze **management performance** across eight key dimensions: **Leadership Tone**, 
                **Strategic Vision**, **Risk Management**, **Operational Efficiency**, **Financial Transparency**, 
                **Stakeholder Communication**, **Governance Structure**, and **Ethical Standards**. Each 
                dimension is assessed with a **confidence score** based on our analysis of the annual report. 
                **Company Feedback:** The company shows an **overall management confidence of {avg_confidence:.1f}%**, 
                indicating {'strong management performance' if avg_confidence > 75 else 'moderate management performance' if avg_confidence > 60 else 'areas requiring management attention'}.
                """)

            # -----------------------------
            # TAB 3: News Trend Analysis (Web Search)
            # -----------------------------
            with tab3:
                st.header("📰 News Trend Analysis (Web Search)")
                
                # Web Search for News Trends
                search_query = st.text_input(
                    "🔍 Search for company news trends",
                    value=f"{company_name} financial news",
                    help="Enter search query for web search"
                )
                
                if st.button("🔎 Search News Trends"):
                    with st.spinner("Searching web for news trends..."):
                        try:
                            # Note: Web search would need to be implemented via API endpoint
                            # For now, we'll use PSX news data as the primary source
                            st.info("💡 **Note:** Web search functionality requires API configuration. Using PSX news data for trend analysis.")
                            
                            # Get PSX news data for trend analysis
                            news_items = []
                            if "external_sources" in data and "news_rss" in data["external_sources"]:
                                news_items = data["external_sources"]["news_rss"]
                            elif "news_rss" in data:
                                if isinstance(data["news_rss"], list):
                                    news_items = data["news_rss"]
                                elif isinstance(data["news_rss"], dict) and "items" in data["news_rss"]:
                                    news_items = data["news_rss"]["items"]
                            
                            # Process news items as search results
                            search_results = []
                            if news_items:
                                for item in news_items:
                                    search_results.append({
                                        "title": item.get("title", "N/A"),
                                        "source": item.get("source", "PSX"),
                                        "snippet": item.get("summary", item.get("note", "N/A")),
                                        "date": item.get("date", item.get("published", "N/A"))
                                    })
                            
                            if search_results:
                                st.subheader("📊 News Trend Analysis Results")
                                
                                # Display search results
                                news_trends = []
                                for i, result in enumerate(search_results[:10], 1):
                                    news_trends.append({
                                        "Rank": i,
                                        "Title": result.get("title", "N/A"),
                                        "Source": result.get("source", "N/A"),
                                        "Snippet": result.get("snippet", "N/A")[:100] + "...",
                                        "Date": result.get("date", "N/A")
                                    })
                                
                                df_news_trends = pd.DataFrame(news_trends)
                                st.table(df_news_trends)
                                
                                # News Trend Visualization
                                st.subheader("📈 News Trend Timeline")
                                
                                # Create timeline chart
                                if news_trends:
                                    timeline_data = pd.DataFrame({
                                        "Date": [item.get("Date", "Unknown") for item in news_trends],
                                        "Count": [1] * len(news_trends)
                                    })
                                    
                                    fig_timeline = px.line(
                                        timeline_data.groupby("Date").sum().reset_index(),
                                        x="Date",
                                        y="Count",
                                        title="News Trend Timeline",
                                        markers=True
                                    )
                                    fig_timeline.update_layout(height=400)
                                    st.plotly_chart(fig_timeline, use_container_width=True)
                                
                                # Sentiment Analysis
                                st.subheader("📊 News Sentiment Analysis")
                                
                                # Simple sentiment analysis based on keywords
                                positive_keywords = ["growth", "profit", "success", "gain", "positive", "increase"]
                                negative_keywords = ["loss", "decline", "risk", "concern", "negative", "decrease"]
                                
                                sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
                                
                                for result in search_results:
                                    text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
                                    pos_count = sum(1 for kw in positive_keywords if kw in text)
                                    neg_count = sum(1 for kw in negative_keywords if kw in text)
                                    
                                    if pos_count > neg_count:
                                        sentiment_counts["Positive"] += 1
                                    elif neg_count > pos_count:
                                        sentiment_counts["Negative"] += 1
                                    else:
                                        sentiment_counts["Neutral"] += 1
                                
                                fig_sentiment = px.pie(
                                    values=list(sentiment_counts.values()),
                                    names=list(sentiment_counts.keys()),
                                    title="News Sentiment Distribution",
                                    color_discrete_map={"Positive": "green", "Negative": "red", "Neutral": "gray"}
                                )
                                st.plotly_chart(fig_sentiment, use_container_width=True)
                                
                                # Explanation
                                st.markdown(f"""
                                **💡 Understanding News Trend Analysis:**
                                We use **web search** to analyze news trends about the company. This helps 
                                identify **positive or negative news patterns**, regulatory issues, or market 
                                developments that might not be reflected in the annual report. The sentiment 
                                analysis provides context for how the company is perceived in the broader market. 
                                **Company Feedback:** Out of **{len(search_results)} news articles** analyzed, 
                                **{sentiment_counts['Positive']} are positive**, **{sentiment_counts['Negative']} are negative**, 
                                and **{sentiment_counts['Neutral']} are neutral**. This suggests {'positive market perception' if sentiment_counts['Positive'] > sentiment_counts['Negative'] else 'negative market perception' if sentiment_counts['Negative'] > sentiment_counts['Positive'] else 'neutral market perception'}.
                                """)
                            else:
                                st.warning("No news trends found. Please try a different search query.")
                                
                        except Exception as e:
                            st.error(f"Error searching news trends: {str(e)}")
                            st.info("💡 **Note:** Web search functionality requires proper API configuration. Using PSX news data as fallback.")
                            
                            # Fallback to PSX news
                            news_items = []
                            if "external_sources" in data and "news_rss" in data["external_sources"]:
                                news_items = data["external_sources"]["news_rss"]
                            elif "news_rss" in data:
                                if isinstance(data["news_rss"], list):
                                    news_items = data["news_rss"]
                                elif isinstance(data["news_rss"], dict) and "items" in data["news_rss"]:
                                    news_items = data["news_rss"]["items"]
                            
                            if news_items:
                                st.subheader("📰 PSX News Data (Fallback)")
                                news_data = []
                                for item in news_items:
                                    news_data.append({
                                        "Title": item.get("title", "N/A"),
                                        "Source": item.get("source", "N/A"),
                                        "Date": item.get("date", item.get("published", "N/A")),
                                        "Sentiment": item.get("sentiment", "N/A")
                                    })
                                df_news = pd.DataFrame(news_data)
                                st.table(df_news)

            # -----------------------------
            # TAB 4: Neo4j Graph Visualization
            # -----------------------------
            with tab4:
                st.header("🕸 Neo4j Graph Visualization")
                
                # Fetch Neo4j data
                try:
                    neo4j_res = requests.get(f"{NEO4J_API_URL}/company/{company_name}", timeout=5)
                    
                    if neo4j_res.status_code == 200:
                        neo4j_data = neo4j_res.json()
                        
                        st.subheader(f"📊 Company Data from Neo4j: {company_name}")
                        
                        # Display company data
                        if neo4j_data:
                            company_df = pd.DataFrame([neo4j_data])
                            st.table(company_df)
                            
                            # Create graph visualization
                            st.subheader("🕸 Neo4j Graph Structure")
                            
                            # Create network graph
                            fig = go.Figure()
                            
                            # Node positions
                            nodes = {
                                "Company": (0, 0),
                                "CII": (1, 1),
                                "Risk": (1, -1),
                                "Ethics": (-1, 1),
                                "Operations": (-1, -1)
                            }
                            
                            # Add edges
                            edges = [
                                ("Company", "CII", neo4j_data.get("CII", 0)),
                                ("Company", "Risk", 100 - (neo4j_data.get("risk", 0) if isinstance(neo4j_data.get("risk"), (int, float)) else 50)),
                                ("Company", "Ethics", 100 if neo4j_data.get("ethics") == "ethical" else 50),
                                ("Company", "Operations", 100 if neo4j_data.get("OCF") == "positive" else 50)
                            ]
                            
                            # Create network graph using plotly
                            node_x = [pos[0] for pos in nodes.values()]
                            node_y = [pos[1] for pos in nodes.values()]
                            node_text = list(nodes.keys())
                            
                            # Add edges
                            for edge in edges:
                                source, target, weight = edge
                                x0, y0 = nodes[source]
                                x1, y1 = nodes[target]
                                
                                fig.add_trace(go.Scatter(
                                    x=[x0, x1],
                                    y=[y0, y1],
                                    mode='lines',
                                    line=dict(width=weight/10, color='gray'),
                                    showlegend=False,
                                    hoverinfo='skip'
                                ))
                            
                            # Add nodes
                            fig.add_trace(go.Scatter(
                                x=node_x,
                                y=node_y,
                                mode='markers+text',
                                marker=dict(size=50, color='lightblue'),
                                text=node_text,
                                textposition="middle center",
                                name="Nodes",
                                hovertemplate="<b>%{text}</b><extra></extra>"
                            ))
                            
                            fig.update_layout(
                                title="Neo4j Company Relationship Graph",
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                height=500,
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Metrics visualization
                            st.subheader("📊 Neo4j Metrics Visualization")
                            
                            metrics_data = {
                                "Metric": ["CII", "TIT", "OCF", "GME", "HS"],
                                "Value": [
                                    neo4j_data.get("CII", 0),
                                    neo4j_data.get("TIT", 0),
                                    neo4j_data.get("OCF", 0) if isinstance(neo4j_data.get("OCF"), (int, float)) else 0,
                                    neo4j_data.get("GME", 0),
                                    neo4j_data.get("HS", 0)
                                ]
                            }
                            
                            df_metrics = pd.DataFrame(metrics_data)
                            fig_metrics = px.bar(
                                df_metrics,
                                x="Metric",
                                y="Value",
                                color="Value",
                                color_continuous_scale="RdYlGn",
                                title="Neo4j Metrics Comparison"
                            )
                            fig_metrics.update_layout(height=400)
                            st.plotly_chart(fig_metrics, use_container_width=True)
                            
                            # Explanation
                            st.markdown(f"""
                            **💡 Understanding Neo4j Graph:**
                            The **Neo4j graph** visualizes the company's relationships and metrics stored in 
                            the graph database. Each node represents a key dimension (Company, CII, Risk, Ethics, 
                            Operations), and edges show the connections between them. The graph helps identify 
                            patterns and relationships in the company's data. **Company Feedback:** The Neo4j 
                            graph shows the company's **CII of {neo4j_data.get('CII', 0)}**, **TIT of {neo4j_data.get('TIT', 0)}**, 
                            and other key metrics, providing a comprehensive view of the company's data structure.
                            """)
                        else:
                            st.info("No data found in Neo4j for this company.")
                    else:
                        st.warning("Neo4j API endpoint not available. Showing analysis data instead.")
                        
                        # Fallback: Create graph from analysis data
                        st.subheader("📊 Analysis Data Graph (Fallback)")
                        
                        # Create simple graph from analysis data
                        graph_data = {
                            "Node": ["Company", "CII", "Risk", "Ethics", "Operations"],
                            "Value": [
                                100,
                                data.get("composite_integrity_index", {}).get("cii_score", 0),
                                data.get("risk_confidence", 0),
                                data.get("ethical_confidence", 0),
                                data.get("operational_metrics", {}).get("operational_cash_flow", {}).get("ocf_confidence", 0)
                            ]
                        }
                        
                        df_graph = pd.DataFrame(graph_data)
                        fig_graph = px.bar(
                            df_graph,
                            x="Node",
                            y="Value",
                            color="Value",
                            color_continuous_scale="RdYlGn",
                            title="Analysis Data Graph"
                        )
                        fig_graph.update_layout(height=400)
                        st.plotly_chart(fig_graph, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Error fetching Neo4j data: {str(e)}")
                    st.info("💡 **Note:** Neo4j connection requires proper configuration. Showing analysis data instead.")

            # -----------------------------
            # TAB 5: Full Analysis
            # -----------------------------
            with tab5:
                st.header("📋 Full Analysis Details")
                
                # Show all sections in this tab
                st.markdown("### Complete Analysis Results")
                
                # All previous sections would go here, but for now show JSON
                with st.expander("📋 View Full JSON & Metadata"):
                    st.json(data)

            # -----------------------------
            # 📋 Metadata (Outside tabs)
            # -----------------------------

        else:
            st.error(f"❌ API Error {res.status_code}: {res.text}")

# -----------------------------
# 📄 PDF Analysis Tab
# -----------------------------
elif choice == "📄 PDF Analysis":
    from tabs import pdf_analysis
    pdf_analysis.main()

# -----------------------------
# 🌐 Web Analysis Tab
# -----------------------------
elif choice == "🌐 Web Analysis":
    from tabs import web_analysis
    web_analysis.main()

# -----------------------------
# ℹ️ About Section
# -----------------------------
elif choice == "ℹ️ About":
    st.title("ℹ️ About AFIW–ZulfiQode")
    st.markdown("""
    **AFIW–ZulfiQode** (Agentic Financial Intelligence Wrapper)  
    by **Zulfiqar Ali Mir**

    Integrates:

    - 🧠 Ethical AI for corporate governance  

    - 💹 Quantitative finance modeling  

    - 🌐 Data fusion (TradingView, SECP, PSX, RSS)  

    - 📊 Observability with Prometheus & Grafana  

    Version: **Lawyer-AI v9.0**
    """)
