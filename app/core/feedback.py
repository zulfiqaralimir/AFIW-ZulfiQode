"""
Human Feedback Mechanism
Stores and manages human feedback for analysis improvement
"""
import os
import json
import time
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
from app.core.logger import get_logger

logger = get_logger(__name__)

# Default feedback storage path
FEEDBACK_DIR = Path("feedback_data")
FEEDBACK_DIR.mkdir(exist_ok=True)


class HumanFeedbackHandler:
    """
    Reads optional human feedback JSON files stored in feedback_data/.
    Aggregates average sentiment and creates a short conclusion message.
    """
    
    def __init__(self):
        self.path = "feedback_data"
        # Ensure directory exists
        os.makedirs(self.path, exist_ok=True)
    
    def aggregate_feedback(self, company_name: str):
        """
        Aggregate feedback for a company.
        
        Args:
            company_name: Company name to aggregate feedback for
            
        Returns:
            Dictionary with feedback conclusion
        """
        try:
            file_path = os.path.join(self.path, f"{company_name.lower().replace(' ', '_')}_feedback.json")
            
            if not os.path.exists(file_path):
                return {"conclusion": "No human feedback yet; system output used as-is."}
            
            with open(file_path, "r") as f:
                feedbacks = json.load(f)
            
            if not feedbacks:
                return {"conclusion": "No human feedback yet; system output used as-is."}
            
            avg_score = sum(f.get("score", 50) for f in feedbacks) / len(feedbacks)
            sentiment = (
                "positive" if avg_score > 70 else
                "neutral" if avg_score > 50 else
                "negative"
            )
            
            conclusion = f"Human reviewers rated model as {sentiment} (avg {avg_score:.1f})."
            return {"conclusion": conclusion}
        
        except Exception as e:
            logger.error(f"Feedback aggregation failed: {e}")
            return {"conclusion": "Error reading feedback data."}


class HumanFeedback:
    """
    Manages human feedback for analysis results (backward compatibility)
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize feedback handler
        
        Args:
            storage_path: Path to store feedback files (default: feedback_data/)
        """
        self.storage_path = storage_path or FEEDBACK_DIR
        self.storage_path.mkdir(exist_ok=True)
        
        logger.info(f"Human feedback initialized with storage: {self.storage_path}")
    
    def submit_feedback(
        self,
        analysis_id: str,
        feedback_type: str,
        feedback_data: Dict,
        user_id: Optional[str] = None,
        comments: Optional[str] = None
    ) -> Dict:
        """
        Submit human feedback for an analysis
        
        Args:
            analysis_id: Unique identifier for the analysis
            feedback_type: Type of feedback (e.g., "accuracy", "relevance", "completeness")
            feedback_data: Feedback data dictionary
            user_id: Optional user identifier
            comments: Optional text comments
            
        Returns:
            Dictionary with feedback submission details
        """
        feedback_entry = {
            "analysis_id": analysis_id,
            "feedback_type": feedback_type,
            "feedback_data": feedback_data,
            "user_id": user_id,
            "comments": comments,
            "timestamp": datetime.now().isoformat(),
            "submitted_at": time.time()
        }
        
        # Save to file
        feedback_file = self.storage_path / f"feedback_{analysis_id}_{int(time.time())}.json"
        
        try:
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_entry, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Feedback submitted for analysis {analysis_id}")
            
            return {
                "status": "success",
                "feedback_id": feedback_file.stem,
                "analysis_id": analysis_id,
                "timestamp": feedback_entry["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Failed to save feedback: {str(e)}", exc_info=True)
            raise
    
    def get_feedback(self, analysis_id: str) -> List[Dict]:
        """
        Get all feedback for a specific analysis
        
        Args:
            analysis_id: Analysis identifier
            
        Returns:
            List of feedback entries
        """
        feedback_entries = []
        
        try:
            for feedback_file in self.storage_path.glob(f"feedback_{analysis_id}_*.json"):
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedback_entries.append(json.load(f))
            
            # Sort by timestamp
            feedback_entries.sort(key=lambda x: x.get("submitted_at", 0), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to load feedback: {str(e)}")
        
        return feedback_entries
    
    def get_all_feedback(self, limit: int = 100) -> List[Dict]:
        """
        Get all feedback entries (limited)
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of feedback entries
        """
        feedback_entries = []
        
        try:
            for feedback_file in sorted(
                self.storage_path.glob("feedback_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:limit]:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedback_entries.append(json.load(f))
        
        except Exception as e:
            logger.error(f"Failed to load feedback: {str(e)}")
        
        return feedback_entries
    
    def aggregate_feedback(self, analysis_id: str) -> Dict:
        """
        Aggregate feedback for an analysis
        
        Args:
            analysis_id: Analysis identifier
            
        Returns:
            Aggregated feedback statistics
        """
        feedback_entries = self.get_feedback(analysis_id)
        
        if not feedback_entries:
            return {
                "analysis_id": analysis_id,
                "total_feedback": 0,
                "aggregated": {}
            }
        
        # Aggregate by feedback type
        aggregated = {}
        
        for entry in feedback_entries:
            feedback_type = entry.get("feedback_type", "unknown")
            feedback_data = entry.get("feedback_data", {})
            
            if feedback_type not in aggregated:
                aggregated[feedback_type] = {
                    "count": 0,
                    "data": []
                }
            
            aggregated[feedback_type]["count"] += 1
            aggregated[feedback_type]["data"].append(feedback_data)
        
        # Calculate averages for numeric feedback
        for feedback_type, data in aggregated.items():
            numeric_values = []
            for item in data["data"]:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, (int, float)):
                            numeric_values.append(value)
            
            if numeric_values:
                aggregated[feedback_type]["average"] = sum(numeric_values) / len(numeric_values)
                aggregated[feedback_type]["min"] = min(numeric_values)
                aggregated[feedback_type]["max"] = max(numeric_values)
        
        return {
            "analysis_id": analysis_id,
            "total_feedback": len(feedback_entries),
            "aggregated": aggregated,
            "latest_feedback": feedback_entries[0] if feedback_entries else None
        }
    
    def format_feedback_for_analysis(self, analysis_id: str) -> str:
        """
        Format feedback as text for inclusion in analysis
        
        Args:
            analysis_id: Analysis identifier
            
        Returns:
            Formatted feedback text
        """
        aggregated = self.aggregate_feedback(analysis_id)
        
        if aggregated["total_feedback"] == 0:
            return "No human feedback available for this analysis."
        
        formatted = ["=== HUMAN FEEDBACK ===\n"]
        formatted.append(f"Total feedback entries: {aggregated['total_feedback']}\n")
        
        for feedback_type, data in aggregated["aggregated"].items():
            formatted.append(f"{feedback_type.upper()}:")
            formatted.append(f"  Count: {data['count']}")
            
            if "average" in data:
                formatted.append(f"  Average Score: {data['average']:.2f}")
                formatted.append(f"  Range: {data['min']:.2f} - {data['max']:.2f}")
            
            # Include latest comments
            latest = aggregated.get("latest_feedback")
            if latest and latest.get("comments"):
                formatted.append(f"  Latest Comment: {latest['comments']}")
            
            formatted.append("")
        
        return "\n".join(formatted)


# Global instance
feedback_handler = HumanFeedback()
