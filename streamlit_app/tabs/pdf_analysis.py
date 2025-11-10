"""
PDF Analysis Tab
Upload company reports and view Lawyer-AI JSON output
"""
import streamlit as st
import os
import sys
import tempfile

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.agents.management_analyzer import ManagementAnalyzer
from utils.ui import (
    upload_company_report,
    get_analysis_result,
    set_analysis_result,
    format_ethical_flag,
    format_metric_value
)


def main():
    """
    Main function for PDF Analysis tab
    """
    st.header("📄 PDF Management Report Analysis")
    
    st.markdown("""
    Upload a company's **annual report (PDF)** and get comprehensive Lawyer-AI analysis 
    including ethics, risk, operations, and financial health assessment.
    
    **Note:** Uploaded files and analysis results persist when switching tabs.
    """)
    
    # Company name input
    company = st.text_input("Enter company name:", value="Hascol Petroleum", help="Company name for analysis")
    
    # Use shared uploader
    uploaded_file = upload_company_report()
    
    # Re-analyze button
    if "analysis_result" in st.session_state and uploaded_file:
        if st.button("🔁 Re-analyze", help="Clear current analysis and re-run"):
            from utils.ui import clear_analysis_result
            clear_analysis_result()
            st.rerun()
    
    if uploaded_file:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name
        
        try:
            # Check if analysis result already exists in session
            if "analysis_result" not in st.session_state:
                # Analyze PDF
                with st.spinner("🔍 Analyzing PDF report... please wait"):
                    analyzer = ManagementAnalyzer()
                    
                    # Use company name from input or extract from filename
                    company_name = company if company else os.path.splitext(uploaded_file.name)[0]
                    
                    result = analyzer.analyze_from_pdf(tmp_path, company_name)
                    
                    # Store result in session state
                    set_analysis_result(result)
                    st.session_state["analysis_company"] = company_name
            else:
                # Use existing analysis result
                result = get_analysis_result()
                company_name = st.session_state.get("analysis_company", company)
                st.info("📊 Using previously analyzed results. Click 'Re-analyze' to refresh.")
            
            if "error" in result:
                st.error(f"❌ Analysis Error: {result['error']}")
            else:
                st.success(f"✅ Analysis complete for **{company_name}**")
                
                # Display key metrics
                st.subheader("📊 Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                cii_score = result.get("composite_integrity_index", {}).get("cii_score", 0)
                risk_level = result.get("risk_level", "N/A")
                ethical_flag = result.get("ethical_flag", "N/A")
                tone = result.get("tone", "N/A")
                
                col1.metric("CII Score", f"{cii_score}/100")
                col2.metric("Risk Level", format_metric_value(risk_level))
                col3.metric("Ethical Flag", format_ethical_flag(ethical_flag))
                col4.metric("Tone", format_metric_value(tone))
                
                # Display full JSON
                with st.expander("📋 View Full Analysis JSON"):
                    st.json(result)
                
                # Display summary
                summary = result.get("summary", "")
                if summary:
                    st.subheader("📝 Summary")
                    st.markdown(summary)
                
                # Display conclusion
                conclusion = result.get("conclusion", "")
                if conclusion:
                    st.subheader("📝 Conclusion")
                    st.markdown(conclusion)
        
        except Exception as e:
            st.error(f"❌ Error analyzing PDF: {str(e)}")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass

