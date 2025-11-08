import streamlit as st
import requests
import os
import plotly.express as px
import pandas as pd

# ------------------------------------------------------------
# ⚙️ PAGE CONFIGURATION
# ------------------------------------------------------------
st.set_page_config(page_title="AFIW–ZulfiQode Dashboard", layout="wide")

# ------------------------------------------------------------
# 🎨 SIDEBAR: BRANDING & NAVIGATION
# ------------------------------------------------------------
with st.sidebar:
    logo_path = os.path.join("streamlit_app", "static", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)

    st.markdown(
        """
        ## **AFIW–ZulfiQode**
        *Agentic Financial Intelligence Wrapper*  
        **By Zulfiqar Ali Mir**
        """
    )

    # Navigation
    st.markdown("---")
    st.subheader("📂 Navigation")
    page = st.radio(
        "Go to Section:",
        ["📁 Upload Files", "🔍 Analyze Report", "📊 View Reports", "ℹ️ About"],
        label_visibility="collapsed",
    )

    # API Settings
    st.markdown("---")
    st.subheader("⚙️ Settings")
    api_url = st.text_input(
        "Backend API URL",
        value="http://localhost:8000/analyze",
        help="Enter backend endpoint where FastAPI server is running."
    )

# ------------------------------------------------------------
# 📄 PAGE 1: UPLOAD FILES
# ------------------------------------------------------------
if page == "📁 Upload Files":
    st.title("📁 Upload Financial Documents")
    st.markdown("Upload PDF reports and CSV data for AI-based financial and ethical analysis.")

    pdf_file = st.file_uploader("Upload PDF Report", type=["pdf"])
    csv_file = st.file_uploader("Upload CSV Financial Data", type=["csv"])

    if pdf_file:
        st.success(f"✅ {pdf_file.name} uploaded successfully.")
    if csv_file:
        st.success(f"✅ {csv_file.name} uploaded successfully.")

    st.info("Once files are uploaded, go to the **Analyze Report** section to process them.")

