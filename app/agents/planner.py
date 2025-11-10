"""
Planner Agent:
Decides which subtasks to run in sequence and prepares the task plan.
"""
from typing import List, Dict


class PlannerAgent:
    """Planner Agent for Lawyer-AI analysis pipeline"""

    def __init__(self):
        """Initialize with default plan structure"""
        self.plan: List[str] = [
            "extract_text",
            "tone_analysis",
            "ethics_risk_analysis",
            "technical_indicators",
            "operational_metrics",
            "composite_index",
            "verification",
            "judgment"
        ]

    def get_plan(self, company_name: str) -> Dict:
        """
        Get analysis plan for a company
        
        Args:
            company_name: Name of the company to analyze
            
        Returns:
            Dictionary with plan and metadata
        """
        return {
            "company": company_name,
            "plan": self.plan,
            "message": f"Planner ready: executing {len(self.plan)} steps for {company_name}"
        }

    def create_plan(self, task: str) -> List[Dict]:
        """
        Creates a structured plan for financial analysis (backward compatibility).
        
        Args:
            task: The input task/text to analyze
            
        Returns:
            List of plan steps with task and content
        """
        return [
            {"step": step, "content": task}
            for step in self.plan
        ]


# Backward compatibility function
def plan_tasks(input_text: str) -> list:
    """Legacy function for backward compatibility"""
    planner = PlannerAgent()
    plan = planner.create_plan(input_text)
    # Convert to old format
    return [
        {"task": step["step"], "content": step["content"]}
        for step in plan
    ]
