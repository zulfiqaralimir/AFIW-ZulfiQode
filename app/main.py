from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
import time
import logging

import app.settings as settings
from app.models.schemas import AnalysisResponse
from app.core.logger import setup_logging
from app.core.middleware import ObservabilityMiddleware
from app.core.metrics import MetricsCollector, AGENT_TASKS, REQUEST_LATENCY, ERROR_COUNT
from app.core import metrics as metrics_module
from app.data.extractor import extract_text_from_pdf, extract_data_from_csv
from app.data.youtube import fetch_youtube_transcript_from_pdf
from app.agents.graph import run_agent_pipeline

# Initialize structured logging
setup_logging(level="INFO", json_format=True)
logger = logging.getLogger(__name__)
metrics = MetricsCollector()

# Create FastAPI app
app = FastAPI(title=settings.PROJECT_NAME)

# Add observability middleware (must be before CORS)
app.add_middleware(ObservabilityMiddleware)

# Enable CORS for local development (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include metrics router
app.include_router(metrics_module.router)

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# Main analyze route with PDF + CSV support
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    request: Request,
    pdf_file: UploadFile = File(None),
    csv_file: UploadFile = File(None)
):
    request_id = getattr(request.state, "request_id", "unknown")
    start_time = time.time()
    file_types = []
    
    logger.info(
        "Analysis request started",
        extra={
            "request_id": request_id,
            "has_pdf": pdf_file is not None,
            "has_csv": csv_file is not None,
            "component": "analyze"
        }
    )
    
    try:
        # Increment agent tasks counter
        AGENT_TASKS.inc()
        
        # Step 1: Extract data from uploaded files
        pdf_text = ""
        csv_summary = ""

        if pdf_file:
            file_types.append("pdf")
            logger.debug(f"Processing PDF: {pdf_file.filename}", extra={"request_id": request_id})
            pdf_bytes = await pdf_file.read()
            pdf_text = extract_text_from_pdf(pdf_bytes)
            logger.debug(f"PDF extracted: {len(pdf_text)} chars", extra={"request_id": request_id})

        if csv_file:
            file_types.append("csv")
            logger.debug(f"Processing CSV: {csv_file.filename}", extra={"request_id": request_id})
            csv_bytes = await csv_file.read()
            df = extract_data_from_csv(csv_bytes)
            csv_summary = df.describe().to_string()
            logger.debug(f"CSV processed: {len(df)} rows", extra={"request_id": request_id})

        # Step 2: Combine data into one text blob
        combined_input = pdf_text + "\n\n" + csv_summary
        
        if not combined_input.strip():
            logger.warning("Empty input received", extra={"request_id": request_id})
            return JSONResponse(
                status_code=400,
                content={"error": "No content extracted from uploaded files"}
            )

        # Step 3: Run through multi-agent system
        logger.info("Running agent pipeline", extra={"request_id": request_id})
        agent_results = run_agent_pipeline(combined_input)
        logger.info("Agent pipeline completed", extra={"request_id": request_id})

        # Step 4: Format output
        summary_text = "\n".join([f"[{step['task']}]\n{step['result']}" for step in agent_results['steps']])
        latency = int((time.time() - start_time) * 1000)
        
        # Record metrics
        file_type_str = "+".join(file_types) if file_types else "none"
        metrics.record_analysis(file_type_str, "success", time.time() - start_time)
        
        logger.info(
            "Analysis completed successfully",
            extra={
                "request_id": request_id,
                "duration_ms": latency,
                "file_types": file_type_str,
                "component": "analyze"
            }
        )

        return AnalysisResponse(
            summary=summary_text,
            ethical_flags=agent_results["flags"],
            latency_ms=latency
        )
        
    except Exception as e:
        duration = time.time() - start_time
        error_type = type(e).__name__
        
        # Record error metrics
        file_type_str = "+".join(file_types) if file_types else "none"
        metrics.record_analysis(file_type_str, "error", duration)
        metrics.record_error(error_type, "analyze")
        
        logger.error(
            f"Analysis failed: {str(e)}",
            extra={
                "request_id": request_id,
                "error_type": error_type,
                "duration_ms": int(duration * 1000),
                "component": "analyze"
            },
            exc_info=True
        )
        
        # Record error
        ERROR_COUNT.inc()
        
        return JSONResponse(
            status_code=500,
            content={"error": f"Analysis failed: {str(e)}"}
        )
    finally:
        # Record request latency
        duration = time.time() - start_time
        REQUEST_LATENCY.observe(duration)


# Analyze YouTube video transcript from PDF about PSX
@app.post("/analyze_youtube")
async def analyze_youtube(request: Request, pdf_file: UploadFile = File(...)):
    request_id = getattr(request.state, "request_id", "unknown")
    start_time = time.time()
    logger.info("YouTube transcript analysis started", extra={"request_id": request_id, "filename": pdf_file.filename})
    
    try:
        # Increment agent tasks counter
        AGENT_TASKS.inc()
        # Save uploaded PDF temporarily
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf_bytes = await pdf_file.read()
            tmp_file.write(pdf_bytes)
            tmp_path = tmp_file.name
        
        try:
            transcript = fetch_youtube_transcript_from_pdf(tmp_path)
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        if not transcript:
            return JSONResponse(status_code=404, content={"error": "Could not extract text from PDF transcript"})

        # Optional: narrow to Pakistan Stock Exchange mentions
        psx_terms = ["psx", "pakistan stock exchange", "kse", "kse-100", "karachi stock exchange"]
        if not any(term in transcript.lower() for term in psx_terms):
            logger.warning("No PSX mentions detected in transcript", extra={"request_id": request_id})

        agent_results = run_agent_pipeline(transcript)
        summary_text = "\n".join([f"[{step['task']}]\n{step['result']}" for step in agent_results['steps']])
        latency = int((time.time() - start_time) * 1000)

        logger.info("YouTube transcript analysis completed", extra={"request_id": request_id, "duration_ms": latency})
        return {
            "summary": summary_text,
            "ethical_flags": agent_results["flags"],
            "latency_ms": latency,
            "source": "youtube_pdf",
        }
    except Exception as e:
        duration = int((time.time() - start_time) * 1000)
        logger.error("YouTube transcript analysis failed", extra={"request_id": request_id, "error_type": type(e).__name__, "duration_ms": duration}, exc_info=True)
        # Record error
        ERROR_COUNT.inc()
        return JSONResponse(status_code=500, content={"error": f"YouTube transcript analysis failed: {str(e)}"})
    finally:
        # Record request latency
        duration = time.time() - start_time
        REQUEST_LATENCY.observe(duration)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
