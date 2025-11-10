"""
FastAPI Application for Lawyer-AI v9.0
Simplified backend with single PDF upload endpoint
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from app.agents.lawyer_ai import LawyerAIOrchestrator
from app.core.logger import setup_logging
from app.core.metrics import start_prometheus_server
from app.models.schemas import FeedbackRequest
import json
import time
import os

# ---------------------------
# Initialize FastAPI App
# ---------------------------
app = FastAPI(
    title="Lawyer-AI Financial Ethics & Risk Analyzer",
    description="Analyzes corporate ethics, risk, and financial integrity based on PDF reports + live market data.",
    version="9.0"
)

# ---------------------------
# Prometheus metrics setup
# ---------------------------
# ✅ Setup metrics before defining routes
instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app, include_in_schema=False, should_gzip=True)

# ---------------------------
# Enable CORS for Streamlit
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Logging & Prometheus
# ---------------------------
setup_logging()
start_prometheus_server(9000)

# ---------------------------
# API Endpoint: Analyze Company Report
# ---------------------------
@app.post("/lawyer_ai/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Uploads a company's annual report (PDF) and returns a structured JSON output
    following Lawyer-AI v9.0 schema.
    """
    
    start_time = time.time()
    file_bytes = await file.read()
    
    # Initialize orchestrator
    orchestrator = LawyerAIOrchestrator()
    
    try:
        result = orchestrator.run_analysis(file_bytes, file.filename)
        
        # Add metadata
        result["metadata"] = {
            "filename": file.filename,
            "processing_time_sec": round(time.time() - start_time, 2),
            "model_version": "Lawyer-AI v9.0",
        }
        
        return result
    
    except Exception as e:
        return {"error": str(e)}

# ---------------------------
# API Endpoint: Submit Feedback
# ---------------------------
@app.post("/lawyer_ai/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submits human feedback for analysis improvement.
    """
    try:
        # Create feedback directory if it doesn't exist
        feedback_dir = "feedback_data"
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Save feedback to file
        feedback_file = os.path.join(feedback_dir, f"{feedback.analysis_id}_feedback.json")
        
        feedback_data = {
            "analysis_id": feedback.analysis_id,
            "feedback_type": feedback.feedback_type,
            "feedback_data": feedback.feedback_data,
            "user_id": feedback.user_id,
            "comments": feedback.comments,
            "timestamp": time.time()
        }
        
        # Append to existing feedback or create new
        if os.path.exists(feedback_file):
            with open(feedback_file, "r") as f:
                existing_feedback = json.load(f)
                if not isinstance(existing_feedback, list):
                    existing_feedback = [existing_feedback]
                existing_feedback.append(feedback_data)
        else:
            existing_feedback = [feedback_data]
        
        with open(feedback_file, "w") as f:
            json.dump(existing_feedback, f, indent=2)
        
        return {"status": "success", "message": "Feedback submitted successfully", "analysis_id": feedback.analysis_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

# ---------------------------
# API Endpoint: Get Feedback
# ---------------------------
@app.get("/lawyer_ai/feedback/{analysis_id}")
async def get_feedback(analysis_id: str):
    """
    Retrieves feedback for a specific analysis.
    """
    try:
        feedback_file = os.path.join("feedback_data", f"{analysis_id}_feedback.json")
        
        if not os.path.exists(feedback_file):
            return {"feedback": [], "message": "No feedback found for this analysis"}
        
        with open(feedback_file, "r") as f:
            feedback_data = json.load(f)
        
        return {"feedback": feedback_data, "analysis_id": analysis_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feedback: {str(e)}")

# ---------------------------
# Root Route
# ---------------------------
@app.get("/")
def root():
    return {"message": "Welcome to Lawyer-AI (AFIW–ZulfiQode)", "version": "9.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
