# Lawyer-AI: Financial Ethics & Risk Analyzer v9.0

## Overview

Lawyer-AI is a comprehensive financial analysis system that evaluates corporate ethics, risk, operations, and financial health. It combines governance data, TradingView indicators, and Pakistan's macroeconomic cycles to produce structured JSON output with confidence scoring.

## Features

- ✅ **12 Analytical Dimensions**: Tone, Ethics, Risk, Source Authenticity, Technical Indicators, Business Cycle Context, CAS, CII, TIT, OCF, GME, FPP
- ✅ **News RSS Integration**: Automatically fetches relevant news articles for context
- ✅ **Human Feedback Mechanism**: Collects and incorporates human feedback for continuous improvement
- ✅ **Structured JSON Output**: Matches exact schema for Neo4j and Prometheus integration
- ✅ **Separate Conclusion**: Provides actionable insights separately from analysis

## Quick Start

### 1. Install Dependencies

```bash
pip install feedparser
```

### 2. API Endpoints

#### Analyze Financial Content

```bash
POST /lawyer_ai/analyze
```

**Request Body:**
```json
{
  "text": "Financial report text to analyze...",
  "financial_data": {
    "total_debt": 500000,
    "total_equity": 1000000,
    "current_assets": 800000,
    "current_liabilities": 600000,
    "stock_prices": [95, 98, 100, 102, 105]
  },
  "company_name": "HASCOL",
  "exchange_code": "PSX-HASCOL",
  "include_news": true,
  "include_feedback": true,
  "include_conclusion": true
}
```

**Response:**
```json
{
  "analysis": {
    "tone": "neutral",
    "tone_confidence": 75,
    "ethical_flag": "questionable",
    "ethical_confidence": 65,
    "risk_level": "moderate",
    "risk_confidence": 70,
    "composite_integrity_index": {
      "cii_score": 72,
      "cii_class": "Moderate",
      "interpretation": "Overall ethical-financial stability."
    },
    "future_performance_perspective": {
      "outlook": "stable",
      "forward_risk_level": "moderate",
      "confidence": 75
    },
    ...
  },
  "conclusion": "Comprehensive conclusion text...",
  "news_context": [...],
  "human_feedback": {...},
  "metadata": {
    "analysis_id": "uuid",
    "latency_ms": 1234
  }
}
```

#### Submit Human Feedback

```bash
POST /lawyer_ai/feedback
```

**Request Body:**
```json
{
  "analysis_id": "uuid-of-analysis",
  "feedback_type": "accuracy",
  "feedback_data": {
    "score": 85,
    "notes": "Analysis was accurate but missed some details"
  },
  "user_id": "user123",
  "comments": "Overall good analysis"
}
```

#### Get Feedback

```bash
GET /lawyer_ai/feedback/{analysis_id}
```

#### Get News Articles

```bash
GET /lawyer_ai/news?company_name=HASCOL&keywords=financial,risk&days=30&max_articles=10
```

## Python Usage

### Basic Analysis

```python
from app.agents.lawyer_ai import LawyerAI

# Initialize Lawyer-AI
lawyer_ai = LawyerAI()

# Perform analysis
analysis = lawyer_ai.analyze(
    text="Financial report text...",
    financial_data={
        "total_debt": 500000,
        "total_equity": 1000000
    },
    company_name="HASCOL",
    exchange_code="PSX-HASCOL"
)

print(f"CII Score: {analysis['composite_integrity_index']['cii_score']}")
```

### Analysis with Conclusion

```python
from app.agents.lawyer_ai import LawyerAI
from app.data.news_rss import NewsRSSFeed
from app.core.feedback import feedback_handler

# Initialize components
lawyer_ai = LawyerAI()
news_feed = NewsRSSFeed()

# Fetch news
news_articles = news_feed.get_recent_news(
    company_name="HASCOL",
    days=30
)

# Get existing feedback
feedback = feedback_handler.aggregate_feedback("analysis-id")

# Analyze with conclusion
result = lawyer_ai.analyze_with_conclusion(
    text="Financial report...",
    financial_data={...},
    company_name="HASCOL",
    news_context=news_articles,
    human_feedback=feedback
)

print("Analysis:", result["analysis"])
print("Conclusion:", result["conclusion"])
```

### News RSS Integration

