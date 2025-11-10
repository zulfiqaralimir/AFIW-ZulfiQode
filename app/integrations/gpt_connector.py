"""
Two-phase GPT connector for AFIW–ZulfiQode Lawyer-AI

Phase 1 → Technical
Phase 2 → Management + Ethics + Risk
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class GPTClient:
    """
    Two-phase GPT connector:
    - Phase 1: Technical analysis (MA-200, RSI, resistance/support)
    - Phase 2: Management + Ethics + Risk analysis
    """
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 gpt_id: Optional[str] = None,
                 model: Optional[str] = None):
        """
        Initialize GPT Client
        
        Args:
            api_key: OpenAI API key (default: from env)
            gpt_id: Custom GPT ID (default: from env)
            model: OpenAI model (default: from env or gpt-4o)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.gpt_id = gpt_id or os.getenv("CUSTOM_GPT_ID")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # ---------- internal helpers ----------
    
    def _call_gpt(self, system: str, user: str) -> Dict[str, Any]:
        """
        Generic GPT JSON call with safe parsing
        
        Args:
            system: System message
            user: User message
            
        Returns:
            Parsed JSON response or error dict
        """
        try:
            # OpenAI requires the word "json" in messages when using json_object response_format
            # Ensure it's present in either system or user message
            system_with_json = system if "json" in system.lower() else f"{system} Return your response as valid JSON."
            user_with_json = user if "json" in user.lower() else f"{user} Return your response as valid JSON."
            
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_with_json},
                    {"role": "user", "content": user_with_json}
                ],
                response_format={"type": "json_object"}
            )
            content = resp.choices[0].message.content
            
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"GPT JSON parse error: {e}")
                return {"error": "GPT JSON parse error", "raw": content}
                
        except Exception as e:
            logger.exception(f"GPT call failed: {e}")
            return {"error": str(e)}
    
    # ---------- phase 1 : technical ----------
    
    def _phase1_technical(self, company: str, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Phase 1: Technical analysis (MA-200, RSI, resistance/support)
        
        Args:
            company: Company name
            symbol: Optional stock symbol
            
        Returns:
            Technical analysis dictionary
        """
        sys = (
            "You are Lawyer-AI Technical Analyst. "
            "You must return your output as a JSON object containing exactly this key: "
            "'technical_analysis'. The JSON must include fields "
            "ma_200, rsi_14_last_10_days, resistance_support, trend_summary, "
            "and technical_confidence."
        )
        user = (
            f"Company: {company}\n"
            f"Symbol: {symbol or 'PSX symbol if available'}\n"
            "Retrieve MA-200, RSI(14), and resistance/support levels from verified sources "
            "(TradingView, PSX, Reuters). If unavailable, set value='not available'. "
            "Respond only in JSON."
        )
        return self._call_gpt(sys, user)
    
    # ---------- phase 2 : management/ethics/risk ----------
    
    def _phase2_management(self, company: str) -> Dict[str, Any]:
        """
        Phase 2: Management + Ethics + Risk analysis
        
        Args:
            company: Company name
            
        Returns:
            Management/ethics/risk analysis dictionary
        """
        sys = (
            "You are Lawyer-AI Financial Ethics & Risk Analyzer. "
            "Return your answer strictly as a JSON object following the AFIW–ZulfiQode schema v9.0. "
            "The JSON must include tone, ethical_flag, risk_level, source_authenticity, summary, "
            "and management_analysis, plus any available confidence scores."
        )
        user = (
            f"Company: {company}\n"
            "Perform ethics, risk, and management-quality analysis using verified sources "
            "(PSX, SECP, Profit, Dawn, Tribune). Respond only in JSON."
        )
        return self._call_gpt(sys, user)
    
    # ---------- merge ----------
    
    @staticmethod
    def _merge_dicts(base: Dict[str, Any], addon: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two dictionaries with smart conflict resolution:
        - addon fills missing fields in base
        - averages confidences if both present
        - addon wins for 'not available' fields
        
        Args:
            base: Base dictionary (Phase 2 results)
            addon: Additional dictionary (Phase 1 results)
            
        Returns:
            Merged dictionary
        """
        if not addon:
            return base
        
        out = dict(base or {})
        
        # Fill missing fields or replace 'not available' with addon values
        for k, v in addon.items():
            if k not in out or out[k] in ("", None, "not available"):
                out[k] = v
            elif isinstance(v, dict) and isinstance(out.get(k), dict):
                # Merge nested dictionaries
                out[k] = {**out[k], **v}
        
        # Average confidences if both sides have numeric values
        confidence_fields = [
            "tone_confidence",
            "ethical_confidence",
            "risk_confidence",
            "authenticity_confidence",
            "technical_confidence"
        ]
        
        for k in confidence_fields:
            try:
                base_val = out.get(k)
                addon_val = addon.get(k)
                if isinstance(base_val, (int, float)) and isinstance(addon_val, (int, float)):
                    out[k] = round((base_val + addon_val) / 2, 1)
            except Exception:
                pass
        
        return out
    
    # ---------- public entry ----------
    
    def analyze_web(self, company: str, symbol: Optional[str] = None, prompt_extras: str = "") -> Dict[str, Any]:
        """
        Two-phase hybrid GPT call
        
        Args:
            company: Company name
            symbol: Optional stock symbol
            prompt_extras: Additional prompt instructions (for backward compatibility)
            
        Returns:
            Merged analysis results
        """
        logger.info(f"Phase 1 technical for {company}")
        tech = self._phase1_technical(company, symbol)
        
        logger.info(f"Phase 2 management/ethics for {company}")
        man = self._phase2_management(company)
        
        merged = self._merge_dicts(man, tech)
        merged["source"] = "Custom GPT (two-phase)"
        
        logger.info(f"✅ Two-phase GPT analysis completed for {company}")
        return merged
    
    def analyze_text(self, company: str, text_blob: str) -> Dict[str, Any]:
        """
        Optional: send a local PDF/text blob for reasoning-only (no web).
        
        Args:
            company: Company name
            text_blob: Text content to analyze
            
        Returns:
            Lawyer-AI JSON schema dictionary
        """
        try:
            system = (
                "You are Lawyer-AI. Reason ONLY over the provided text. "
                "Return the standard JSON schema (v9.0) as valid JSON."
            )
            user = (
                f"Company: {company}\n"
                "Analyze the following text for ethics/risk/tone. "
                "Return only the JSON schema as valid JSON.\n\n"
                f"{text_blob[:150000]}"  # safety cap
            )
            
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                response_format={"type": "json_object"}
            )
            
            content = resp.choices[0].message.content
            
            try:
                result = json.loads(content)
                logger.info(f"✅ GPT text analysis completed for {company}")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"GPT JSON parse error: {e}")
                return {"error": "GPT JSON parse error", "raw": content}
                
        except Exception as e:
            logger.error(f"GPT text analysis failed: {e}")
            return {"error": f"GPT analysis failed: {str(e)}"}
