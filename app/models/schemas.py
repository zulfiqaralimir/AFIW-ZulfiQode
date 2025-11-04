from pydantic import BaseModel
from typing import Dict, Union, Optional

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
    ethical_flags: Dict[str, Union[str, Dict[str, Union[int, bool]]]]
    latency_ms: int
