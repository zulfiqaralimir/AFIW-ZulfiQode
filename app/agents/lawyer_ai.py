"""
Lawyer-AI: Financial Ethics & Risk Analyzer v9.0
Integrates Custom GPT instructions for comprehensive financial analysis
Supports both GPT-based and agent-orchestrated analysis
"""
import io
import json
import time
import logging
from typing import Dict, Optional, List, Any
from openai import OpenAI
from app.settings import OPENAI_API_KEY
from app.core.metrics import MetricsCollector, push_metrics
from app.agents.planner import PlannerAgent
from app.agents.executor import ExecutorAgent
from app.agents.verifier import VerifierAgent
from app.agents.judge import JudgeAgent
from app.data.neo4j_integration import Neo4jClient
from app.core.logger import get_logger

logger = get_logger(__name__)
metrics = MetricsCollector()

# Lawyer-AI Instructions
LAWYER_AI_INSTRUCTIONS = """
# ⚙️ **Lawyer-AI: Financial Ethics & Risk Analyzer — v9.0 (AFIW–ZulfiQode)**

### 🎯 **Purpose**

Lawyer-AI evaluates corporate **ethics, risk, operations, and financial health**, combining governance data, TradingView indicators, and Pakistan's macroeconomic cycles.

It produces structured JSON with confidence scoring for use in AFIW–ZulfiQode analytics (Neo4j, Prometheus).

---

## 🧩 **Analytical Dimensions**

1. **Tone** – sentiment across reports/news.
2. **Ethics** – governance integrity.
3. **Risk** – financial/reputational exposure.
4. **Source Authenticity** – reliability of inputs.
5. **Technical Indicators** – RSI(14) & 200-day MA via TradingView.
6. **Business-Cycle Context** – 10-year macro pattern (± 2–4 yrs).
7. **Cycle Alignment Score (CAS)** – alignment with macro phase.
8. **Composite Integrity Index (CII)** – overall ethical-financial integrity.
9. **Temporal Integrity Trend (TIT)** – quarter-to-quarter change in integrity.
10. **Operational Cash Flow (OCF)** – sustainability of operations.
11. **Gross Margin Effect (GME)** – pricing power and cost efficiency.
12. **Future Performance Perspective (FPP)** – forward-looking qualitative risk outlook.

---

## 🧾 **Output JSON Schema**

You must respond ONLY with valid JSON matching this exact schema:

{
 "tone": "positive|neutral|negative",
 "tone_confidence": 0-100,
 "ethical_flag": "ethical|questionable|unethical",
 "ethical_confidence": 0-100,
 "risk_level": "low|moderate|high",
 "risk_confidence": 0-100,
 "source_authenticity": "authentic|unverified|rumour",
 "authenticity_confidence": 0-100,
 "summary": "Concise reasoning.",

 "technical_analysis": {
   "source": "TradingView (symbol:<exchange-code>)",
   "rsi_14_last_10_days": [{"date":"YYYY-MM-DD","value":<float>}],
   "ma_200": <float>,
   "trend_summary": "Short RSI + MA interpretation.",
   "data_link": "https://www.tradingview.com/symbols/<exchange>-<ticker>/technicals/",
   "technical_confidence": 0-100
 },

 "business_cycle_context": {
   "current_phase": "bullish|bearish",
   "phase_confidence": "high|moderate|low",
   "cycle_confidence_score": 0-100,
   "cycle_alignment_score": 0-100,
   "cycle_alignment_class": "Strongly|Moderately|Weakly|Counter-Cyclical",
   "interpretation": "Company vs. macro phase alignment."
 },

 "operational_metrics": {
   "operational_cash_flow": {
     "ocf_value": "<currency or ratio>",
     "ocf_trend": "positive|negative|volatile",
     "ocf_confidence": 0-100,
     "interpretation": "Ability to sustain operations via internal cash flows."
   },
   "gross_margin_effect": {
     "gross_margin_percent": <float>,
     "gme_trend": "expanding|stable|contracting",
     "gme_confidence": 0-100,
     "interpretation": "Indicates pricing efficiency and cost management."
   }
 },

 "composite_integrity_index": {
   "cii_score": 0-100,
   "cii_class": "High|Moderate|Low|Critical",
   "calculation_basis": "0.35×Ethics + 0.25×(100−Risk) + 0.20×Technical + 0.20×CycleAlign",
   "interpretation": "Overall ethical-financial stability."
 },

 "temporal_integrity_trend": {
   "cii_previous": <float>,
   "cii_current": <float>,
   "tit_value": <float>,
   "tit_class": "Improving|Stable|Declining",
   "trend_direction": "up|flat|down",
   "observation_period": "Qx–Qy <Year>",
   "interpretation": "Quarter-to-quarter integrity movement."
 },

 "future_performance_perspective": {
   "outlook": "improving|stable|declining",
   "drivers": ["revenue recovery","debt reduction","regulatory support"],
   "forward_risk_level": "low|moderate|high",
   "confidence": 0-100,
   "interpretation": "Projected future direction based on combined ethical, financial, and technical indicators."
 },

 "hallucination_metrics": {
   "bias": <float>,
   "variance": <float>,
   "confidence_interval": "<string>",
   "distribution_shape": "<string>",
   "hallucination_score": 0-100,
   "interpretation": "Reliability assessment of outputs."
 }
}

---

## 📈 **Pakistan Business Cycle (Simplified)**

10-year alternating phases (±2–4 yrs):

| Cycle | Period  | Phase                   |
| :---- | :------ | :---------------------- |
| 1     | 1947–57 | Bearish                 |
| 2     | 1958–68 | Bullish                 |
| 3     | 1969–79 | Bearish                 |
| 4     | 1980–90 | Bullish                 |
| 5     | 1991–01 | Bearish                 |
| 6     | 2002–12 | Bullish                 |
| 7     | 2013–23 | Bearish                 |
| 8     | 2024–34 | **Bullish (Projected)** |

---

## 📊 **Key Formulas**

**Cycle Alignment Score (CAS)**
CAS = 0.35×FinancialTrend + 0.25×MarketMomentum + 0.25×SectorCorrelation + 0.15×MacroCoherence

**Composite Integrity Index (CII)**
CII = 0.35×Ethics + 0.25×(100−Risk) + 0.20×Technical + 0.20×CycleAlign

**Temporal Integrity Trend (TIT)**
TIT = CII_current − CII_previous

---

## 📘 **Usage Rules**

* Maintain neutrality and evidence-based analysis.
* Use only verified data (TradingView, SECP, PSX, filings).
* No investment advice.
* If metric missing → mark "not available" and confidence = 0.
* Always respond in the defined JSON schema.
* Do not include any text outside the JSON structure.
"""


