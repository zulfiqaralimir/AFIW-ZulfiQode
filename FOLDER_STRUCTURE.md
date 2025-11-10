# AFIW-ZulfiQode Project Structure (v9.0)

## 📁 Complete Folder Structure

```
AFIW_ZulfiQode_Final/
│
├── 📄 README.md                                    # Project documentation
├── 📄 LICENSE                                      # License file
├── 📄 requirements.txt                             # Python dependencies (root)
├── 📄 .env                                         # Environment variables (not in repo)
├── 📄 logo.png                                     # Project logo
│
├── 📁 app/                                         # Main FastAPI application
│   ├── 📄 __init__.py
│   ├── 📄 main.py                                  # FastAPI application entry point
│   ├── 📄 settings.py                              # Configuration settings
│   ├── 📄 requirements.txt                         # App-specific dependencies
│   ├── 📄 Dockerfile                               # Docker configuration for FastAPI
│   │
│   ├── 📁 agents/                                  # AI Agent modules (Orchestration)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 executor.py                          # Executor agent (PDF extraction, data enrichment)
│   │   ├── 📄 graph.py                             # Agent pipeline graph
│   │   ├── 📄 judge.py                             # Judge agent (finalization, hallucination metrics)
│   │   ├── 📄 lawyer_ai.py                         # ⭐ Lawyer-AI orchestrator (Planner→Executor→Verifier→Judge)
│   │   ├── 📄 planner.py                           # Planner agent (task planning)
│   │   ├── 📄 risk_analyzer.py                    # Risk analysis agent
│   │   └── 📄 verifier.py                          # Verifier agent (validation, CII, TIT computation)
│   │
│   ├── 📁 core/                                    # Core functionality
│   │   ├── 📄 __init__.py
│   │   ├── 📄 feedback.py                          # ⭐ Human feedback mechanism
│   │   ├── 📄 logger.py                            # Logging configuration
│   │   ├── 📄 metrics.py                           # ⭐ Prometheus metrics (Lawyer-AI metrics)
│   │   └── 📄 middleware.py                        # FastAPI middleware
│   │
│   ├── 📁 data/                                    # Data processing modules
│   │   ├── 📄 __init__.py
│   │   ├── 📄 extractor.py                        # ⭐ Financial data extraction (OCF, GME)
│   │   ├── 📄 neo4j_integration.py                # ⭐ Neo4j database integration
│   │   ├── 📄 news_rss.py                          # ⭐ News RSS feed integration (PSX)
│   │   ├── 📄 trading_view.py                      # ⭐ TradingView data (investing.com, psx.com.pk)
│   │   └── 📄 youtube.py                           # YouTube transcript extraction
│   │
│   ├── 📁 evaluation/                              # Evaluation modules
│   │   ├── 📄 __init__.py
│   │   └── 📄 metrics.py                           # Evaluation metrics
│   │
│   ├── 📁 integrations/                            # External integrations (empty)
│   │
│   └── 📁 models/                                  # Data models and schemas
│       ├── 📄 __init__.py
│       └── 📄 schemas.py                           # ⭐ Pydantic models (LawyerAIRequest, LawyerAIResponse, FeedbackRequest)
│
├── 📁 streamlit_app/                               # Streamlit dashboard
│   ├── 📄 dashboard.py                            # ⭐ Main dashboard (with tabs: Core Metrics, Management Analysis, News Trends, Neo4j Graph)
│   ├── 📄 dashboard_lawyer_ai.py                  # Legacy Lawyer-AI dashboard
│   ├── 📄 Dockerfile                               # Docker configuration for Streamlit
│   ├── 📄 requirements.txt                         # Streamlit-specific dependencies
│   └── 📁 static/
│       └── 📄 logo.png                             # Dashboard logo
│
├── 📁 tests/                                       # Test files
│   ├── 📄 __init__.py
│   ├── 📄 test_app.py                              # Application tests
│   └── 📄 test_risk_analyzer.py                    # Risk analyzer tests
│
├── 📁 feedback_data/                               # ⭐ Human feedback storage
│   └── 📄 *_feedback.json                          # Feedback JSON files (auto-generated)
│
├── 📁 prometheus/                                  # Prometheus configuration
│   └── 📄 prometheus.yml                           # Prometheus scrape configuration
│
├── 📁 grafana/                                     # Grafana dashboards
│   └── 📄 LawyerAI_Dashboard.json                  # ⭐ Grafana dashboard JSON
│
├── 📁 grafana-data/                                # Grafana data storage (Docker volume)
│
├── 📁 venv/                                        # Virtual environment (not in repo)
│
├── 📄 docker-compose.yml                           # ⭐ Docker Compose configuration (lawyer_ai, streamlit, prometheus, grafana)
├── 📄 prometheus.yml                               # Prometheus configuration (root)
│
├── 📄 Documentation Files
│   ├── 📄 LAWYER_AI_INTEGRATION.md                 # ⭐ Lawyer-AI integration guide
│   ├── 📄 QUICK_START.md                           # ⭐ Quick start guide
│   ├── 📄 PROMETHEUS_SETUP.md                      # ⭐ Prometheus setup guide
│   ├── 📄 OBSERVABILITY.md                         # Observability documentation
│   ├── 📄 FOLDER_STRUCTURE.md                      # This file
│   └── 📄 README.md                                # Project README
│
└── 📄 Utility Files
    ├── 📄 metrics_server.py                        # Standalone metrics server
    ├── 📄 parser.py                                 # Parser utilities
    ├── 📄 table_summarizer.py                      # Table summarization
    ├── 📄 verifier.py                               # Verification utilities
    └── 📄 test_metrics.py                           # Metrics testing
```

