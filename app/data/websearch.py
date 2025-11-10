"""
Lawyer-AI Web Intelligence Search Tool
Improved version with multiple search strategies and RSS feed support
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from app.core.logger import get_logger
from app.settings import TRUSTED_DOMAINS, MAX_WEB_RESULTS, REQUEST_TIMEOUT
import feedparser
import time
import re
from urllib.parse import quote, urljoin

logger = get_logger(__name__)

# Headers for requests
HEADERS = {
    "User-Agent": "AFIW-LawyerAI/1.0 (+compliance)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}


def _domain_ok(url: str) -> bool:
    """Check if URL is from a trusted domain."""
    return any(domain in url for domain in TRUSTED_DOMAINS)


class WebSearch:
    """
    Lawyer-AI Web Intelligence Search Tool
    Performs searches across financial domains using multiple strategies:
    1. RSS feeds from financial sites
    2. Direct site search
    3. Google Custom Search (if API key available)
    """
    
    def __init__(self, max_results: int = None):
        """
        Initialize WebSearch
        
        Args:
            max_results: Maximum number of results to return (default: from settings)
        """
        self.max_results = max_results or MAX_WEB_RESULTS
        self.financial_sites = {
            "PSX": "https://www.psx.com.pk",
            "SECP": "https://www.secp.gov.pk",
            "Profit": "https://profit.pakistantoday.com.pk"
        }
        self.rss_feeds = {
            "PSX": "https://www.psx.com.pk/rss/news",
            "Profit": "https://profit.pakistantoday.com.pk/rss"
        }
    
    def search(self, query: str) -> List[Dict]:
        """
        Performs a multi-strategy search across financial domains.
        
        Args:
            query: Search query string
            
        Returns:
            List of search results with title, url, and source
        """
        results = []
        
        # Strategy 1: RSS Feed Search
        try:
            rss_results = self._search_rss_feeds(query)
            results.extend(rss_results)
            logger.info(f"RSS search found {len(rss_results)} results")
        except Exception as e:
            logger.warning(f"RSS search failed: {e}")
        
        # Strategy 2: Direct Site Search
        try:
            site_results = self._search_direct_sites(query)
            results.extend(site_results)
            logger.info(f"Direct site search found {len(site_results)} results")
        except Exception as e:
            logger.warning(f"Direct site search failed: {e}")
        
        # Strategy 3: DuckDuckGo Search (fallback)
        if len(results) < self.max_results:
            try:
                ddg_results = self._search_duckduckgo(query)
                results.extend(ddg_results)
                logger.info(f"DuckDuckGo search found {len(ddg_results)} results")
            except Exception as e:
                logger.warning(f"DuckDuckGo search failed: {e}")
        
        # Remove duplicates and limit results
        unique_results = self._deduplicate_results(results)
        final_results = unique_results[:self.max_results]
        
        logger.info(f"✅ Web search completed: {len(final_results)} unique results for '{query}'")
        return final_results
    
    def _search_rss_feeds(self, query: str) -> List[Dict]:
        """Search RSS feeds from financial sites."""
        results = []
        query_lower = query.lower()
        
        for site_name, rss_url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries:
                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    summary = entry.get("summary", entry.get("description", ""))
                    published = entry.get("published", "")
                    
                    # Check if query matches
                    if (query_lower in title.lower() or 
                        query_lower in summary.lower()):
                        results.append({
                            "title": title,
                            "url": link,
                            "source": site_name,
                            "snippet": summary[:200] + "..." if len(summary) > 200 else summary,
                            "published": published
                        })
            except Exception as e:
                logger.warning(f"Failed to parse RSS feed {rss_url}: {e}")
                continue
        
        return results
    
    def _search_direct_sites(self, query: str) -> List[Dict]:
        """Search directly on financial sites."""
        results = []
        query_encoded = quote(query)
        
        # PSX News Search
        try:
            psx_url = f"https://www.psx.com.pk/news/search?q={query_encoded}"
            psx_results = self._scrape_site_search(psx_url, "PSX", query)
            results.extend(psx_results)
        except Exception as e:
            logger.warning(f"PSX direct search failed: {e}")
        
        # SECP Search
        try:
            secp_url = f"https://www.secp.gov.pk/search/?q={query_encoded}"
            secp_results = self._scrape_site_search(secp_url, "SECP", query)
            results.extend(secp_results)
        except Exception as e:
            logger.warning(f"SECP direct search failed: {e}")
        
        return results
    
    def _scrape_site_search(self, url: str, site_name: str, query: str) -> List[Dict]:
        """Scrape search results from a site."""
        results = []
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5"
            }
            
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            query_lower = query.lower()
            
            # Try multiple selectors for different sites
            selectors = [
                ("a", {"class": "news-title"}),
                ("a", {"class": "article-link"}),
                ("h2 a", {}),
                ("h3 a", {}),
                ("a", {"href": lambda x: x and ("news" in x.lower() or "article" in x.lower())})
            ]
            
            for tag, attrs in selectors:
                links = soup.find_all(tag, attrs)
                
                for link in links[:self.max_results]:
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    
                    if not title or not href:
                        continue
                    
                    # Make URL absolute
                    if href.startswith("/"):
                        href = urljoin(url, href)
                    elif not href.startswith("http"):
                        continue
                    
                    # Check relevance
                    if query_lower in title.lower():
                        results.append({
                            "title": title,
                            "url": href,
                            "source": site_name,
                            "snippet": ""
                        })
                
                if results:
                    break
        
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
        
        return results
    
    def _search_duckduckgo(self, query: str) -> List[Dict]:
        """Search using DuckDuckGo (fallback method)."""
        results = []
        
        try:
            # Build search query with site filters
            site_filters = "site:psx.com.pk OR site:secp.gov.pk OR site:profit.pakistantoday.com.pk"
            search_query = f"{query} {site_filters}"
            search_query_encoded = quote(search_query)
            
            url = f"https://html.duckduckgo.com/html/?q={search_query_encoded}"
            
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try multiple selectors for DuckDuckGo results
            selectors = [
                ("a", {"class": "result__a"}),
                ("a", {"class": "web-result__a"}),
                ("a", {"class": "result-link"}),
                ("h2 a", {}),
                ("a", {"href": lambda x: x and x.startswith("http")})
            ]
            
            for tag, attrs in selectors:
                links = soup.find_all(tag, attrs)
                
                for link in links[:self.max_results]:
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    
                    if not title or not href:
                        continue
                    
                    # Skip DuckDuckGo internal links
                    if "duckduckgo.com" in href:
                        continue
                    
                    results.append({
                        "title": title,
                        "url": href,
                        "source": self._extract_source(href),
                        "snippet": ""
                    })
                
                if results:
                    break
        
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
        
        return results
    
    def extract_text(self, url: str) -> str:
        """
        Extracts readable text from a given web page with improved extraction.
        
        Args:
            url: URL to extract text from
            
        Returns:
            Extracted text content
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5"
            }
            
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if "application/pdf" in content_type:
                return f"[PDF file at {url} - cannot extract text directly]"
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Try to find main content area
            main_content = None
            content_selectors = [
                ("article", {}),
                ("main", {}),
                ("div", {"class": "content"}),
                ("div", {"class": "article-content"}),
                ("div", {"id": "content"}),
                ("div", {"class": "post-content"})
            ]
            
            for tag, attrs in content_selectors:
                main_content = soup.find(tag, attrs)
                if main_content:
                    break
            
            # Extract text from main content or body
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                # Fallback to body
                body = soup.find("body")
                if body:
                    text = body.get_text(separator=' ', strip=True)
                else:
                    text = soup.get_text(separator=' ', strip=True)
            
            # Clean up text
            text = ' '.join(text.split())  # Remove extra whitespace
            
            if text and len(text) > 100:
                return text
            else:
                return f"[Insufficient text content at {url}]"
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout extracting text from {url}")
            return f"[Timeout error extracting {url}]"
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error extracting text from {url}: {e}")
            return f"[Request error extracting {url}]: {e}"
        except Exception as e:
            logger.error(f"Failed to extract text from {url}: {e}")
            return f"[Error extracting {url}]: {e}"
    
    def _extract_source(self, url: str) -> str:
        """
        Extract source domain from URL.
        
        Args:
            url: URL string
            
        Returns:
            Source domain name
        """
        try:
            url_lower = url.lower()
            if "psx.com.pk" in url_lower:
                return "PSX"
            elif "secp.gov.pk" in url_lower:
                return "SECP"
            elif "profit.pakistantoday.com.pk" in url_lower or "pakistantoday.com.pk" in url_lower:
                return "Profit Pakistan Today"
            elif "brecorder.com" in url_lower:
                return "Business Recorder"
            elif "dawn.com" in url_lower:
                return "Dawn"
            else:
                # Extract domain name
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc.replace("www.", "")
                return domain.split(".")[0].title() if domain else "Unknown"
        except:
            return "Unknown"
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on URL."""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
