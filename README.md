# AFIW-ZulfiQode

**Agentic Financial Intelligence Wrapper** - An AI-powered platform for ethical financial document analysis using GPT-4 and LangGraph.

## Features

- 📄 PDF and CSV document analysis
- 🤖 Multi-agent pipeline (Planner → Executor → Verifier)
- ⚖️ Ethical risk detection and bias auditing
- 📊 Streamlit dashboard with visual analytics
- 🚀 FastAPI backend with CORS support

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   Create a `.env` file:
   ```
   OPENAI_API_KEY=sk-your-key-here
   PROJECT_NAME=AFIW-ZulfiQode
   ```

3. **Run backend:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Run frontend (in another terminal):**
   ```bash
   streamlit run streamlit_app/dashboard.py
   ```

## Tech Stack

- **Backend:** FastAPI + LangGraph + OpenAI GPT-4
- **Frontend:** Streamlit
- **Data Processing:** pdfplumber, pandas
- **Visualization:** Plotly

## Project Structure

```
app/
├── agents/          # Multi-agent system (planner, executor, verifier)
├── core/            # Logging and utilities
├── data/            # PDF/CSV extractors
├── evaluation/      # Metrics and evaluation
├── models/          # Pydantic schemas
└── main.py          # FastAPI application

streamlit_app/
└── dashboard.py     # Streamlit UI

requirements.txt     # Python dependencies
```

## API Endpoints

- `POST /analyze` - Analyze PDF and/or CSV files
  - Request: multipart/form-data with `pdf_file` and/or `csv_file`
  - Response: Analysis summary, ethical flags, and latency metrics

## License

© 2025 Zulfiqar Ali Mir

