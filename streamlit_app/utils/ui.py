"""
Streamlit UI utilities for file upload and session state management
"""
import streamlit as st
import tempfile
import os
from typing import Optional, Dict, Any


def upload_company_report() -> Optional[Any]:
    """
    Shared uploader that stores files in session state.
    Ensures file persists when switching tabs.
    
    Returns:
        Uploaded file object or None
    """
    # Check if file already exists in session
    uploaded_file = st.file_uploader(
        "📄 Upload company report (PDF)",
        type=["pdf"],
        key="company_report_uploader"
    )
    
    # If uploaded now, store it in session
    if uploaded_file is not None:
        st.session_state["uploaded_report"] = uploaded_file
        st.session_state["uploaded_report_name"] = uploaded_file.name
        st.success(f"✅ Uploaded: {uploaded_file.name}")
    elif "uploaded_report" in st.session_state:
        uploaded_file = st.session_state["uploaded_report"]
        st.info(f"📄 Using previously uploaded file: {st.session_state.get('uploaded_report_name', 'Unknown')}")
    
    return uploaded_file


def save_uploaded_file(uploaded_file) -> str:
    """
    Save uploaded file to temporary directory for persistence.
    
    Args:
        uploaded_file: Uploaded file object
        
    Returns:
        Path to saved file
    """
    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.session_state["uploaded_file_path"] = path
    return path


def get_analysis_result() -> Optional[Dict[str, Any]]:
    """
    Get analysis result from session state.
    
    Returns:
        Analysis result dictionary or None
    """
    return st.session_state.get("analysis_result")


def set_analysis_result(result: Dict[str, Any]) -> None:
    """
    Store analysis result in session state.
    
    Args:
        result: Analysis result dictionary
    """
    st.session_state["analysis_result"] = result


def clear_analysis_result() -> None:
    """
    Clear analysis result from session state.
    """
    if "analysis_result" in st.session_state:
        del st.session_state["analysis_result"]


def clear_uploaded_file() -> None:
    """
    Clear uploaded file from session state.
    """
    if "uploaded_report" in st.session_state:
        del st.session_state["uploaded_report"]
    if "uploaded_report_name" in st.session_state:
        del st.session_state["uploaded_report_name"]
    if "uploaded_file_path" in st.session_state:
        # Optionally delete temp file
        try:
            os.unlink(st.session_state["uploaded_file_path"])
        except:
            pass
        del st.session_state["uploaded_file_path"]


def format_ethical_flag(ethical_flag: Any) -> str:
    """
    Format ethical flag for display, handling boolean, string, or None values.
    
    Args:
        ethical_flag: Ethical flag value (can be bool, str, or None)
        
    Returns:
        Formatted string for display
    """
    if ethical_flag is True:
        return "Ethical"
    elif ethical_flag is False:
        return "Unethical"
    elif ethical_flag is None:
        return "Unknown"
    else:
        return str(ethical_flag).title()


def format_metric_value(value: Any, default: str = "N/A") -> str:
    """
    Format metric value for display, handling various types.
    
    Args:
        value: Value to format (can be bool, str, int, float, or None)
        default: Default value if None
        
    Returns:
        Formatted string for display
    """
    if value is None:
        return default
    elif isinstance(value, bool):
        return "Yes" if value else "No"
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return str(value).title()

