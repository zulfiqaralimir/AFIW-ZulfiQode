from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import time

import app.settings as settings
from app.models.schemas import AnalysisResponse
from app.core.logger import setup_logging
from app.data.extractor import extract_text_from_pdf, extract_data_from_csv
from app.agents.graph import run_agent_pipeline

# Initialize logging
setup_logging()

# Create FastAPI app
app = FastAPI(title=settings.PROJECT_NAME)

# Enable CORS for local development (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Main analyze route with PDF + CSV support
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    pdf_file: UploadFile = File(None),
    csv_file: UploadFile = File(None)
):
    start_time = time.time()

    # Step 1: Extract data from uploaded files
    pdf_text = ""
    csv_summary = ""

    if pdf_file:
        pdf_bytes = await pdf_file.read()
        pdf_text = extract_text_from_pdf(pdf_bytes)

    if csv_file:
        csv_bytes = await csv_file.read()
        df = extract_data_from_csv(csv_bytes)
        csv_summary = df.describe().to_string()

    # Step 2: Combine data into one text blob
    combined_input = pdf_text + "\n\n" + csv_summary

    # Step 3: Run through multi-agent system
    agent_results = run_agent_pipeline(combined_input)

    # Step 4: Format output
    summary_text = "\n".join([f"[{step['task']}]\n{step['result']}" for step in agent_results['steps']])
    latency = int((time.time() - start_time) * 1000)

    return AnalysisResponse(
        summary=summary_text,
        ethical_flags=agent_results["flags"],
        latency_ms=latency
    )