## 🆕 New Files Added for Lawyer-AI v9.0

### Core Integration Files
- ✅ `app/agents/lawyer_ai.py` - Lawyer-AI orchestrator (Planner→Executor→Verifier→Judge)
- ✅ `app/agents/planner.py` - Planning agent
- ✅ `app/agents/executor.py` - Execution agent (PDF extraction, data enrichment)
- ✅ `app/agents/verifier.py` - Verification agent (CII, TIT computation)
- ✅ `app/agents/judge.py` - Judge agent (hallucination metrics, FPP)
- ✅ `app/data/news_rss.py` - News RSS feed integration (PSX)
- ✅ `app/data/trading_view.py` - TradingView data (investing.com, psx.com.pk)
- ✅ `app/data/extractor.py` - Financial data extraction (OCF, GME)
- ✅ `app/core/feedback.py` - Human feedback mechanism
- ✅ `app/data/neo4j_integration.py` - Neo4j database integration

### Docker & Deployment Files
- ✅ `app/Dockerfile` - FastAPI container configuration
- ✅ `streamlit_app/Dockerfile` - Streamlit container configuration
- ✅ `docker-compose.yml` - Multi-container orchestration (lawyer_ai, streamlit, prometheus, grafana)
- ✅ `prometheus/prometheus.yml` - Prometheus scrape configuration
- ✅ `prometheus.yml` - Prometheus configuration (root)
- ✅ `grafana/LawyerAI_Dashboard.json` - Grafana dashboard JSON

### Updated Files
- ✅ `app/main.py` - Added Lawyer-AI endpoints, feedback endpoints, Neo4j integration
- ✅ `app/core/metrics.py` - Added Prometheus metrics for Lawyer-AI (CII, OCF, Risk, FPP, HS)
- ✅ `app/models/schemas.py` - Added Lawyer-AI request/response models, FeedbackRequest
- ✅ `app/settings.py` - Added Neo4j configuration
- ✅ `streamlit_app/dashboard.py` - Complete redesign with tabs (Core Metrics, Management Analysis, News Trends, Neo4j Graph, Full Analysis)
- ✅ `requirements.txt` - Added feedparser, neo4j, PyMuPDF, pdfplumber, beautifulsoup4

### Documentation Files
- ✅ `LAWYER_AI_INTEGRATION.md` - Complete integration guide
- ✅ `QUICK_START.md` - Quick start guide
- ✅ `PROMETHEUS_SETUP.md` - Prometheus setup guide
- ✅ `FOLDER_STRUCTURE.md` - This file

