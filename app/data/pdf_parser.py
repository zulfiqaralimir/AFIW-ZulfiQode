"""
PDF Parser for extracting text from PDF files
"""
import fitz  # PyMuPDF
from typing import Optional
from app.core.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts full text content from PDF file.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text content
    """
    try:
        text = ""
        doc = fitz.open(file_path)
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text("text")
            if page_text:
                text += page_text + "\n"
        
        doc.close()
        
        logger.info(f"✅ PDF text extracted: {len(text)} characters from {file_path}")
        return text.strip()
        
    except Exception as e:
        logger.error(f"PDF parsing error: {e}")
        return f"[PDF Parsing Error]: {e}"


def extract_text_from_bytes(file_bytes: bytes) -> str:
    """
    Extracts full text content from PDF bytes.
    
    Args:
        file_bytes: PDF file as bytes
        
    Returns:
        Extracted text content
    """
    try:
        import io
        text = ""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text("text")
            if page_text:
                text += page_text + "\n"
        
        doc.close()
        
        logger.info(f"✅ PDF text extracted: {len(text)} characters from bytes")
        return text.strip()
        
    except Exception as e:
        logger.error(f"PDF parsing error from bytes: {e}")
        return f"[PDF Parsing Error]: {e}"


def extract_tables_from_pdf(file_path: str) -> list:
    """
    Extracts tables from PDF file.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of extracted tables
    """
    try:
        import pdfplumber
        tables = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        
        logger.info(f"✅ PDF tables extracted: {len(tables)} tables from {file_path}")
        return tables
        
    except Exception as e:
        logger.error(f"PDF table extraction error: {e}")
        return []

