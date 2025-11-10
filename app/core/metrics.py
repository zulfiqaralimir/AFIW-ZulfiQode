"""
Prometheus-style metrics collection for observability
"""
from prometheus_client import Gauge, start_http_server, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
from typing import Optional, Dict
import time
from app.core.logger import get_logger

logger = get_logger(__name__)

# Create metrics router
router = APIRouter()

# Request metrics (backward compatibility)
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

active_requests = Gauge(
    "active_requests",
    "Number of active requests"
)

# Additional simplified metrics for direct endpoint usage (backward compatibility)
REQUEST_LATENCY = Histogram("request_latency_seconds", "API request latency in seconds")
ERROR_COUNT = Counter("errors_total_simple", "Total API errors (simplified)")
HALLUCINATION_ALERTS = Counter("hallucination_alerts_total", "Hallucination alerts detected")
AGENT_TASKS = Counter("agent_tasks_total", "Agent tasks executed")

# ---------------------------------------------------------
# 📈 Prometheus Metrics Registry
# ---------------------------------------------------------
lawyer_ai_cii = Gauge("lawyer_ai_composite_integrity_index", "Composite Integrity Index (CII)", ["company"])
lawyer_ai_ocf_conf = Gauge("lawyer_ai_operational_cash_flow_confidence", "OCF Confidence", ["company"])
lawyer_ai_risk_conf = Gauge("lawyer_ai_risk_confidence", "Risk Confidence", ["company"])
lawyer_ai_fpp_conf = Gauge("lawyer_ai_future_performance_confidence", "FPP Confidence", ["company"])
lawyer_ai_hs = Gauge("lawyer_ai_hallucination_score", "Hallucination Score", ["company"])

# Backward compatibility - keep old metric names for compatibility
lawyer_ai_composite_integrity_index = lawyer_ai_cii
lawyer_ai_risk_level = lawyer_ai_risk_conf
lawyer_ai_tone_confidence = Gauge("lawyer_ai_tone_confidence", "Tone confidence from Lawyer-AI analysis", ["company"])
lawyer_ai_hallucination_score = lawyer_ai_hs

# ---------------------------------------------------------
def start_prometheus_server(port: int = 8001):
    """Starts the Prometheus exporter server."""
    try:
        start_http_server(port)
        logger.info(f"Prometheus metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Prometheus server failed to start: {e}")

# ---------------------------------------------------------
def push_metrics(company: str, data: dict):
    """Pushes Lawyer-AI metrics to Prometheus."""
    try:
        cii = data["composite_integrity_index"]["cii_score"]
        ocf_conf = data["operational_metrics"]["operational_cash_flow"]["ocf_confidence"]
        risk_conf = data["risk_confidence"]
        fpp_conf = data["future_performance_perspective"]["confidence"]
        hs = data["hallucination_metrics"]["hallucination_score"]
        
        lawyer_ai_cii.labels(company=company).set(cii)
        lawyer_ai_ocf_conf.labels(company=company).set(ocf_conf)
        lawyer_ai_risk_conf.labels(company=company).set(risk_conf)
        lawyer_ai_fpp_conf.labels(company=company).set(fpp_conf)
        lawyer_ai_hs.labels(company=company).set(hs)
        
        logger.info(f"✅ Prometheus metrics updated for {company}")
    except Exception as e:
        logger.error(f"Prometheus push failed for {company}: {e}")

# Backward compatibility
def update_metrics(company: str, output: dict):
    """
    Update Prometheus metrics (backward compatibility alias for push_metrics).
    
    Args:
        company: Company name
        output: Complete Lawyer-AI analysis output dictionary
    """
    push_metrics(company, output)

# Backward compatibility - MetricsCollector class
class MetricsCollector:
    """
    Metrics Collector for observability (backward compatibility)
    """
    
    def __init__(self):
        """Initialize metrics collector"""
        pass
    
    def record_agent_task(self, task_name: str, duration: float):
        """Record agent task duration (backward compatibility)"""
        # Placeholder for backward compatibility
        pass
    
    def record_error(self, error_type: str, component: str):
        """Record error (backward compatibility)"""
        # Placeholder for backward compatibility
        pass
    
    def record_analysis(self, file_type: str, status: str, duration: float):
        """Record analysis (backward compatibility)"""
        # Placeholder for backward compatibility
        pass

# Backward compatibility - RequestTimer class
class RequestTimer:
    """Context manager for timing requests (backward compatibility)"""
    
    def __init__(self, collector: MetricsCollector, file_type: Optional[str] = None):
        self.collector = collector
        self.file_type = file_type
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        active_requests.inc()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            status = "error" if exc_type else "success"
            if self.file_type:
                self.collector.record_analysis(self.file_type, status, duration)
        active_requests.dec()

# Backward compatibility - Metrics endpoint
@router.get("/metrics")
def get_metrics_endpoint():
    """Prometheus metrics endpoint (backward compatibility)"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
