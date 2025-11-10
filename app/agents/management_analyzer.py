"""
Unified Management Analyzer (HYBRID)
Feeds both uploaded reports and web data into Lawyer-AI's ethics/risk pipeline
Supports GPT + Local hybrid mode
"""
import json
from typing import Dict, Any, Optional
from app.settings import USE_HYBRID, USE_GPT_FOR_WEB, USE_LOCAL_WEB
from app.data.websearch import WebSearch
from app.data.pdf_parser import extract_text_from_pdf, extract_text_from_bytes
from app.agents.lawyer_ai import LawyerAIOrchestrator
from app.core.logger import get_logger

logger = get_logger(__name__)


def _safe_load(d: Any) -> Dict[str, Any]:
    """Safely load JSON from string or dict."""
    if isinstance(d, str):
        try:
            return json.loads(d)
        except Exception:
            return {}
    return d or {}


def _merge_json(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two Lawyer-AI JSONs with a simple precedence:
    - primary wins when conflicts occur
    - average numeric confidences where possible
    - if field missing in primary, take from secondary
    """
    if not secondary:
        return primary
    
    out = dict(secondary)
    out.update(primary or {})
    
    # Average confidences if present on both
    confidence_fields = [
        "tone_confidence",
        "ethical_confidence",
        "risk_confidence",
        "authenticity_confidence"
    ]
    
    for k in confidence_fields:
        try:
            a = secondary.get(k)
            b = primary.get(k)
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                out[k] = round((a + b) / 2, 1)
        except Exception:
            pass
    
    # Merge nested dictionaries
    for key in ["composite_integrity_index", "temporal_integrity_trend", 
                "operational_metrics", "future_performance_perspective",
                "hallucination_metrics"]:
        if key in primary and key in secondary:
            if isinstance(primary[key], dict) and isinstance(secondary[key], dict):
                out[key] = {**secondary[key], **primary[key]}
    
    # Post-merge weighting: Give GPT higher weight on technical_analysis and management_analysis
    # since local web scraping won't provide these reliably
    if "technical_analysis" in primary:
        out["technical_analysis"] = primary["technical_analysis"]
    elif "technical_analysis" in secondary:
        out["technical_analysis"] = secondary["technical_analysis"]
    
    if "management_analysis" in primary:
        out["management_analysis"] = primary["management_analysis"]
    elif "management_analysis" in secondary:
        out["management_analysis"] = secondary["management_analysis"]
    
    return out


class ManagementAnalyzer:
    """
    Unified entry point for PDF + Web-based company analysis.
    Supports hybrid GPT + Local mode.
    """
    
    def __init__(self, gpt_client=None, use_hybrid=None, use_gpt_for_web=None, use_local_web=None):
        """
        Initialize ManagementAnalyzer
        
        Args:
            gpt_client: Optional GPTClient instance
            use_hybrid: Override USE_HYBRID setting
            use_gpt_for_web: Override USE_GPT_FOR_WEB setting
            use_local_web: Override USE_LOCAL_WEB setting
        """
        # Import GPT client only if needed
        self.gpt = None
        try:
            if gpt_client is not None:
                self.gpt = gpt_client
            elif USE_GPT_FOR_WEB or USE_HYBRID:
                from app.integrations.gpt_connector import GPTClient
                self.gpt = GPTClient()
        except Exception as e:
            logger.warning(f"GPT client initialization failed: {e}")
        
        self.local_ai = LawyerAIOrchestrator()
        self.web = WebSearch()
        
        # Runtime overrides
        self.use_hybrid = use_hybrid if use_hybrid is not None else USE_HYBRID
        self.use_gpt_for_web = use_gpt_for_web if use_gpt_for_web is not None else USE_GPT_FOR_WEB
        self.use_local_web = use_local_web if use_local_web is not None else USE_LOCAL_WEB
    
    def analyze_from_pdf(self, file_path: str, company: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze company from PDF file.
        Supports hybrid mode: local analysis + optional GPT boost.
        
        Args:
            file_path: Path to PDF file
            company: Optional company name (extracted from filename if not provided)
            
        Returns:
            Lawyer-AI analysis result
        """
        try:
            # Extract company name from file path if not provided
            if not company:
                import os
                company = os.path.splitext(os.path.basename(file_path))[0]
            
            # Extract text from PDF
            text = extract_text_from_pdf(file_path)
            
            # Local analysis
            local_json = self._analyze_text(company, text)
            
            if not self.use_hybrid or not self.gpt:
                return local_json
            
            # Optional: ask GPT to reason over the same text and merge
            try:
                gpt_json = self.gpt.analyze_text(company, text)
                merged = _merge_json(_safe_load(local_json), _safe_load(gpt_json))
                logger.info(f"✅ Hybrid PDF analysis completed for {company}")
                return merged
            except Exception as e:
                logger.warning(f"GPT analysis failed, using local only: {e}")
                return local_json
            
        except Exception as e:
            logger.error(f"PDF analysis failed: {e}")
            return {"error": str(e)}
    
    def analyze_from_pdf_bytes(self, file_bytes: bytes, filename: str, company: Optional[str] = None) -> Dict:
        """
        Analyze company from PDF bytes.
        
        Args:
            file_bytes: PDF file as bytes
            filename: Original filename
            company: Optional company name (extracted from filename if not provided)
            
        Returns:
            Lawyer-AI analysis result
        """
        try:
            # Extract company name from filename if not provided
            if not company:
                import os
                company = os.path.splitext(os.path.basename(filename))[0]
            
            # Extract text from PDF bytes
            text = extract_text_from_bytes(file_bytes)
            
            # Local analysis
            local_json = self._analyze_text(company, text)
            
            if not self.use_hybrid or not self.gpt:
                return local_json
            
            # Optional: ask GPT to reason over the same text and merge
            try:
                gpt_json = self.gpt.analyze_text(company, text)
                merged = _merge_json(_safe_load(local_json), _safe_load(gpt_json))
                logger.info(f"✅ Hybrid PDF analysis completed for {company}")
                return merged
            except Exception as e:
                logger.warning(f"GPT analysis failed, using local only: {e}")
                return local_json
            
        except Exception as e:
            logger.error(f"PDF analysis failed: {e}")
            return {"error": str(e)}
    
    def analyze_from_web(self, company: str, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze company from web search results.
        Supports hybrid mode: GPT web analysis + local web search.
        
        Args:
            company: Company name
            query: Optional custom search query
            
        Returns:
            Lawyer-AI analysis result
        """
        gpt_json = {}
        local_json = {}
        
        # GPT web analysis
        if self.use_gpt_for_web and self.gpt:
            try:
                gpt_json = self.gpt.analyze_web(
                    company,
                    prompt_extras="Use only verified corporate/financial sources. Provide citations inside summary if applicable."
                )
                logger.info(f"✅ GPT web analysis completed for {company}")
            except Exception as e:
                logger.warning(f"GPT web analysis failed: {e}")
                gpt_json = {}
        
        # Local web search
        if self.use_local_web:
            try:
                # Build search query
                if not query:
                    search_query = f"{company} Pakistan PSX SECP audit risk ethics"
                else:
                    search_query = query
                
                # Search web
                hits = self.web.search(search_query)
                
                if hits:
                    # Extract text from all results
                    combined = " ".join(self.web.extract_text(h.get('url', '')) for h in hits if h.get('url'))
                    local_json = self._analyze_text(company, combined)
                    logger.info(f"✅ Local web analysis completed for {company}")
                else:
                    logger.warning(f"No local web results found for {company}")
            except Exception as e:
                logger.warning(f"Local web analysis failed: {e}")
                local_json = {}
        
        # Merge results if hybrid mode
        if self.use_hybrid:
            merged = _merge_json(_safe_load(gpt_json), _safe_load(local_json))
            logger.info(f"✅ Hybrid web analysis completed for {company}")
            return merged
        
        # Return GPT or local (whichever is available)
        return gpt_json if gpt_json else local_json
    
    def _analyze_text(self, company: str, text: str) -> Dict:
        """
        Analyze text content directly using local orchestrator.
        
        Args:
            company: Company name
            text: Text content to analyze
            
        Returns:
            Lawyer-AI analysis result
        """
        try:
            # Use executor to process text
            from app.agents.executor import ExecutorAgent
            from app.agents.planner import PlannerAgent
            from app.agents.verifier import VerifierAgent
            from app.agents.judge import JudgeAgent
            
            planner = PlannerAgent()
            executor = ExecutorAgent()
            verifier = VerifierAgent()
            judge = JudgeAgent()
            
            # Create plan
            plan = planner.create_plan(company)
            
            # Execute with text content
            # Note: Executor expects file_bytes, so we'll pass text as bytes
            text_bytes = text.encode('utf-8')
            raw_data = executor.execute(text_bytes, plan)
            raw_data["company_name"] = company
            raw_data["text_content"] = text
            
            # Verify
            verified = verifier.validate(raw_data)
            
            # Judge
            final_json = judge.finalize(verified)
            
            return final_json
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return {"error": str(e), "company": company}