## 📂 Key Directories Explained

### `/app` - Main FastAPI Application
- **`main.py`**: FastAPI application with all endpoints
  - `POST /lawyer_ai/analyze` - PDF analysis endpoint
  - `POST /lawyer_ai/feedback` - Feedback submission
  - `GET /lawyer_ai/feedback/{analysis_id}` - Get feedback
  - `GET /neo4j/company/{company_name}` - Get company from Neo4j
- **`settings.py`**: Configuration and environment variables
- **`agents/`**: AI agent modules for orchestration
  - `planner.py` - Creates analysis plan
  - `executor.py` - Extracts PDF data, fetches external data
  - `verifier.py` - Validates and computes CII, TIT
  - `judge.py` - Finalizes with hallucination metrics, FPP
  - `lawyer_ai.py` - Main orchestrator
- **`core/`**: Core functionality
  - `logger.py` - Logging configuration
  - `metrics.py` - Prometheus metrics
  - `feedback.py` - Human feedback storage
  - `middleware.py` - FastAPI middleware
- **`data/`**: Data processing modules
  - `extractor.py` - Financial metrics extraction
  - `neo4j_integration.py` - Neo4j graph database
  - `news_rss.py` - PSX news feed
  - `trading_view.py` - investing.com, psx.com.pk data
  - `youtube.py` - YouTube transcript extraction
- **`models/`**: Pydantic schemas for request/response validation
- **`evaluation/`**: Evaluation and testing metrics

### `/streamlit_app` - Streamlit Dashboard
- **`dashboard.py`**: Main dashboard with 5 tabs:
  - Tab 1: Core Metrics (all analysis sections)
  - Tab 2: Management Analysis (with confidence scores)
  - Tab 3: News Trend Analysis (web search with PSX fallback)
  - Tab 4: Neo4j Graph (graph visualization)
  - Tab 5: Full Analysis (complete JSON output)
- **`static/`**: Static assets (logos, images)
- **`Dockerfile`**: Streamlit container configuration

### `/tests` - Testing
- Unit tests for various components
- Integration tests

### `/feedback_data` - Feedback Storage
- Stores human feedback JSON files
- Created automatically when feedback is submitted
- Format: `{analysis_id}_feedback.json`

### `/prometheus` - Prometheus Configuration
- **`prometheus.yml`**: Scrape configuration for metrics collection
- Targets: `localhost:8001` (Prometheus metrics server)

### `/grafana` - Grafana Dashboards
- **`LawyerAI_Dashboard.json`**: Pre-configured dashboard for Lawyer-AI metrics
- Import via Grafana UI

## 🔗 API Endpoints Structure

### Lawyer-AI Endpoints
- `POST /lawyer_ai/analyze` - Main PDF analysis endpoint
  - Accepts: PDF file upload
  - Returns: Complete Lawyer-AI analysis JSON
- `POST /lawyer_ai/feedback` - Submit human feedback
  - Accepts: FeedbackRequest JSON
  - Returns: Success confirmation
- `GET /lawyer_ai/feedback/{analysis_id}` - Get feedback for analysis
  - Returns: Feedback data
- `GET /lawyer_ai/news` - Get news articles (if implemented)

### Neo4j Endpoints
- `GET /neo4j/company/{company_name}` - Get company from Neo4j
  - Returns: Company node data
- `GET /neo4j/companies` - Get all companies (if implemented)
- `POST /neo4j/generate_cypher` - Generate Cypher query (if implemented)

### Existing Endpoints
- `POST /analyze` - File-based analysis
- `POST /analyze_financial` - Financial data analysis
- `POST /analyze_text` - Text analysis
- `POST /analyze_youtube` - YouTube transcript analysis
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## 📊 Data Flow

```
User Uploads PDF
    ↓
Streamlit Dashboard (streamlit_app/dashboard.py)
    ↓
FastAPI Endpoint (app/main.py) - POST /lawyer_ai/analyze
    ↓
Lawyer-AI Orchestrator (app/agents/lawyer_ai.py)
    ↓
├── Planner Agent (app/agents/planner.py) - Creates plan
├── Executor Agent (app/agents/executor.py) - Extracts PDF, fetches external data
│   ├── PDF Extraction (PyMuPDF, pdfplumber)
│   ├── TradingView Data (app/data/trading_view.py) - investing.com, psx.com.pk
│   ├── News RSS (app/data/news_rss.py) - PSX news
│   └── Financial Extraction (app/data/extractor.py) - OCF, GME
├── Verifier Agent (app/agents/verifier.py) - Validates, computes CII, TIT
└── Judge Agent (app/agents/judge.py) - Finalizes with hallucination metrics, FPP
    ↓
Analysis Results
    ↓
├── Neo4j Storage (app/data/neo4j_integration.py)
├── Prometheus Metrics (app/core/metrics.py) - Port 8001
└── Response to User (JSON)
```

## 🔧 Configuration Files

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
PROJECT_NAME=AFIW-ZulfiQode
```

### Docker Compose Services
```yaml
services:
  lawyer_ai:      # FastAPI backend (ports 8000, 8001)
  streamlit:      # Streamlit dashboard (port 8501)
  prometheus:     # Metrics collection (port 9090)
  grafana:        # Visualization (port 3000)
```

### Dependencies (requirements.txt)
- **FastAPI, Uvicorn** - Web framework
- **OpenAI** - AI models
- **Neo4j** - Graph database
- **Feedparser** - RSS feeds
- **Streamlit** - Dashboard
- **Prometheus Client** - Metrics
- **LangChain, LangGraph** - Agent framework
- **PyMuPDF (fitz)** - PDF text extraction
- **pdfplumber** - PDF table extraction
- **BeautifulSoup4** - Web scraping
- **Plotly** - Graph visualization
- **Pandas** - Data manipulation
- And more...

## 📝 File Descriptions

### Core Application Files

**`app/main.py`**
- FastAPI application
- All API endpoints
- CORS middleware
- Prometheus server startup (port 8001)
- Lawyer-AI analysis endpoint
- Feedback endpoints
- Neo4j integration

**`app/agents/lawyer_ai.py`**
- Lawyer-AI orchestrator
- Coordinates: Planner → Executor → Verifier → Judge
- Produces Lawyer-AI v9.0 JSON schema
- Integrates Neo4j and Prometheus

**`app/agents/planner.py`**
- Creates analysis plan
- Returns list of tasks

**`app/agents/executor.py`**
- Extracts text and numeric data from PDF
- Fetches TradingView data (investing.com, psx.com.pk)
- Fetches PSX news
- Extracts financial metrics (OCF, GME)

**`app/agents/verifier.py`**
- Validates raw data
- Computes CII (Composite Integrity Index)
- Computes TIT (Temporal Integrity Trend)
- Ensures data consistency

**`app/agents/judge.py`**
- Finalizes analysis
- Computes hallucination metrics (bias, variance, HS)
- Computes FPP (Future Performance Perspective)
- Integrates human feedback

**`app/core/metrics.py`**
- Prometheus metrics definitions
- Lawyer-AI specific metrics:
  - `lawyer_ai_composite_integrity_index`
  - `lawyer_ai_operational_cash_flow_confidence`
  - `lawyer_ai_risk_confidence`
  - `lawyer_ai_future_performance_confidence`
  - `lawyer_ai_hallucination_score`
- Metrics server startup

**`app/data/neo4j_integration.py`**
- Neo4j database connection
- Company node creation/update
- Stores: tone, ethics, risk, CII, TIT, OCF, GME, FPP, HS

**`app/data/news_rss.py`**
- PSX news feed fetching
- News article processing
- Company-specific filtering

**`app/data/trading_view.py`**
- TradingView data fetching
- Sources: investing.com, psx.com.pk
- RSI(14) and MA-200 data

**`app/data/extractor.py`**
- Financial metrics extraction
- OCF (Operational Cash Flow)
- GME (Gross Margin Effect)

**`app/core/feedback.py`**
- Human feedback storage
- Feedback aggregation
- Feedback retrieval

**`streamlit_app/dashboard.py`**
- Streamlit web interface
- 5 tabs:
  1. Core Metrics - All analysis sections
  2. Management Analysis - Management performance with confidence scores
  3. News Trend Analysis - Web search with PSX fallback
  4. Neo4j Graph - Graph visualization
  5. Full Analysis - Complete JSON output
- Company feedback in all explanations
- Human feedback submission form

## 🚀 Quick Navigation

### To run the application:

**Option 1: Docker Compose (Recommended)**
```bash
docker-compose up -d
```
- FastAPI: http://localhost:8000
- Streamlit: http://localhost:8501
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

**Option 2: Manual**
```bash
# Backend
python -m uvicorn app.main:app --reload