```python
from app.data.news_rss import NewsRSSFeed

# Initialize feed handler
news_feed = NewsRSSFeed()

# Get recent news for a company
articles = news_feed.get_recent_news(
    company_name="HASCOL",
    keywords=["financial", "risk"],
    days=30,
    max_articles=10
)

# Format for analysis
news_text = news_feed.format_for_analysis(articles)
```

### Human Feedback

```python
from app.core.feedback import feedback_handler

# Submit feedback
result = feedback_handler.submit_feedback(
    analysis_id="analysis-uuid",
    feedback_type="accuracy",
    feedback_data={"score": 85, "notes": "Good analysis"},
    user_id="user123",
    comments="Overall accurate"
)

# Get feedback
feedback = feedback_handler.get_feedback("analysis-uuid")

# Aggregate feedback
aggregated = feedback_handler.aggregate_feedback("analysis-uuid")
```

## Output Schema

The Lawyer-AI analysis produces a comprehensive JSON structure with:

1. **Tone Analysis**: Sentiment with confidence scores
2. **Ethical Flags**: Governance integrity assessment
3. **Risk Level**: Financial/reputational exposure
4. **Source Authenticity**: Reliability of inputs
5. **Technical Analysis**: RSI(14) and 200-day MA indicators
6. **Business Cycle Context**: Pakistan macro cycle alignment
7. **Cycle Alignment Score (CAS)**: Alignment with macro phase
8. **Composite Integrity Index (CII)**: Overall ethical-financial integrity
9. **Temporal Integrity Trend (TIT)**: Quarter-to-quarter change
10. **Operational Cash Flow (OCF)**: Operational sustainability
11. **Gross Margin Effect (GME)**: Pricing power and efficiency
12. **Future Performance Perspective (FPP)**: Forward-looking outlook
13. **Hallucination Metrics**: Reliability assessment

## Key Formulas

### Cycle Alignment Score (CAS)
```
CAS = 0.35×FinancialTrend + 0.25×MarketMomentum + 0.25×SectorCorrelation + 0.15×MacroCoherence
```

### Composite Integrity Index (CII)
```
CII = 0.35×Ethics + 0.25×(100−Risk) + 0.20×Technical + 0.20×CycleAlign
```

### Temporal Integrity Trend (TIT)
```
TIT = CII_current − CII_previous
```

## Pakistan Business Cycle

10-year alternating phases (±2–4 yrs):

| Cycle | Period  | Phase                   |
| :---- | :------ | :---------------------- |
| 1     | 1947–57 | Bearish                 |
| 2     | 1958–68 | Bullish                 |
| 3     | 1969–79 | Bearish                 |
| 4     | 1980–90 | Bullish                 |
| 5     | 1991–01 | Bearish                 |
| 6     | 2002–12 | Bullish                 |
| 7     | 2013–23 | Bearish                 |
| 8     | 2024–34 | **Bullish (Projected)** |

## Integration Examples

### Neo4j

```cypher
(:Company {
  name: "HASCOL",
  ethics: "questionable",
  risk: "moderate",
  CII: 72,
  TIT: 3,
  OCF: "positive",
  GME: "expanding",
  FPP: "stable"
})
```

### Prometheus

```
lawyer_ai_composite_integrity_index{company="HASCOL"} 72
lawyer_ai_operational_cash_flow_confidence{company="HASCOL"} 85
lawyer_ai_future_performance_outlook{company="HASCOL"} 70
```

## Best Practices

1. **Always include company_name and exchange_code** for better TradingView integration
2. **Enable include_news** for richer context from recent news articles
3. **Submit feedback** after reviewing analyses to improve future results
4. **Use include_conclusion** for actionable insights separate from raw analysis
5. **Monitor CII and TIT** for trend analysis over time

## Error Handling

The system handles various error scenarios:

- **Missing data**: Returns "not available" with confidence = 0
- **API errors**: Logged and returned with error details
- **News fetch failures**: Analysis continues without news context
- **Feedback retrieval failures**: Analysis continues without feedback

## Metrics

All Lawyer-AI operations are tracked in Prometheus:

- `openai_api_calls_total{model="lawyer-ai", status="success|error"}`
- `agent_tasks_total` (includes Lawyer-AI analyses)
- `request_latency_seconds`

View metrics at: `http://localhost:8000/metrics`

## API Documentation

Once your server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

You'll see all Lawyer-AI endpoints documented with full request/response schemas.

