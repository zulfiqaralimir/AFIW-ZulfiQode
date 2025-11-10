from pydantic import BaseModel
from typing import Dict, Union, Optional, List

# -----------------------------------------------------
# ✅ Input model (for text-based requests — optional)
# -----------------------------------------------------
class AnalysisRequest(BaseModel):
    """
    Accepts plain text input for analysis.
    Although the main route uses file uploads,
    this class is retained for future extensions.
    """
    content: str


# -----------------------------------------------------
# ✅ Output model for response
# -----------------------------------------------------
class AnalysisResponse(BaseModel):
    """
    Standardized API response for the AFIW–ZulfiQode system.
    Includes:
    - AI-generated summary
    - Ethical evaluation flags
    - Latency and performance metrics
    """
    summary: str
    # Allow either a simple string ("Red Flag"/"Clear") or a detailed dict
    # with numeric/boolean metrics and a string status field
    ethical_flags: Dict[str, Union[str, Dict[str, Union[int, bool, str]]]]
    latency_ms: int


# -----------------------------------------------------
# ✅ Lawyer-AI Request/Response Models
# -----------------------------------------------------
class LawyerAIRequest(BaseModel):
    """Request model for Lawyer-AI analysis"""
    text: str
    financial_data: Optional[Dict] = None
    company_name: Optional[str] = None
    exchange_code: Optional[str] = None
    include_news: bool = True
    include_feedback: bool = True
    include_conclusion: bool = True
    use_agents: bool = False  # Use agent orchestration instead of GPT


class LawyerAIResponse(BaseModel):
    """Response model for Lawyer-AI analysis"""
    analysis: Dict
    conclusion: Optional[str] = None
    news_context: Optional[List[Dict]] = None
    human_feedback: Optional[Dict] = None
    metadata: Dict


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback"""
    analysis_id: str
    feedback_type: str
    feedback_data: Dict
    user_id: Optional[str] = None
    comments: Optional[str] = None