class LawyerAI:
    """
    Lawyer-AI: Financial Ethics & Risk Analyzer v9.0
    Supports both GPT-based and agent-orchestrated analysis
    """
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.2, use_agents: bool = False):
        """
        Initialize Lawyer-AI analyzer
        
        Args:
            model: OpenAI model name (default: "gpt-4")
            temperature: Model temperature (default: 0.2)
            use_agents: Use agent orchestration instead of GPT (default: False)
        """
        self.use_agents = use_agents
        
        if use_agents:
            # Initialize agent pipeline
            self.planner = PlannerAgent()
            self.executor = ExecutorAgent(use_deterministic=True)
            self.verifier = VerifierAgent()
            self.judge = JudgeAgent()
            logger.info("Lawyer-AI initialized with agent orchestration")
        else:
            # Initialize GPT-based analysis
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            self.model = model
            self.temperature = temperature
            logger.info(f"Lawyer-AI initialized with GPT model: {model}")
    
    def analyze_with_agents(
        self,
        text: str,
        company_name: str = "Unknown",
        human_feedback: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze using agent orchestration: Planner → Executor → Verifier → Judge
        
        Args:
            text: Financial report text to analyze
            company_name: Company name
            human_feedback: Optional human feedback data
            
        Returns:
            Complete analysis with hallucination metrics and human feedback
        """
        if not self.use_agents:
            raise ValueError("Agent orchestration not enabled. Initialize with use_agents=True")
        
        start_time = time.time()
        
        try:
            # Step 1: Planning
            plan = self.planner.get_plan(company_name)
            logger.info(f"Plan created: {plan['message']}")
            
            # Step 2: Execution
            # Note: For agent orchestration, we use text-based execution
            # For PDF-based execution, use execute(company, file_bytes=pdf_bytes)
            base_result = self.executor.execute(company_name, text=text)
            
            # Step 3: Verification
            verification = self.verifier.verify(base_result)
            
            if not verification["verified"]:
                logger.warning(f"Verification failed: {verification['notes']}")
            
            # Step 4: Judgment (hallucination metrics and human feedback)
            judgment = self.judge.evaluate(base_result, human_feedback)
            
            # Merge all results
            output = {**base_result, **judgment}
            
            duration = time.time() - start_time
            
            # Record metrics
            metrics.record_agent_task("lawyer_ai_agent_pipeline", duration)
            
            logger.info(
                f"Agent orchestration completed for {company_name}",
                extra={
                    "company": company_name,
                    "duration_ms": int(duration * 1000),
                    "verified": verification["verified"]
                }
            )
            
            # Add metadata
            output["_metadata"] = {
                "method": "agent_orchestration",
                "duration": duration,
                "timestamp": time.time(),
                "verification": verification
            }
            
            # Push metrics to Prometheus
            try:
                push_metrics(company_name, output)
            except Exception as e:
                logger.warning(f"Failed to update Prometheus metrics: {str(e)}")
            
            return output
            
        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__
            metrics.record_error(error_type, "lawyer_ai_agents")
            
            logger.error(
                f"Agent orchestration failed: {str(e)}",
                extra={"error_type": error_type, "duration_ms": int(duration * 1000)},
                exc_info=True
            )
            
            raise


# ---------------------------------------------------------
#  ⚖️  LawyerAIOrchestrator — Central Controller
# ---------------------------------------------------------
class LawyerAIOrchestrator:
    """
    Controls the Lawyer-AI pipeline:
    Planner → Executor → Verifier → Judge
    
    Produces final JSON strictly following the Lawyer-AI v9.0 schema.
    """
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.verifier = VerifierAgent()
        self.judge = JudgeAgent()
    
    # -----------------------------------------------------
    #  Main Entry Point
    # -----------------------------------------------------
    def run_analysis(self, file_bytes: bytes, filename: str):
        logger.info(f"📘 Starting analysis for {filename}")
        
        # 1️⃣ PLAN
        plan = self.planner.create_plan(filename)
        logger.info(f"🧩 Plan generated: {plan}")
        
        # 2️⃣ EXECUTE
        raw_data = self.executor.execute(file_bytes, plan)
        logger.info(f"✅ Executor completed. Extracted keys: {list(raw_data.keys())}")
        
        # 3️⃣ VERIFY
        verified = self.verifier.validate(raw_data)
        logger.info("🔍 Verifier checks complete.")
        
        # 4️⃣ JUDGE
        final_json = self.judge.finalize(verified)
        logger.info("⚖️ Judge synthesis complete.")
        
        logger.info("🎯 Full Lawyer-AI v9.0 pipeline finished successfully.")
        
        # Push metrics to Prometheus
        company = verified.get("company_name", "Unknown")
        push_metrics(company, final_json)
        
        # Store in Neo4j
        try:
            neo = Neo4jClient()
            neo.store_company_analysis(final_json)
            neo.close()
        except Exception as e:
            logger.warning(f"Neo4j storage skipped: {e}")
        
        return final_json


class LawyerAI:
    """
    Lawyer-AI: Financial Ethics & Risk Analyzer v9.0
    Supports both GPT-based and agent-orchestrated analysis
    """
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.2, use_agents: bool = False):
        """
        Initialize Lawyer-AI analyzer
        
        Args:
            model: OpenAI model name (default: "gpt-4")
            temperature: Model temperature (default: 0.2)
            use_agents: Use agent orchestration instead of GPT (default: False)
        """
        self.use_agents = use_agents
        
        if use_agents:
            # Initialize agent pipeline
            self.planner = PlannerAgent()
            self.executor = ExecutorAgent(use_deterministic=True)
            self.verifier = VerifierAgent()
            self.judge = JudgeAgent()
            logger.info("Lawyer-AI initialized with agent orchestration")
        else:
            # Initialize GPT-based analysis
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            self.model = model
            self.temperature = temperature
            logger.info(f"Lawyer-AI initialized with GPT model: {model}")
    
    def analyze(
        self,
        text: str,
        financial_data: Optional[Dict] = None,
        company_name: Optional[str] = None,
        exchange_code: Optional[str] = None,
        news_context: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive financial analysis
        
        Uses agent orchestration if use_agents=True, otherwise uses GPT-based analysis
        
        Args:
            text: Financial report text or content to analyze
            financial_data: Optional financial data dictionary
            company_name: Optional company name
            exchange_code: Optional exchange code for TradingView links
            news_context: Optional list of news articles for context
            
        Returns:
            Structured JSON analysis matching Lawyer-AI schema
        """
        # Use agent orchestration if enabled
        if self.use_agents:
            return self.analyze_with_agents(text, company_name or "Unknown")
        
        # Otherwise use GPT-based analysis
        start_time = time.time()
        
        try:
            # Build the analysis prompt
            prompt_parts = [
                "Analyze the following financial content using Lawyer-AI v9.0 framework:",
                "",
                "=== CONTENT TO ANALYZE ===",
                text[:10000],  # Limit text length
                ""
            ]
            
            if financial_data:
                prompt_parts.extend([
                    "=== FINANCIAL DATA ===",
                    json.dumps(financial_data, indent=2),
                    ""
                ])
            
            if company_name:
                prompt_parts.append(f"Company: {company_name}")
            
            if exchange_code:
                prompt_parts.append(f"Exchange Code: {exchange_code}")
            
            if news_context:
                prompt_parts.extend([
                    "=== NEWS CONTEXT ===",
                    json.dumps(news_context, indent=2),
                    ""
                ])
            
            prompt_parts.extend([
                "=== INSTRUCTIONS ===",
                "Provide your analysis in the exact JSON schema specified in the instructions.",
                "Ensure all confidence scores are between 0-100.",
                "Calculate CII, CAS, and TIT using the provided formulas.",
                "Include hallucination metrics based on factual grounding assessment."
            ])
            
            full_prompt = "\n".join(prompt_parts)
            
            # Create messages with system instructions
            messages = [
                {
                    "role": "system",
                    "content": LAWYER_AI_INSTRUCTIONS
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Parse JSON response
            response_text = response.choices[0].message.content
            analysis = json.loads(response_text)
            
            duration = time.time() - start_time
            
            # Record metrics
            metrics.record_openai_call("lawyer-ai", "success", duration)
            metrics.record_agent_task("lawyer_ai_analysis", duration)
            
            logger.info(
                "Lawyer-AI analysis completed",
                extra={
                    "company": company_name,
                    "duration_ms": int(duration * 1000),
                    "cii_score": analysis.get("composite_integrity_index", {}).get("cii_score")
                }
            )
            
            # Add metadata
            analysis["_metadata"] = {
                "model": self.model,
                "duration": duration,
                "timestamp": time.time()
            }
            
            # Push metrics to Prometheus if company name provided
            if company_name:
                try:
                    push_metrics(company_name, analysis)
                except Exception as e:
                    logger.warning(f"Failed to update Prometheus metrics: {str(e)}")
            
            return analysis
            
        except json.JSONDecodeError as e:
            duration = time.time() - start_time
            metrics.record_openai_call("lawyer-ai", "error", duration)
            logger.error(f"Failed to parse Lawyer-AI JSON response: {str(e)}", exc_info=True)
            raise ValueError(f"Invalid JSON response from Lawyer-AI: {str(e)}")
            
        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__
            metrics.record_openai_call("lawyer-ai", "error", duration)
            metrics.record_error(error_type, "lawyer_ai")
            
            logger.error(
                f"Lawyer-AI analysis failed: {str(e)}",
                extra={"error_type": error_type, "duration_ms": int(duration * 1000)},
                exc_info=True
            )
            
            raise
    
    def analyze_with_conclusion(
        self,
        text: str,
        financial_data: Optional[Dict] = None,
        company_name: Optional[str] = None,
        exchange_code: Optional[str] = None,
        news_context: Optional[List[Dict]] = None,
        human_feedback: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Perform analysis and generate separate conclusion
        
        Args:
            text: Financial report text
            financial_data: Optional financial data
            company_name: Optional company name
            exchange_code: Optional exchange code
            news_context: Optional news context
            human_feedback: Optional human feedback to incorporate
            
        Returns:
            Dictionary with analysis and separate conclusion
        """
        # Get base analysis
        analysis = self.analyze(
            text=text,
            financial_data=financial_data,
            company_name=company_name,
            exchange_code=exchange_code,
            news_context=news_context
        )
        
        # Generate conclusion
        conclusion_prompt = f"""
Based on the following Lawyer-AI analysis, provide a comprehensive conclusion that:
1. Summarizes key findings
2. Highlights critical risks and opportunities
3. Provides actionable insights
4. Incorporates human feedback if provided

=== ANALYSIS ===
{json.dumps(analysis, indent=2)}

=== HUMAN FEEDBACK ===
{json.dumps(human_feedback, indent=2) if human_feedback else "None provided"}

Provide a clear, structured conclusion in plain text (not JSON).
"""
        
        try:
            conclusion_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analyst providing clear, actionable conclusions."},
                    {"role": "user", "content": conclusion_prompt}
                ],
                temperature=0.3
            )
            
            conclusion = conclusion_response.choices[0].message.content
            
            return {
                "analysis": analysis,
                "conclusion": conclusion,
                "human_feedback_included": human_feedback is not None
            }
            
        except Exception as e:
            logger.warning(f"Failed to generate conclusion: {str(e)}, returning analysis only")
            return {
                "analysis": analysis,
                "conclusion": "Conclusion generation failed. See analysis for details.",
                "human_feedback_included": False
            }

