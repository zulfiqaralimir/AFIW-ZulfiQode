"""
Financial Data Extractor
Extracts financial metrics from text and numeric data
"""
import re
import statistics
from typing import Dict, List, Optional, Tuple
from io import BytesIO
from PyPDF2 import PdfReader
import pandas as pd
from app.core.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------
# 💰 FinancialExtractor
# ---------------------------------------------------------
class FinancialExtractor:
    """
    Extracts financial metrics (OCF, Gross Margin, profitability indicators)
    from text and numeric tables inside an uploaded company annual report PDF.
    """
    
    # -----------------------------------------------------
    def extract_financial_metrics(self, text_content: str, tables: list):
        """
        Extract operational financial metrics from text and numeric tables.
        
        Args:
            text_content: Extracted text from PDF
            tables: List of extracted tables from PDF
            
        Returns:
            Dictionary with operational metrics (OCF, GME, etc.)
        """
        logger.info("💰 Extracting financial metrics from PDF text and tables.")
        text = text_content.lower()
        
        # 1️⃣ Try to find OCF from text
        ocf_value, ocf_trend = self._find_ocf(text)
        ocf_conf = 90 if ocf_value else 0
        
        # 2️⃣ Try to detect Gross Margin percentage
        gme_value, gme_trend = self._find_gross_margin(text, tables)
        gme_conf = 85 if gme_value else 0
        
        # 3️⃣ Build structured dictionary for operational metrics
        result = {
            "operational_cash_flow": {
                "ocf_value": ocf_value or "not available",
                "ocf_trend": ocf_trend,
                "ocf_confidence": ocf_conf,
                "interpretation": self._interpret_ocf(ocf_trend)
            },
            "gross_margin_effect": {
                "gross_margin_percent": gme_value or 0,
                "gme_trend": gme_trend,
                "gme_confidence": gme_conf,
                "interpretation": self._interpret_gme(gme_trend)
            }
        }
        
        logger.info("✅ Financial metrics extraction complete.")
        return result
    
    # -----------------------------------------------------
    def _find_ocf(self, text: str) -> Tuple[Optional[str], str]:
        """
        Detects Operational Cash Flow (OCF) value and trend from text lines.
        
        Args:
            text: Lowercase text content
            
        Returns:
            Tuple of (ocf_value, ocf_trend)
        """
        pattern = r"operating\s+cash\s+flow[^0-9\-]+([\-]?\d+[.,]?\d*)"
        match = re.search(pattern, text)
        
        if match:
            val = match.group(1).replace(",", "")
            numeric = float(val)
            trend = "positive" if numeric > 0 else "negative"
            return f"PKR {numeric:.2f} bn", trend
        
        # fallback keyword-based detection
        if "positive cash flow" in text:
            return "positive (undisclosed)", "positive"
        elif "negative cash flow" in text or "outflow" in text:
            return "negative (undisclosed)", "negative"
        else:
            return None, "volatile"
    
    # -----------------------------------------------------
    def _find_gross_margin(self, text: str, tables: list) -> Tuple[Optional[float], str]:
        """
        Detects Gross Margin percentage from text or tables.
        
        Args:
            text: Lowercase text content
            tables: List of extracted tables
            
        Returns:
            Tuple of (gross_margin_value, gme_trend)
        """
        # Try regex in text first
        margin_pattern = r"gross\s+margin[^0-9]+(\d{1,2}\.?\d{0,2})"
        match = re.search(margin_pattern, text)
        
        if match:
            val = float(match.group(1))
            trend = "expanding" if val > 10 else "contracting"
            return val, trend
        
        # Fallback: look in tables
        values = []
        for table in tables:
            if isinstance(table, list):
                for row in table:
                    if isinstance(row, list):
                        joined = " ".join(str(x) for x in row).lower()
                        if "gross" in joined and "margin" in joined:
                            nums = re.findall(r"(\d{1,3}\.?\d{0,2})", joined)
                            if nums:
                                try:
                                    values.extend(float(x) for x in nums)
                                except ValueError:
                                    pass
        
        if values:
            avg_margin = round(statistics.mean(values), 2)
            trend = "expanding" if avg_margin > 10 else "contracting"
            return avg_margin, trend
        
        return None, "stable"
    
    # -----------------------------------------------------
    def _interpret_ocf(self, trend: str) -> str:
        """
        Interpret OCF trend.
        
        Args:
            trend: OCF trend (positive/negative/volatile)
            
        Returns:
            Interpretation string
        """
        if trend == "positive":
            return "Company generates sustainable internal cash flows."
        elif trend == "negative":
            return "Operational liquidity pressures are evident."
        elif trend == "volatile":
            return "OCF fluctuates, possibly due to seasonal or restructuring effects."
        else:
            return "OCF status uncertain due to missing data."
    
    # -----------------------------------------------------
    def _interpret_gme(self, trend: str) -> str:
        """
        Interpret Gross Margin Effect trend.
        
        Args:
            trend: GME trend (expanding/contracting/stable)
            
        Returns:
            Interpretation string
        """
        if trend == "expanding":
            return "Improving cost management and pricing efficiency."
        elif trend == "contracting":
            return "Shrinking margins; pricing or cost inefficiency present."
        elif trend == "stable":
            return "Margins remain stable with consistent pricing performance."
        else:
            return "No clear gross margin trend identified."


# Backward compatibility functions
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts plain text from the uploaded PDF file (annual report).
    
    Args:
        pdf_bytes: PDF file as bytes
        
    Returns:
        Extracted text string
    """
    text = ""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return f"[Error extracting PDF text: {e}]"


def extract_financial_figures(pdf_text: str) -> dict:
    """
    Extracts key financial figures (Debt, Equity, Assets, Liabilities)
    from the annual report text using regex-based heuristics.
    
    Args:
        pdf_text: PDF text content
        
    Returns:
        Dictionary with extracted financial figures
    """
    # Normalize text
    clean_text = pdf_text.replace(",", "").lower()
    
    # Patterns to detect financial figures (heuristic)
    patterns = {
        "total_debt": r"total\s+debt[:\s]+([\d.]+)",
        "total_equity": r"total\s+equity[:\s]+([\d.]+)",
        "current_assets": r"current\s+assets[:\s]+([\d.]+)",
        "current_liabilities": r"current\s+liabilities[:\s]+([\d.]+)",
        "revenue": r"revenue[:\s]+([\d.]+)",
        "net_profit": r"net\s+profit[:\s]+([\d.]+)",
    }
    
    results = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, clean_text)
        if match:
            try:
                results[key] = float(match.group(1))
            except ValueError:
                results[key] = 0.0
        else:
            results[key] = 0.0
    
    return results


def extract_from_pdf_pipeline(pdf_bytes: bytes) -> dict:
    """
    Combines text extraction + financial figure parsing.
    Returns both the text and numeric data in a unified structure.
    
    Args:
        pdf_bytes: PDF file as bytes
        
    Returns:
        Dictionary with text and financials
    """
    text_data = extract_text_from_pdf(pdf_bytes)
    financials = extract_financial_figures(text_data)
    return {
        "text": text_data,
        "financials": financials
    }


# Backward compatibility function
def extract_data_from_csv(csv_bytes: bytes) -> pd.DataFrame:
    """
    Extract data from CSV file (backward compatibility).
    
    Args:
        csv_bytes: CSV file as bytes
        
    Returns:
        DataFrame with CSV data
    """
    return pd.read_csv(BytesIO(csv_bytes))
