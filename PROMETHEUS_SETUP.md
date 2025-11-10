# Prometheus Metrics Setup Guide

## Overview

Lawyer-AI automatically exports metrics to Prometheus for monitoring and visualization in Grafana.

## Metrics Exported

### Lawyer-AI Metrics (Gauge)

1. **`lawyer_ai_composite_integrity_index{company="HASCOL"}`**
   - Composite Integrity Index (CII) score (0-100)
   - Higher = better ethical-financial integrity

2. **`lawyer_ai_risk_level{company="HASCOL"}`**
   - Risk confidence score (0-100)
   - Higher = higher risk confidence

3. **`lawyer_ai_tone_confidence{company="HASCOL"}`**
   - Tone confidence score (0-100)
   - Confidence in sentiment analysis

4. **`lawyer_ai_hallucination_score{company="HASCOL"}`**
   - Hallucination reliability score (0-100)
   - Higher = more reliable outputs

5. **`lawyer_ai_news_score{company="HASCOL"}`** (Optional)
   - News sentiment score (0-100)
   - Calculated from news context

6. **`lawyer_ai_hf_quality_score{company="HASCOL"}`** (Optional)
   - Human feedback quality score (0-100)
   - Average of feedback scores

## Setup

### 1. Prometheus HTTP Server

The Prometheus HTTP server starts automatically when you run the FastAPI app:

```python
# In app/main.py
from prometheus_client import start_http_server

# Start Prometheus HTTP server on port 8001
start_http_server(8001)
```

**Metrics Endpoint:** `http://localhost:8001/metrics`

### 2. Prometheus Configuration

Create or update `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'lawyer_ai'
    static_configs:
      - targets: ['localhost:8001']
```

### 3. Start Prometheus

```bash
prometheus --config.file=prometheus.yml
```

Prometheus will scrape metrics from `http://localhost:8001/metrics`

## Usage

### Automatic Metrics Recording

Metrics are automatically recorded when you run Lawyer-AI analysis:

```python
from app.agents.lawyer_ai import LawyerAI

lawyer_ai = LawyerAI()
analysis = lawyer_ai.analyze(
    text="Financial report...",
    company_name="HASCOL"
)

# Metrics are automatically pushed to Prometheus
# lawyer_ai_composite_integrity_index{company="HASCOL"} 74
# lawyer_ai_risk_level{company="HASCOL"} 90
# lawyer_ai_tone_confidence{company="HASCOL"} 75
# lawyer_ai_hallucination_score{company="HASCOL"} 82
```

### Manual Metrics Update

You can also manually update metrics:

```python
from app.core.metrics import update_metrics

update_metrics("HASCOL", analysis_output)
```

## Viewing Metrics

### 1. Direct HTTP Access

```bash
curl http://localhost:8001/metrics
```

You'll see:
```
# HELP lawyer_ai_composite_integrity_index Composite Integrity Index (CII) score from Lawyer-AI analysis
# TYPE lawyer_ai_composite_integrity_index gauge
lawyer_ai_composite_integrity_index{company="HASCOL"} 74.0

# HELP lawyer_ai_risk_level Risk level (0-100) from Lawyer-AI analysis
# TYPE lawyer_ai_risk_level gauge
lawyer_ai_risk_level{company="HASCOL"} 90.0

# HELP lawyer_ai_tone_confidence Tone confidence from Lawyer-AI analysis
# TYPE lawyer_ai_tone_confidence gauge
lawyer_ai_tone_confidence{company="HASCOL"} 75.0

# HELP lawyer_ai_hallucination_score Hallucination score from Lawyer-AI analysis
# TYPE lawyer_ai_hallucination_score gauge
lawyer_ai_hallucination_score{company="HASCOL"} 82.0
```

### 2. Prometheus UI

1. Start Prometheus: `prometheus --config.file=prometheus.yml`
2. Open: `http://localhost:9090`
3. Query: `lawyer_ai_composite_integrity_index{company="HASCOL"}`

### 3. Grafana Dashboard

Create a Grafana dashboard with queries like:

```promql
# CII Score over time
lawyer_ai_composite_integrity_index{company="HASCOL"}

# Risk Level
lawyer_ai_risk_level{company="HASCOL"}

# Hallucination Score
lawyer_ai_hallucination_score{company="HASCOL"}

# All companies comparison
lawyer_ai_composite_integrity_index
```

## Example Grafana Queries

### Single Company Metrics

```promql
# CII Score
lawyer_ai_composite_integrity_index{company="HASCOL"}

# Risk Level
lawyer_ai_risk_level{company="HASCOL"}

# Tone Confidence
lawyer_ai_tone_confidence{company="HASCOL"}

# Hallucination Score
lawyer_ai_hallucination_score{company="HASCOL"}
```

### Multi-Company Comparison

```promql
# Compare CII across all companies
lawyer_ai_composite_integrity_index

# Average CII across all companies
avg(lawyer_ai_composite_integrity_index)

# Companies with CII > 70
lawyer_ai_composite_integrity_index > 70
```

### Time Series

```promql
# CII over time (if you have historical data)
rate(lawyer_ai_composite_integrity_index{company="HASCOL"}[5m])
```

## Ports

- **FastAPI Server:** `http://localhost:8000`
- **Prometheus Metrics:** `http://localhost:8001/metrics`
- **Prometheus UI:** `http://localhost:9090` (if running Prometheus)
- **Grafana:** `http://localhost:3000` (if running Grafana)

## Troubleshooting

### Metrics not appearing

1. **Check Prometheus server is running:**
   ```bash
   curl http://localhost:8001/metrics
   ```

2. **Check Prometheus config:**
   - Verify `prometheus.yml` has correct target
   - Check Prometheus logs for errors

3. **Check company name:**
   - Metrics are only recorded if `company_name` is provided
   - Verify company name in analysis request

### Port already in use

If port 8001 is already in use:
- Change port in `app/main.py`:
  ```python
  start_http_server(8002)  # Use different port
  ```
- Update `prometheus.yml` target accordingly

## Integration with Existing Metrics

The Lawyer-AI metrics are in addition to existing Prometheus metrics:
- `http_requests_total`
- `openai_api_calls_total`
- `agent_tasks_total`
- `request_latency_seconds`
- And more...

All metrics are available at:
- FastAPI endpoint: `http://localhost:8000/metrics`
- Prometheus server: `http://localhost:8001/metrics`

## Next Steps

1. **Set up Prometheus** using `prometheus.yml`
2. **Create Grafana dashboard** with Lawyer-AI metrics
3. **Set up alerts** for low CII scores or high risk levels
4. **Monitor trends** over time for multiple companies

