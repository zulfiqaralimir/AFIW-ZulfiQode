import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME", "AFIW-ZulfiQode")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# --- Hybrid GPT/Web Search Settings ---
USE_HYBRID = os.getenv("USE_HYBRID", "True").lower() == "true"  # Hybrid: GPT + local (PDF/Web)
USE_GPT_FOR_WEB = os.getenv("USE_GPT_FOR_WEB", "True").lower() == "true"  # GPT handles web retrieval/analysis
USE_LOCAL_WEB = os.getenv("USE_LOCAL_WEB", "True").lower() == "true"  # Local websearch fallback/augmentation

# GPT config (already in your project; keeping here for clarity)
CUSTOM_GPT_ID = os.getenv("CUSTOM_GPT_ID", "g-691028c2db1c8191bed9c2b8a4948f80")  # your custom GPT
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # or "gpt-4.1" (your org default)

# Domain scoping for local search
TRUSTED_DOMAINS = [
    "psx.com.pk",
    "secp.gov.pk",
    "dawn.com",
    "profit.pakistantoday.com.pk",
    "tribune.com.pk"
]

# Safety defaults
MAX_WEB_RESULTS = int(os.getenv("MAX_WEB_RESULTS", "5"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "12"))