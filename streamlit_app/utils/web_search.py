"""
Web Search Helper
Fetches web results using Brave Search API (with DuckDuckGo fallback)
"""
import requests
import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def fetch_web_results(company: str, query: str) -> str:
    """
    Return 5-10 clean snippets from the public web for the given company + query.
    Tries Brave Search (free API) first, falls back to DuckDuckGo.
    
    Args:
        company: Company name to search for
        query: Search query string
        
    Returns:
        Formatted string of web search snippets
    """
    search = f"{company} {query}".strip()
    headers = {"Accept": "application/json"}

    # 1️⃣ Brave Search (you can get a free key at https://api.search.brave.com)
    key = os.getenv("BRAVE_API_KEY")
    if key:
        try:
            r = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={**headers, "X-Subscription-Token": key},
                params={"q": search, "count": 8},
                timeout=10,
            )
            r.raise_for_status()
            data = r.json().get("web", {}).get("results", [])
            snippets = [f"- {d['title']}: {d['description']}" for d in data[:8]]
            if snippets:
                logger.info(f"✅ Fetched {len(snippets)} snippets from Brave Search for {company}")
                return "\n".join(snippets)
        except Exception as e:
            logger.warning(f"Brave search failed: {e}")

    # 2️⃣ Fallback: DuckDuckGo JSON (no key required)
    try:
        r = requests.get(
            f"https://api.duckduckgo.com/?q={search}&format=json&no_html=1",
            timeout=10,
        )
        r.raise_for_status()
        data = r.json().get("RelatedTopics", [])
        snippets = [
            f"- {t.get('Text')}" for t in data if isinstance(t, dict) and t.get("Text")
        ]
        result = "\n".join(snippets[:8]) or f"[No relevant web data found for '{search}']"
        logger.info(f"✅ Fetched {len(snippets)} snippets from DuckDuckGo for {company}")
        return result
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"[⚠️ Web search failed: {e}]"


def fetch_web_results_list(company_name: str, query: str) -> List[Dict[str, str]]:
    """
    Fetch web results as a list of dictionaries.
    
    Args:
        company_name: Company name to search for
        query: Search query string
        
    Returns:
        List of dictionaries with title, text, and url
    """
    search = f"{company_name} {query}".strip()
    headers = {"Accept": "application/json"}

    # 1️⃣ Brave Search (if API key available)
    key = os.getenv("BRAVE_API_KEY")
    if key:
        try:
            r = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={**headers, "X-Subscription-Token": key},
                params={"q": search, "count": 8},
                timeout=10,
            )
            r.raise_for_status()
            data = r.json().get("web", {}).get("results", [])
            results = [
                {
                    "title": d.get("title", ""),
                    "text": d.get("description", ""),
                    "url": d.get("url", "")
                }
                for d in data[:8]
            ]
            if results:
                logger.info(f"✅ Fetched {len(results)} results from Brave Search for {company_name}")
                return results
        except Exception as e:
            logger.warning(f"Brave search failed: {e}")

    # 2️⃣ Fallback: DuckDuckGo
    try:
        r = requests.get(
            f"https://api.duckduckgo.com/?q={search}&format=json&no_html=1",
            timeout=10,
        )
        r.raise_for_status()
        data = r.json().get("RelatedTopics", [])
        results = []
        for item in data[:8]:
            if isinstance(item, dict):
                text = item.get("Text", "")
                url = item.get("FirstURL", "")
                title = text.split(" - ")[0] if " - " in text else text[:50]
                
                if text:
                    results.append({
                        "title": title,
                        "text": text,
                        "url": url
                    })
        
        logger.info(f"✅ Fetched {len(results)} results from DuckDuckGo for {company_name}")
        return results
        
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return []