# ------------------------------------------------------------
# 📄 PAGE 2: ANALYZE REPORT (Enhanced)
# ------------------------------------------------------------
elif page == "🔍 Analyze Report":
    st.title("🔍 AI-Powered Ethical & Financial Report Analysis")
    st.markdown("Analyze tone, ethics, and risks in your financial statements using GPT intelligence.")

    pdf_file = st.file_uploader("Upload PDF Report", type=["pdf"])
    csv_file = st.file_uploader("Upload CSV Financial Data", type=["csv"])
    
    st.markdown("---")
    st.markdown("**Or analyze YouTube transcript from PDF:**")
    yt_pdf_file = st.file_uploader("Upload YouTube Transcript PDF", type=["pdf"], key="youtube_pdf")

    if st.button("🚀 Run Analysis", use_container_width=True):
        if not pdf_file and not csv_file:
            if yt_pdf_file:
                # Upload PDF file to YouTube analysis endpoint
                with st.spinner("🤖 Analyzing YouTube transcript with GPT-4... This may take 30-60 seconds."):
                    try:
                        files = {"pdf_file": (yt_pdf_file.name, yt_pdf_file, "application/pdf")}
                        resp = requests.post(api_url.replace("/analyze", "/analyze_youtube"), files=files, timeout=120)
                        
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success("✅ YouTube transcript analysis completed.")
                            # Reuse the same rendering pipeline as file analysis
                            summary = data.get("summary", "")
                            st.markdown("## 🧾 AI Summary (Markdown Format)")
                            formatted = summary.replace("[", "### ").replace("]", "")
                            formatted = formatted.replace("\n", "\n\n- ")
                            st.markdown(formatted, unsafe_allow_html=True)
                        else:
                            st.error(f"❌ API Error {resp.status_code}: {resp.text}")
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Request timed out. The analysis is taking longer than expected. Please try again.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"🚫 Failed to connect to API server.\n\n`{e}`")
                    except Exception as e:
                        st.error(f"❌ Error processing PDF: {str(e)}")
            else:
                st.warning("⚠️ Please upload at least one file or provide a YouTube transcript PDF.")
        else:
            with st.spinner("🤖 GPT-4 is analyzing your data... This may take 30-60 seconds."):
                files = {}
                if pdf_file:
                    files["pdf_file"] = (pdf_file.name, pdf_file, "application/pdf")
                if csv_file:
                    files["csv_file"] = (csv_file.name, csv_file, "text/csv")

                try:
                    response = requests.post(api_url, files=files, timeout=120)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Show completion message
                        st.success("✅ Analysis completed successfully!")
                        
                        # -------------------------------
                        # 🧭 Executive Summary Panel
                        # -------------------------------
                        st.markdown("## 🧭 Executive Summary")
                        summary = data.get("summary", "").strip()
                        ethical_flags = data.get("ethical_flags", {})
                        latency_ms = data.get("latency_ms", 0)

                        # Derive scores
                        # We already compute ARI below (higher = lower risk). Ethical Tone = ARI
                        # Risk Index (higher = higher risk) = 100 - ARI
                        # We'll compute here early for the panel and reuse below
                        bias_score = 0
                        halluc_rate = 0
                        count = 0
                        for _, flags in ethical_flags.items():
                            if isinstance(flags, dict):
                                bias_score += flags.get("bias_score", 0)
                                halluc_rate += 1 if flags.get("hallucination", False) else 0
                                count += 1
                        if count > 0:
                            bias_score /= count
                            halluc_rate /= count

                        def compute_ari(bias, halluc, latency):
                            latency_score = min(latency / 20000, 1)
                            ari_val = (0.5 * bias) + (0.3 * halluc) + (0.2 * latency_score)
                            return round((1 - ari_val) * 100, 2)

                        ethical_tone_score = compute_ari(bias_score, halluc_rate, latency_ms)
                        risk_index_score = round(100 - ethical_tone_score, 2)

                        # Verdict
                        if ethical_tone_score > 80:
                            verdict = "Low Ethical Risk"
                        elif ethical_tone_score > 60:
                            verdict = "Moderate Transparency"
                        else:
                            verdict = "High Governance Concern"

                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("Overall Ethical Tone Score", f"{ethical_tone_score}/100")
                        with c2:
                            st.metric("Risk Index Score", f"{risk_index_score}/100")
                        with c3:
                            st.metric("Summary Verdict", verdict)

                        # Concise AI summary (2–3 lines)
                        if summary:
                            lines = [ln.strip() for ln in summary.splitlines() if ln.strip()]
                            short_summary = " ".join(lines[:3])
                            st.markdown(f"**AI Summary:** {short_summary}")

                        # -------------------------------
                        # 🧾 AI-Generated Markdown Summary (full)
                        # -------------------------------
                        st.markdown("## 🧾 AI Summary (Markdown Format)")
                        formatted = summary.replace("[", "### ").replace("]", "")
                        formatted = formatted.replace("\n", "\n\n- ")
                        st.markdown(formatted, unsafe_allow_html=True)

                        # -------------------------------
                        # ⚖️ Extract Ethical Flags
                        # -------------------------------
                        ethical_flags = data.get("ethical_flags", {})

                        # -------------------------------
                        # 🚨 Highlight Red Flags (Tone & Ethics)
                        # -------------------------------
                        st.markdown("## 🚨 Flag Status")
                        for task, flags in ethical_flags.items():
                            if task in ("tone_analysis", "ethical_risk_check"):
                                is_red = False
                                if isinstance(flags, str):
                                    is_red = flags.lower().startswith("red")
                                elif isinstance(flags, dict):
                                    is_red = (
                                        flags.get("status", "").lower().startswith("red")
                                        or flags.get("bias_score", 0) > 0
                                        or bool(flags.get("hallucination", False))
                                    )
                                color = "red" if is_red else "green"
                                label = "RED FLAG" if is_red else "Clear"
                                task_title = task.replace("_", " ").title()
                                st.markdown(
                                    f"<b style='color:{color}'>{task_title}: {label}</b>",
                                    unsafe_allow_html=True,
                                )
                                # If there is a specific reason from backend, show it in one line
                                if isinstance(flags, dict):
                                    reason = str(flags.get("reason", "")).strip()
                                    if reason:
                                        st.markdown(
                                            f"<span style='color:#b22222;'>↳ {reason}</span>",
                                            unsafe_allow_html=True,
                                        )

                        # -------------------------------
                        # 🧮 AI Risk Index (ARI)
                        # -------------------------------
                        ari = ethical_tone_score
                        st.markdown("## 🧮 AI Risk Index (ARI)")
                        st.metric("Composite Ethical Score", f"{ari}/100", help="Higher = lower ethical risk")

                        if ari > 80:
                            st.success("✅ Excellent Ethical Performance")
                        elif ari > 60:
                            st.warning("⚠️ Moderate Risk Detected")
                        else:
                            st.error("🔴 High Ethical Risk")

                        # -------------------------------
                        # 🧩 GPT Insight Agent
                        # -------------------------------
                        st.markdown("### 💬 GPT Insight Agent")
                        insight_prompt = f"""
                        You are an AI ethics auditor.
                        Given these metrics:
                        - Bias Score = {bias_score:.2f}
                        - Hallucination Rate = {halluc_rate:.2f}
                        - Latency (ms) = {latency_ms}
                        Provide 3 concise bullet-point insights explaining why bias or hallucination may be high,
                        and suggest clear mitigation steps.
                        """

                        try:
                            insight_resp = requests.post(
                                "http://localhost:8000/insight", json={"prompt": insight_prompt}
                            )
                            insight_text = insight_resp.json().get("insight", "")
                        except Exception:
                            insight_text = "Insight service unavailable — please ensure the backend route `/insight` is running."

                        # -------------------------------
                        # 🧭 Drill-Down Tabs
                        # -------------------------------
                        st.markdown("## 🧭 Detailed Breakdown")
                        tab1, tab2, tab3 = st.tabs(["🧮 Bias Detail", "⚠️ Hallucination Detail", "📘 Ethical Notes"])

                        with tab1:
                            st.subheader("Bias Detail by Task")
                            for task, flags in ethical_flags.items():
                                if isinstance(flags, dict):
                                    bias = flags.get('bias_score', 0)
                                    halluc = bool(flags.get('hallucination', False))
                                    status = str(flags.get('status', ''))
                                    reason = str(flags.get('reason', '')).strip()
                                    task_title = task.replace('_', ' ').title()

                                    # Primary line with score
                                    st.markdown(f"- **{task_title}** → Bias Score: {bias}")

                                    # One-line explanation per type
                                    explanation = "No bias signals detected."
                                    if bias > 0 and halluc:
                                        explanation = "Detected bias signals and potential hallucination indicators in the response."
                                    elif bias > 0:
                                        explanation = "Detected bias signals in language (risk keywords present)."
                                    elif halluc:
                                        explanation = "Potential hallucination indicators found (uncertain/boilerplate phrases)."
                                    if reason:
                                        explanation = reason
                                    elif status.lower().startswith('red') and explanation == "No bias signals detected.":
                                        explanation = "Ethical risk flagged for this task; review content for issues."

                                    st.markdown(f"  <span style='color:gray;'>↳ {explanation}</span>", unsafe_allow_html=True)

                        with tab2:
                            st.subheader("Hallucination Detail")
                            for task, flags in ethical_flags.items():
                                if isinstance(flags, dict):
                                    h = flags.get("hallucination", False)
                                    st.markdown(f"- **{task.title()}** → {'⚠️ Yes' if h else '✅ No'}")

                        with tab3:
                            st.subheader("Ethical Notes from GPT Insight Agent")
                            st.markdown(insight_text)

                        # -------------------------------
                        # ⏱️ Latency Display
                        # -------------------------------
                        color = "green" if latency_ms < 8000 else "orange" if latency_ms < 15000 else "red"
                        st.markdown(
                            f"<p style='color:{color};font-weight:bold;'>⏱️ Latency: {latency_ms} ms</p>",
                            unsafe_allow_html=True,
                        )

                    else:
                        st.error(f"❌ API Error {response.status_code}: {response.text}")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The analysis is taking longer than expected. Please try again or check your OpenAI API key.")
                except requests.exceptions.RequestException as e:
                    st.error(f"🚫 Failed to connect to API server.\n\n`{e}`")

