# Observability Guide

This project includes comprehensive observability features for monitoring, logging, and metrics collection.

## Features

### 1. **Structured JSON Logging**
- All logs are output in JSON format for easy parsing
- Includes request IDs, timestamps, component names, and context
- Logs can be sent to log aggregation tools (ELK, Loki, CloudWatch, etc.)

### 2. **Prometheus Metrics**
- HTTP request metrics (count, duration, status codes)
- Analysis request metrics (by file type, success/error)
- Agent task metrics (individual task performance)
- OpenAI API call metrics (duration, success/error)
- Error tracking by type and component
- Active request gauge

### 3. **Request Tracing**
- Automatic request ID generation for all requests
- Request ID included in response headers (`X-Request-ID`)
- Response time in headers (`X-Response-Time-MS`)
- Full request lifecycle logging

### 4. **Health & Metrics Endpoints**
- `GET /health` - Health check endpoint
- `GET /metrics` - Prometheus metrics endpoint

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure logging level (optional):**
   Edit `app/main.py`:
   ```python
   setup_logging(level="DEBUG", json_format=True)  # or "INFO", "WARNING", "ERROR"
   ```

## Usage

### Viewing Logs

Logs are output to stdout in JSON format. Example:
```json
{
  "timestamp": "2025-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "app.main",
  "message": "Analysis request started",
  "request_id": "abc12345",
  "has_pdf": true,
  "has_csv": false,
  "component": "analyze"
}
```

### Viewing Metrics

Access Prometheus metrics at:
```
http://localhost:8000/metrics
```

Example metrics output:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/analyze",status_code="200"} 5.0

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="POST",endpoint="/analyze",le="0.1"} 2.0
http_request_duration_seconds_bucket{method="POST",endpoint="/analyze",le="0.5"} 4.0

# HELP analysis_requests_total Total analysis requests processed
# TYPE analysis_requests_total counter
analysis_requests_total{file_type="pdf",status="success"} 3.0
```

### Health Check

Check service health:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "AFIW-ZulfiQode"
}
```

## Integration with Monitoring Tools

### Prometheus + Grafana

1. **Configure Prometheus** to scrape metrics:
   ```yaml
   scrape_configs:
     - job_name: 'afiw-zulfiqode'
       static_configs:
         - targets: ['localhost:8000']
   ```

2. **Import Grafana Dashboard:**
   - Use Prometheus as data source
   - Create dashboards using metrics:
     - `http_requests_total`
     - `http_request_duration_seconds`
     - `analysis_requests_total`
     - `analysis_duration_seconds`
     - `agent_task_duration_seconds`
     - `openai_api_calls_total`
     - `errors_total`

### Log Aggregation

#### ELK Stack (Elasticsearch, Logstash, Kibana)
- Send JSON logs to Logstash
- Parse with JSON filter
- Visualize in Kibana

#### CloudWatch (AWS)
- Use CloudWatch Logs Agent
- JSON logs are automatically parsed
- Create CloudWatch Insights queries

#### Loki (Grafana)
- Use Promtail to collect logs
- Query in Grafana with LogQL

## Available Metrics

### HTTP Metrics
- `http_requests_total` - Total requests by method, endpoint, status
- `http_request_duration_seconds` - Request duration histogram

### Analysis Metrics
- `analysis_requests_total` - Total analysis requests by file type and status
- `analysis_duration_seconds` - Analysis duration histogram

### Agent Metrics
- `agent_task_duration_seconds` - Individual task duration by task name

### OpenAI Metrics
- `openai_api_calls_total` - Total API calls by model and status
- `openai_api_duration_seconds` - API call duration by model

### System Metrics
- `active_requests` - Current number of active requests
- `errors_total` - Total errors by type and component

## Customization

### Adding Custom Metrics

Edit `app/core/metrics.py`:
```python
custom_metric = Counter(
    "custom_metric_total",
    "Description",
    ["label1", "label2"]
)
```

### Adding Custom Logging

In your code:
```python
import logging

logger = logging.getLogger(__name__)

logger.info(
    "Custom message",
    extra={
        "request_id": request_id,
        "custom_field": value,
        "component": "your_component"
    }
)
```

## Troubleshooting

### Logs not appearing
- Check logging level in `app/main.py`
- Verify `setup_logging()` is called

### Metrics not updating
- Ensure metrics are recorded after operations
- Check `/metrics` endpoint is accessible

### Request IDs missing
- Verify `ObservabilityMiddleware` is added before CORS middleware
- Check middleware order in `app/main.py`

## Best Practices

1. **Use structured logging** - Always include context in `extra` dict
2. **Track errors** - Use `metrics.record_error()` for all exceptions
3. **Monitor key metrics** - Set up alerts on:
   - High error rates
   - Slow request durations
   - OpenAI API failures
4. **Request tracing** - Use request IDs to trace requests across services
5. **Log aggregation** - Send logs to centralized system for production

