# Quick Start Guide - Lawyer-AI Integration

## Step 1: Install Dependencies

Make sure you have all required packages installed:

```bash
pip install feedparser
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Environment Variables

Create or update your `.env` file with your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

## Step 3: Start the FastAPI Backend

Open a terminal and start the FastAPI server:

```bash
# Navigate to project root
cd D:\AFIW_ZulfiQode_Final

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Start Streamlit Dashboard

Open a **new terminal** and run:

```bash
# Navigate to project root
cd D:\AFIW_ZulfiQode_Final

# Start Streamlit
streamlit run streamlit_app/dashboard.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## Step 5: Test Lawyer-AI Analysis

1. **Open your browser** to `http://localhost:8501`

2. **Navigate to "⚖️ Lawyer-AI Analysis"** in the sidebar

3. **Enter test data:**
   - **Company Name:** HASCOL
   - **Exchange Code:** PSX-HASCOL
   - **Financial Report Text:** (paste sample text below)
   - **Financial Data:** (use defaults or enter your own)
   - **Checkboxes:** Enable all (News RSS, Feedback, Conclusion)

4. **Click "🚀 Run Lawyer-AI Analysis"**

5. **Wait 30-60 seconds** for analysis to complete

6. **View results** in the organized tabs:
   - Summary tab: CII, TIT scores
   - Ethics & Risk tab: Tone, Ethics, Risk analysis
   - Technical tab: RSI, MA indicators
   - Business Cycle tab: CAS scores
   - Operations tab: OCF, GME metrics
   - Future Outlook tab: FPP and hallucination metrics

7. **Check the Conclusion** section (separate from analysis)

8. **Submit Feedback** if you want to test the feedback mechanism

## Sample Test Data

### Sample Financial Report Text:
```
HASCOL Petroleum Limited Annual Report 2024

Financial Highlights:
- Total Revenue: PKR 45.2 billion
- Net Profit: PKR 1.8 billion
- Total Assets: PKR 28.5 billion
- Total Debt: PKR 12.3 billion
- Current Ratio: 1.2

The company has shown resilience in challenging market conditions.
Management remains committed to sustainable growth and ethical business practices.
Regulatory compliance has been maintained throughout the reporting period.
```

### Sample Financial Data:
- **Total Debt:** 500000
- **Total Equity:** 1000000
- **Current Assets:** 800000
- **Current Liabilities:** 600000
- **Stock Prices:** 95,98,100,102,105,104,107,106

## Step 6: Verify API Endpoints

You can also test the API directly:

### Test Lawyer-AI Analysis Endpoint:
```bash
curl -X POST "http://localhost:8000/lawyer_ai/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "HASCOL Petroleum Limited Annual Report 2024. Financial Highlights show strong performance.",
    "financial_data": {
      "total_debt": 500000,
      "total_equity": 1000000,
      "current_assets": 800000,
      "current_liabilities": 600000,
      "stock_prices": [95,98,100,102,105,104,107,106]
    },
    "company_name": "HASCOL",
    "exchange_code": "PSX-HASCOL",
    "include_news": true,
    "include_feedback": true,
    "include_conclusion": true
  }'
```

### Test News RSS Endpoint:
```bash
curl "http://localhost:8000/lawyer_ai/news?company_name=HASCOL&days=30&max_articles=10"
```

### Test Feedback Endpoint:
```bash
curl -X POST "http://localhost:8000/lawyer_ai/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "your-analysis-id",
    "feedback_type": "accuracy",
    "feedback_data": {"score": 85},
    "comments": "Good analysis"
  }'
```

## Step 7: View API Documentation

Open in browser:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You'll see all Lawyer-AI endpoints documented with request/response schemas.

## Step 8: Check Metrics

View Prometheus metrics:
- **Metrics Endpoint:** http://localhost:8000/metrics

You'll see:
- `openai_api_calls_total{model="lawyer-ai", status="success|error"}`
- `agent_tasks_total`
- `request_latency_seconds`

## Troubleshooting

### Issue: "Failed to connect to API server"
**Solution:** Make sure FastAPI server is running on port 8000

### Issue: "OpenAI API key not found"
**Solution:** Check your `.env` file has `OPENAI_API_KEY` set

### Issue: "Request timed out"
**Solution:** 
- Analysis may take 30-60 seconds
- Check your OpenAI API key is valid
- Ensure you have API credits

### Issue: "No news articles found"
**Solution:** 
- News RSS feeds may be temporarily unavailable
- Analysis will continue without news context
- Check internet connection

### Issue: "Invalid JSON response"
**Solution:**
- Check OpenAI API is responding correctly
- Verify your API key has access to GPT-4
- Check server logs for detailed errors

## Next Steps

1. **Test with real financial reports** from your PDF files
2. **Submit feedback** to improve future analyses
3. **Integrate with Neo4j** for graph database storage
4. **Set up Prometheus monitoring** for production
5. **Customize RSS feeds** for specific news sources
6. **Add more companies** and compare analyses

## What You'll See

When the analysis completes, you'll get:

✅ **Structured JSON** with all 12 analytical dimensions
✅ **CII Score** (Composite Integrity Index) 0-100
✅ **TIT Value** (Temporal Integrity Trend)
✅ **Technical Analysis** with RSI and MA indicators
✅ **Business Cycle Context** with CAS scores
✅ **Operational Metrics** (OCF, GME)
✅ **Future Performance Perspective** with outlook
✅ **Hallucination Metrics** for reliability assessment
✅ **Separate Conclusion** with actionable insights
✅ **News Context** from RSS feeds (if enabled)
✅ **Human Feedback** integration (if available)

Enjoy testing your Lawyer-AI integration! 🚀

