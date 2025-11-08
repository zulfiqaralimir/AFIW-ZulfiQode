"""
Prometheus-style metrics collection for observability
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
from typing import Optional
import time

# Create metrics router
router = APIRouter()

# Request metrics
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

# Business metrics
analysis_requests_total = Counter(
    "analysis_requests_total",
    "Total analysis requests processed",
    ["file_type", "status"]
)

analysis_duration_seconds = Histogram(
    "analysis_duration_seconds",
    "Analysis processing duration in seconds",
    ["file_type"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

agent_task_duration_seconds = Histogram(
    "agent_task_duration_seconds",
    "Individual agent task duration",
    ["task_name"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# System metrics
openai_api_calls_total = Counter(
    "openai_api_calls_total",
    "Total OpenAI API calls",
    ["model", "status"]
)

openai_api_duration_seconds = Histogram(
    "openai_api_duration_seconds",
    "OpenAI API call duration",
    ["model"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

active_requests = Gauge(
    "active_requests",
    "Number of active requests being processed"
)

# Error metrics
errors_total = Counter(
    "errors_total",
    "Total errors encountered",
    ["error_type", "component"]
)

# Additional simplified metrics for direct endpoint usage
REQUEST_LATENCY = Histogram("request_latency_seconds", "API request latency in seconds")
ERROR_COUNT = Counter("errors_total_simple", "Total API errors (simplified)")
HALLUCINATION_ALERTS = Counter("hallucination_alerts_total", "Hallucination alerts detected")
AGENT_TASKS = Counter("agent_tasks_total", "Agent tasks executed")


class MetricsCollector:
    """Context manager for collecting metrics"""
    
    @staticmethod
    def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    @staticmethod
    def record_analysis(file_type: str, status: str, duration: float):
        """Record analysis request metrics"""
        analysis_requests_total.labels(file_type=file_type, status=status).inc()
        analysis_duration_seconds.labels(file_type=file_type).observe(duration)
    
    @staticmethod
    def record_agent_task(task_name: str, duration: float):
        """Record agent task metrics"""
        agent_task_duration_seconds.labels(task_name=task_name).observe(duration)
    
    @staticmethod
    def record_openai_call(model: str, status: str, duration: float):
        """Record OpenAI API call metrics"""
        openai_api_calls_total.labels(model=model, status=status).inc()
        openai_api_duration_seconds.labels(model=model).observe(duration)
    
    @staticmethod
    def record_error(error_type: str, component: str):
        """Record error occurrence"""
        errors_total.labels(error_type=error_type, component=component).inc()
    
    @staticmethod
    def get_metrics() -> bytes:
        """Get Prometheus metrics in text format"""
        return generate_latest()


# Metrics endpoint route
@router.get("/metrics")
def get_metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


class RequestTimer:
    """Context manager for timing requests"""
    
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
