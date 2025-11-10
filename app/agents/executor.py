"""
Executor Agent — Lawyer-AI v9.1
--------------------------------
Extracts textual + numeric data from a single uploaded PDF,
and enriches it with live TradingView indicators and News RSS.
"""
import io
import pdfplumber
import fitz  # PyMuPDF
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.data.news_rss import NewsRSSFeed
from app.data.trading_view import TradingViewFetcher
from app.data.extractor import FinancialExtractor
from app.core.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------
# ⚙️ ExecutorAgent
# ---------------------------------------------------------
class ExecutorAgent:
    """
    Extracts textual and numeric information from a company's annual report PDF,
    enriches with TradingView and News RSS data, and returns a raw data dictionary.
    """
    
    def __init__(self):
        self.news = NewsRSSFeed()
        self.trading = TradingViewFetcher()
        self.extractor = FinancialExtractor()
    
    # -----------------------------------------------------
    def execute(self, file_bytes: bytes, plan: dict) -> dict:
        logger.info("🚀 ExecutorAgent started data extraction.")
        
        text_content, numeric_data = self._extract_from_pdf(file_bytes)
        
        # Get company name from plan
        # Plan is a list of dicts with "step" and "content" keys
        # The "content" should be the filename
        company_name = "Unknown Company"
        if isinstance(plan, list) and len(plan) > 0:
            first_item = plan[0]
            if isinstance(first_item, dict) and "content" in first_item:
                filename = first_item["content"]
                company_name = filename.split('.')[0].upper() if filename else "Unknown Company"
        elif isinstance(plan, dict):
            company_name = plan.get("company_name", plan.get("company", "Unknown Company"))
        
        # Fetch external data
        technical_data = self._fetch_trading_data(company_name)
        news_data = self._fetch_news(company_name)
        
        # Extract internal financial metrics
        operational_metrics = self.extractor.extract_financial_metrics(text_content, numeric_data)
        
        # Combine everything into a single structure
        data = {
            "company_name": company_name,
            "text_content": text_content[:3000],  # short preview for audit
            "operational_metrics": operational_metrics,
            "technical_analysis": technical_data,
            "news_rss": news_data,
        }
        
        logger.info(f"📦 Executor output keys: {list(data.keys())}")
        return data
    
    # -----------------------------------------------------
    def _extract_from_pdf(self, file_bytes: bytes):
        """
        Extracts all text and numeric tables from the uploaded PDF.
        """
        text = ""
        tables = []
        
        try:
            # Extract text
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text("text")
            
            # Extract numeric tables
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        tables.append(table)
            
            logger.info(f"📘 Extracted {len(tables)} tables and {len(text)} characters of text.")
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
        
        return text, tables
    
    # -----------------------------------------------------
    def _fetch_trading_data(self, company_name: str) -> dict:
        """
        Gets RSI(14), MA-200, and trend summary from TradingView.
        """
        try:
            result = self.trading.fetch(company_name)
            logger.info(f"📈 TradingView data fetched for {company_name}")
            return result
        except Exception as e:
            logger.warning(f"TradingView fetch failed: {e}")
            return {
                "source": "TradingView",
                "rsi_14_last_10_days": [],
                "ma_200": None,
                "trend_summary": "not available",
                "data_link": "not available",
                "technical_confidence": 0
            }
    
    # -----------------------------------------------------
    def _fetch_news(self, company_name: str):
        """
        Gets latest relevant news headlines using RSS feeds.
        """
        try:
            news = self.news.fetch(company_name)
            logger.info(f"📰 {len(news)} news items retrieved for {company_name}")
            return news
        except Exception as e:
            logger.warning(f"News RSS fetch failed: {e}")
            return []