# ------------------------------------------------------------
# 📄 PAGE 3: VIEW REPORTS (Interactive Visual Analytics)
# ------------------------------------------------------------
elif page == "📊 View Reports":
    st.title("📊 Data Insights & Visual Analytics")
    st.markdown("Visualize bias trends, hallucination rates, and latency patterns across reports.")

    # Mock Data (replace later with backend data)
    data = {
        "Report": [f"Report {i}" for i in range(1, 7)],
        "Bias Score": [0.2, 0.5, 0.1, 0.3, 0.4, 0.6],
        "Hallucination Rate": [0.1, 0.3, 0.05, 0.2, 0.15, 0.25],
        "Latency (ms)": [4500, 7200, 6200, 8100, 9600, 11000],
    }
    df = pd.DataFrame(data)

    # 📈 Bias Chart
    st.subheader("🧮 Bias Score Across Reports")
    fig_bias = px.bar(df, x="Report", y="Bias Score", color="Bias Score",
                      text_auto=True, color_continuous_scale="sunset", title="Bias Score Trend")
    fig_bias.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_bias, use_container_width=True)

    # ⚠️ Hallucination Trend
    st.subheader("⚠️ Hallucination Rate Overview")
    fig_hall = px.line(df, x="Report", y="Hallucination Rate", markers=True,
                       title="Hallucination Trend Over Time")
    fig_hall.update_traces(line=dict(width=3))
    st.plotly_chart(fig_hall, use_container_width=True)

    # ⏱️ Latency Distribution
    st.subheader("⏱️ Latency Distribution")
    fig_latency = px.scatter(df, x="Report", y="Latency (ms)", size="Bias Score",
                             color="Latency (ms)", hover_name="Report",
                             title="Latency vs Bias Visualization",
                             color_continuous_scale="tealrose")
    fig_latency.update_layout(height=400)
    st.plotly_chart(fig_latency, use_container_width=True)

    # Summary Table
    st.markdown("### 📋 Summary Table")
    st.dataframe(df.style.highlight_max(axis=0, color="lightgreen"))

    st.info("📘 Future: Connect with AuraDB for live trend analytics and persistent history.")

# ------------------------------------------------------------
# 📄 PAGE 4: ABOUT
# ------------------------------------------------------------
elif page == "ℹ️ About":
    st.title("ℹ️ About AFIW–ZulfiQode")
    st.markdown("""
    ### 💡 What is AFIW–ZulfiQode?
    **AFIW–ZulfiQode** stands for *Agentic Financial Intelligence Wrapper*,  
    an AI-powered platform developed by **Zulfiqar Ali Mir** that blends ethical reasoning,  
    financial analytics, and AI agent systems using **LangGraph** and **GPT models**.

    ### 🧩 Key Features:
    - Ethical Risk Detection & Bias Auditing  
    - AI-powered Financial Summaries (Markdown Ready)  
    - Latency-aware Processing Metrics  
    - CSV + PDF Document Analysis  
    - Scalable API Integration with FastAPI backend  

    ### 🛠️ Tech Stack:
    - **Frontend:** Streamlit  
    - **Backend:** FastAPI + LangGraph + GPT-4  
    - **Database:** AuraDB (Neo4j)  
    - **Auth:** JWT & Role-Based Access  
    - **Deployment:** Vercel + Docker + Azure  

    ### 👤 Developer:
    - **Zulfiqar Ali Mir**  
      Data Analyst | AI Researcher | LLM Trainer  
      *Turing · Mir Global Soft · Google Gen Scholar (APAC 2025–26)*  
    """)

# ------------------------------------------------------------
# 🪶 FOOTER
# ------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; font-size:13px; color:gray;'>
        © 2025 <strong>Zulfiqar Ali Mir</strong> · AFIW–ZulfiQode  
        💼 Powered by GPT-4 & LangGraph | Designed for Ethical AI in Finance
    </div>
    """,
    unsafe_allow_html=True,
)
