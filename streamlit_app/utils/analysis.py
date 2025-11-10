"""
Hybrid Web Intelligence Analysis
Combines live web search results with GPT analysis
"""
import streamlit as st
import requests
import json
import os
import sys
from typing import Optional, Dict, Any

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.agents.management_analyzer import ManagementAnalyzer
from app.data.websearch import WebSearch
from app.integrations.gpt_connector import GPTClient
from utils.web_search import fetch_web_results


def analyze_hybrid(company_name: str, query: str, pdf_summary: Optional[str] = None) -> Dict[str, Any]:
    """
    Hybrid Web + GPT analysis using DuckDuckGo API and OpenAI.
    
    Args:
        company_name: Company name to analyze
        query: Search query string
        pdf_summary: Optional PDF summary for context
        
    Returns:
        Analysis result dictionary
    """
    try:
        # Step 1: Fetch web results using DuckDuckGo API
        web_snippets = fetch_web_results(company_name, query)
        
        # Step 2: Build context
        context = f"""
--- Uploaded Report Summary ---
{pdf_summary or "No uploaded report"}

--- Web Search Snippets ---
{web_snippets}
"""
        
        # Step 3: GPT Analysis
        try:
            from openai import OpenAI
            import os
            
            # Get API key from secrets or environment
            api_key = st.secrets.get("openai_api_key") if hasattr(st, 'secrets') else os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                return {
                    "error": "OpenAI API key not found. Please set OPENAI_API_KEY environment variable or Streamlit secrets.",
                    "company": company_name
                }
            
            client = OpenAI(api_key=api_key)
            
            prompt = f"""
You are Lawyer-AI, a financial and ethical risk analyst.
Analyze the company: {company_name}.
Context includes report and live web info.
Determine:
- Price trend (bullish / bearish / neutral)
- RSI(14)
- MA-200
- Tone
- Risk level
- Ethical flag
- A short, factual summary.

Return your result as a JSON object:
{{
  "CII_Score": "<0-100>",
  "Risk_Level": "",
  "Ethical_Flag": "",
  "Tone": "",
  "RSI": "",
  "MA200": "",
  "Trend": "",
  "Summary": ""
}}

Context:
{context}
"""
            
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.4,
            )
            
            result = json.loads(completion.choices[0].message.content)
            result["company"] = company_name
            result["source"] = "Hybrid Web + GPT (DuckDuckGo + OpenAI)"
            
            return result
            
        except json.JSONDecodeError as e:
            import logging
            logging.error(f"GPT JSON parse error: {e}")
            return {
                "error": "GPT JSON parse error",
                "company": company_name,
                "raw": completion.choices[0].message.content if 'completion' in locals() else None
            }
        except Exception as e:
            import logging
            logging.error(f"GPT analysis failed: {e}")
            return {
                "error": f"GPT analysis failed: {str(e)}",
                "company": company_name
            }
            
    except Exception as e:
        import logging
        logging.error(f"Hybrid analysis failed: {e}")
        return {
            "error": f"Hybrid analysis failed: {str(e)}",
            "company": company_name
        }


def hybrid_web_intelligence(company_name: str, query: str, pdf_summary: Optional[str] = None) -> Dict[str, Any]:
    """
    Combine live web search results with GPT analysis (legacy function for backward compatibility).
    
    Args:
        company_name: Company name to analyze
        query: Search query string
        pdf_summary: Optional PDF summary for context
        
    Returns:
        Combined analysis result dictionary
    """
    # Use the new analyze_hybrid function
    return analyze_hybrid(company_name, query, pdf_summary)


def extract_summary_from_pdf(uploaded_file) -> Optional[str]:
    """
    Extract summary from uploaded PDF file.
    
    Args:
        uploaded_file: Uploaded file object
        
    Returns:
        PDF summary text or None
    """
    try:
        import tempfile
        import os
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name
        
        # Extract text
        from app.data.pdf_parser import extract_text_from_pdf
        text = extract_text_from_pdf(tmp_path)
        
        # Clean up
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        # Return first 2000 characters as summary
        return text[:2000] if text else None
        
    except Exception as e:
        import logging
        logging.warning(f"PDF extraction failed: {e}")
        return None

