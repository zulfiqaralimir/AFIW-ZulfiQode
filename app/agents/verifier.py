"""
Verifier Agent:
Validates and completes the raw data extracted by ExecutorAgent.
Computes CAS, CII, and TIT formulas according to Lawyer-AI v9.0.
"""
import math
from typing import Dict, Optional, Tuple
from app.core.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------
# 🔍 VerifierAgent
# ---------------------------------------------------------
class VerifierAgent:
    """
    Validates and completes the raw data extracted by ExecutorAgent.
    Computes CAS, CII, and TIT formulas according to Lawyer-AI v9.0.
    Ensures output is normalized, consistent, and ready for JudgeAgent.
    """
    
    def __init__(self):
        self.previous_cii = 68  # you can load this from Neo4j later for real tracking
    
    # -----------------------------------------------------
    def validate(self, raw_data: dict) -> dict:
        logger.info("🔍 VerifierAgent validating extracted data.")
        
        op = raw_data.get("operational_metrics", {})
        tech = raw_data.get("technical_analysis", {})
        cycle = self._build_cycle_context()
        ethics_score = self._estimate_ethics_score(raw_data)
        risk_score = self._estimate_risk_score(raw_data)
        technical_score = tech.get("technical_confidence", 0)
        cycle_score = cycle.get("cycle_alignment_score", 50)
        
        # Compute Composite Integrity Index (CII)
        cii = self._compute_cii(
            ethics_score,
            risk_score,
            technical_score,
            cycle_score
        )
        
        # Compute Temporal Integrity Trend (TIT)
        tit_value, tit_class, direction = self._compute_tit(cii)
        
        # Build verified structure
        verified = {
            "company_name": raw_data.get("company_name", "Unknown"),
            "tone": self._detect_tone(raw_data.get("text_content", "")),
            "tone_confidence": 80,
            
            "ethical_flag": self._classify_ethics(ethics_score),
            "ethical_confidence": ethics_score,
            
            "risk_level": self._classify_risk(risk_score),
            "risk_confidence": risk_score,
            
            "source_authenticity": "authentic",
            "authenticity_confidence": 90,
            "summary": f"Report shows {self._classify_ethics(ethics_score)} governance and {self._classify_risk(risk_score)} risk profile.",
            
            "technical_analysis": tech,
            "business_cycle_context": cycle,
            "operational_metrics": op,
            
            "composite_integrity_index": {
                "cii_score": cii,
                "cii_class": self._classify_cii(cii),
                "calculation_basis": "0.35×Ethics + 0.25×(100−Risk) + 0.20×Technical + 0.20×CycleAlign",
                "interpretation": self._interpret_cii(cii)
            },
            
            "temporal_integrity_trend": {
                "cii_previous": self.previous_cii,
                "cii_current": cii,
                "tit_value": tit_value,
                "tit_class": tit_class,
                "trend_direction": direction,
                "observation_period": "Q2–Q3 2025",
                "interpretation": f"Integrity trend is {tit_class.lower()} quarter-to-quarter."
            }
        }
        
        logger.info("✅ VerifierAgent validation complete.")
        return verified
    
    # -----------------------------------------------------
    # --- Internal Calculation Helpers ---
    # -----------------------------------------------------
    def _compute_cii(self, ethics, risk, technical, cycle):
        """
        Composite Integrity Index (CII)
        CII = 0.35×Ethics + 0.25×(100−Risk) + 0.20×Technical + 0.20×CycleAlign
        """
        cii = (0.35 * ethics) + (0.25 * (100 - risk)) + (0.20 * technical) + (0.20 * cycle)
        return round(cii, 2)
    
    def _compute_tit(self, current_cii) -> Tuple[float, str, str]:
        """
        Compute Temporal Integrity Trend (TIT)
        
        Returns:
            Tuple of (tit_value, tit_class, trend_direction)
        """
        tit = current_cii - self.previous_cii
        if tit > 2:
            return tit, "Improving", "up"
        elif tit < -2:
            return tit, "Declining", "down"
        else:
            return tit, "Stable", "flat"
    
    def _build_cycle_context(self):
        """
        Hardcoded for now; can be made dynamic from year detection.
        """
        cycle = {
            "current_phase": "bullish",
            "phase_confidence": "high",
            "cycle_confidence_score": 85,
            "cycle_alignment_score": 78,
            "cycle_alignment_class": "Strongly-Cyclical",
            "interpretation": "Company appears aligned with Pakistan's bullish macro phase (2024–34)."
        }
        return cycle
    
    def _detect_tone(self, text):
        """
        Simple keyword-based tone detection.
        """
        text_lower = text.lower()
        if any(k in text_lower for k in ["loss", "deficit", "impairment", "liability", "uncertain"]):
            return "negative"
        elif any(k in text_lower for k in ["growth", "profit", "increase", "expansion", "stability"]):
            return "positive"
        return "neutral"
    
    def _estimate_ethics_score(self, raw):
        """
        Very simple heuristic based on audit / governance keywords.
        """
        text = raw.get("text_content", "").lower()
        score = 85
        if "qualified opinion" in text or "investigation" in text:
            score -= 25
        if "adverse audit" in text or "restatement" in text:
            score -= 35
        return max(40, min(score, 95))
    
    def _estimate_risk_score(self, raw):
        """
        Estimate risk based on financial or news sentiment.
        """
        news = raw.get("news_rss", [])
        risk = 50
        for n in news:
            title = n.get("title", "").lower() if isinstance(n, dict) else ""
            summary = n.get("summary", "").lower() if isinstance(n, dict) else ""
            if "default" in title or "loss" in summary:
                risk += 15
        if risk > 90:
            risk = 90
        return risk
    
    def _classify_ethics(self, val):
        if val >= 80:
            return "ethical"
        elif val >= 60:
            return "questionable"
        else:
            return "unethical"
    
    def _classify_risk(self, val):
        if val <= 40:
            return "low"
        elif val <= 70:
            return "moderate"
        else:
            return "high"
    
    def _classify_cii(self, val):
        if val >= 80:
            return "High"
        elif val >= 60:
            return "Moderate"
        elif val >= 40:
            return "Low"
        else:
            return "Critical"
    
    def _interpret_cii(self, val):
        if val >= 80:
            return "Company demonstrates strong ethical-financial integrity."
        elif val >= 60:
            return "Company maintains reasonable governance balance with some risk."
        elif val >= 40:
            return "Company integrity under strain, governance issues visible."
        else:
            return "Severe governance or ethical distress detected."
    
    # Backward compatibility methods
    def verify(self, result: Dict) -> Dict:
        """
        Verify analysis result for schema completeness and consistency (backward compatibility).
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Dictionary with verification status
        """
        # Check for missing required fields
        missing = [k for k in [
            "tone", "ethical_flag", "risk_level",
            "composite_integrity_index"
        ] if k not in result]
        
        # Check consistency
        consistency = True
        cii_score = result.get("composite_integrity_index", {}).get("cii_score", 0)
        if cii_score < 0 or cii_score > 100:
            consistency = False
        
        return {
            "verified": len(missing) == 0 and consistency,
            "missing_fields": missing,
            "notes": "All essential fields present and logically consistent."
                      if len(missing) == 0 and consistency
                      else f"Issues: {missing}",
            "result": result  # Include original result
        }
    
    def verify_text(self, text: str) -> Dict:
        """
        Verify text for hallucination, bias, and calculate confidence (backward compatibility).
        
        Args:
            text: The text to verify
            
        Returns:
            Dictionary with verification results including scores and confidence
        """
        from app.evaluation.metrics import (
            detect_bias_signals,
            detect_hallucination_signals,
        )
        from app.core.metrics import HALLUCINATION_ALERTS
        
        bias_score = detect_bias_signals(text)
        hallucination = detect_hallucination_signals(text)
        
        # Increment hallucination metric if detected
        if hallucination:
            HALLUCINATION_ALERTS.inc()
        
        # Calculate confidence (1 - normalized bias score, penalized by hallucination)
        bias_normalized = min(bias_score / 5.0, 1.0)  # Normalize to 0-1
        hallucination_penalty = 0.5 if hallucination else 0.0
        confidence = round(1 - (bias_normalized * 0.5 + hallucination_penalty * 0.5), 2)
        
        # Build reason from detected signals
        reason = ""
        lower = text.lower()
        bias_keywords = ["manipulate", "bias", "overconfident", "inflated", "ambiguous"]
        hallu_phrases = ["as an ai", "i do not have", "cannot verify"]
        matched_bias = next((w for w in bias_keywords if w in lower), None)
        matched_hallu = next((p for p in hallu_phrases if p in lower), None)
        
        if matched_bias:
            reason = f"Found bias keyword: '{matched_bias}'"
        elif matched_hallu:
            reason = f"Found hallucination phrase: '{matched_hallu}'"
        
        return {
            "text": text,
            "hallucination_score": 1.0 if hallucination else 0.0,
            "bias_score": bias_score,
            "confidence": confidence,
            "hallucination": hallucination,
            "reason": reason
        }


# Backward compatibility function
def verify_result(execution_results: list) -> dict:
    """Legacy function for backward compatibility"""
    verifier = VerifierAgent()
    flags = {}
    
    for item in execution_results:
        task = item["task"]
        output: str = item.get("result", "")
        
        # Use verify_text for text-based verification (backward compatibility)
        verified = verifier.verify_text(output)
        
        status = "Red Flag" if (verified["bias_score"] > 0 or verified["hallucination"]) else "Clear"
        
        flags[task] = {
            "status": status,
            "bias_score": verified["bias_score"],
            "hallucination": verified["hallucination"],
            "reason": verified["reason"],
        }
    
    return flags