# Dashboard
streamlit run streamlit_app/dashboard.py
```

### To add new features:
- **New Agent**: Add to `app/agents/`
- **New Data Source**: Add to `app/data/`
- **New Endpoint**: Add to `app/main.py`
- **New Schema**: Add to `app/models/schemas.py`
- **New Dashboard Tab**: Add to `streamlit_app/dashboard.py`

### To view documentation:
- **Integration Guide**: `LAWYER_AI_INTEGRATION.md`
- **Quick Start**: `QUICK_START.md`
- **Prometheus Setup**: `PROMETHEUS_SETUP.md`
- **Observability**: `OBSERVABILITY.md`
- **Folder Structure**: `FOLDER_STRUCTURE.md` (this file)

## 📌 Important Notes

1. **Virtual Environment**: `venv/` is not tracked in git
2. **Environment Variables**: `.env` file should not be committed
3. **Feedback Data**: `feedback_data/` is created automatically
4. **Cache Files**: `__pycache__/` directories are auto-generated
5. **Documentation**: All `.md` files are in the root directory
6. **Docker Volumes**: `grafana-data/` is a Docker volume for Grafana persistence
7. **Prometheus Config**: Both `prometheus.yml` (root) and `prometheus/prometheus.yml` exist

## 🔍 Finding Specific Functionality

- **Lawyer-AI Analysis**: `app/agents/lawyer_ai.py`
- **Agent Orchestration**: `app/agents/` (planner, executor, verifier, judge)
- **Neo4j Integration**: `app/data/neo4j_integration.py`
- **News RSS**: `app/data/news_rss.py`
- **TradingView Data**: `app/data/trading_view.py`
- **Financial Extraction**: `app/data/extractor.py`
- **Human Feedback**: `app/core/feedback.py`
- **Prometheus Metrics**: `app/core/metrics.py`
- **API Endpoints**: `app/main.py`
- **Dashboard**: `streamlit_app/dashboard.py`
- **Schemas**: `app/models/schemas.py`
- **Docker Config**: `docker-compose.yml`, `app/Dockerfile`, `streamlit_app/Dockerfile`
- **Grafana Dashboard**: `grafana/LawyerAI_Dashboard.json`

## 📊 Dashboard Tabs Structure

### Tab 1: Core Metrics
- Core Evaluation Metrics
- Technical Analysis
- Business Cycle Context
- Operational Metrics
- Composite Integrity Index (CII)
- Temporal Integrity Trend (TIT)
- Future Performance Perspective (FPP)
- Hallucination Metrics
- PSX News Feed Analysis
- Human Feedback
- Analysis Conclusion

### Tab 2: Management Analysis
- Management metrics table (8 dimensions)
- Confidence scores visualization
- Overall Management Confidence metric
- Company feedback

### Tab 3: News Trend Analysis
- Web search interface
- News trend timeline chart
- Sentiment analysis pie chart
- PSX news fallback

### Tab 4: Neo4j Graph
- Network graph visualization
- Company relationship graph
- Metrics bar chart
- Analysis data fallback

### Tab 5: Full Analysis
- Complete JSON output
- Metadata view

---

**Last Updated**: Lawyer-AI v9.0
**Total Files**: ~40+ Python files
**Key Integrations**: Lawyer-AI, Neo4j, News RSS (PSX), TradingView (investing.com, psx.com.pk), Human Feedback, Prometheus, Grafana
**Docker Services**: 4 containers (lawyer_ai, streamlit, prometheus, grafana)
