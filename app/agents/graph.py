from app.agents.planner import PlannerAgent
from app.agents.executor import ExecutorAgent
from app.agents.verifier import VerifierAgent
from app.agents.risk_analyzer import RiskAnalyzer
from typing import List, Dict, Optional
import time


class AgentPipeline:
    """Full pipeline: Planner → Executor → Verifier → Risk Analyzer"""

    def __init__(self):
        """Initialize the agent pipeline with all agents."""
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.verifier = VerifierAgent()
        self.risk_analyzer = RiskAnalyzer()

    def run_pipeline(self, task: str, financial_data: Optional[Dict] = None) -> Dict:
        """
        Run the complete agent pipeline: Plan → Execute → Verify → Risk Analysis.
        
        Args:
            task: The input task/text to process
            financial_data: Optional financial data dictionary for risk analysis
            
        Returns:
            Dictionary with steps, ratios, risk summary, and comparison
        """
        start_time = time.time()
        results = []

        # Step 1: Planning
        plan = self.planner.create_plan(task)

        # Step 2: Execution + Verification
        verified = None
        for step_obj in plan:
            step = step_obj["step"]
            context = step_obj["content"]
            
            # Execute step
            output = self.executor.execute_step(step, context)
            
            # Verify output
            verified = self.verifier.verify(output)
            
            results.append({
                "step": step,
                "task": step,  # For backward compatibility
                "output": verified["text"],
                "result": verified["text"],  # For backward compatibility
                "hallucination_score": verified["hallucination_score"],
                "bias_score": verified["bias_score"],
                "confidence": verified["confidence"],
            })

        # Step 3: Compute Risk Analysis (if financial data provided)
        if financial_data:
            ratios = self.risk_analyzer.compute_ratios(financial_data)
            ethical_bias = verified["bias_score"] / 5.0 if verified else 0.0  # Normalize bias score
            risk = self.risk_analyzer.compute_risk_score(ratios, ethical_bias=ethical_bias)
            econ = self.risk_analyzer.econometric_baseline(ratios)
            comparison = self.risk_analyzer.compare_models(risk["risk_score"], econ)
        else:
            ratios = {}
            risk = {}
            comparison = {}

        # Step 4: Package Output
        latency = round((time.time() - start_time) * 1000, 2)
        
        return {
            "task": task,
            "steps": results,
            "ratios": ratios,
            "risk_summary": risk,
            "econ_comparison": comparison,
            "latency_ms": latency,
        }


# Backward compatibility function
def run_agent_pipeline(text: str) -> dict:
    """Legacy function for backward compatibility"""
    pipeline = AgentPipeline()
    results = pipeline.run_pipeline(text)
    
    # Convert to old format
    execution_results = [
        {"task": r["task"], "result": r["result"]}
        for r in results["steps"]
    ]
    
    # Extract flags from verified results
    flags = {}
    for r in results["steps"]:
        task = r["task"]
        flags[task] = {
            "status": "Red Flag" if (r["bias_score"] > 0 or r.get("hallucination_score", 0) > 0) else "Clear",
            "bias_score": r["bias_score"],
            "hallucination": r.get("hallucination_score", 0) > 0,
            "reason": "",  # Will be populated by verifier
        }

    return {
        "steps": execution_results,
        "flags": flags
    }
