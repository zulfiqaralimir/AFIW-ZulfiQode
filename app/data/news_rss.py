"""
News RSS Feed Integration
Fetches and processes news articles for financial analysis context
"""
import feedparser
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.core.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------
# 📰 NewsRSSFeed
# ---------------------------------------------------------
class NewsRSSFeed:
    """
    Fetches relevant business and finance news for a company
    using RSS feeds from Business Recorder, Dawn, Profit, etc.
    """
    
    def __init__(self):
        self.feeds = [
            "https://www.brecorder.com/rss.xml",
            "https://profit.pakistantoday.com.pk/feed/",
            "https://www.dawn.com/business/rss.xml"
        ]
    
    def fetch(self, company_name: str):
        """
        Fetch latest news for a company from RSS feeds.
        
        Args:
            company_name: Company name to search for
            
        Returns:
            List of relevant news articles
        """
        logger.info(f"📰 Fetching RSS news for {company_name}")
        all_news = []
        keywords = [kw.lower() for kw in company_name.split()]
        
        try:
            for url in self.feeds:
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:10]:
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    link = entry.get("link", "")
                    source = feed.feed.get("title", "Unknown Source")
                    
                    if any(k in title.lower() or k in summary.lower() for k in keywords):
                        all_news.append({
                            "title": title,
                            "source": source,
                            "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                            "link": link
                        })
            
            if not all_news:
                all_news.append({
                    "title": f"No recent articles found for {company_name}",
                    "source": "RSS",
                    "summary": "No company-specific items appeared in the latest financial feeds.",
                    "link": ""
                })
            
            return all_news
        
        except Exception as e:
            logger.error(f"RSS fetch failed: {e}")
            return [{
                "title": "News retrieval error",
                "source": "RSS",
                "summary": str(e),
                "link": ""
            }]
    
    # Backward compatibility methods
    def fetch_feed(self, feed_url: str) -> List[Dict]:
        """
        Fetch and parse a single RSS feed (backward compatibility).
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            List of news articles as dictionaries
        """
        try:
            feed = feedparser.parse(feed_url)
            
            articles = []
            for entry in feed.entries[:20]:  # Limit to 20 most recent
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                    "source": feed.feed.get("title", feed_url)
                }
                articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from {feed_url}")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to fetch feed {feed_url}: {str(e)}")
            return []
    
    def fetch_multiple_feeds(self, feed_urls: Optional[List[str]] = None) -> List[Dict]:
        """
        Fetch articles from multiple RSS feeds (backward compatibility).
        
        Args:
            feed_urls: List of RSS feed URLs (uses default if None)
            
        Returns:
            Combined list of news articles
        """
        if feed_urls is None:
            feed_urls = self.feeds
        
        all_articles = []
        for feed_url in feed_urls:
            articles = self.fetch_feed(feed_url)
            all_articles.extend(articles)
        
        # Sort by published date (most recent first)
        all_articles.sort(
            key=lambda x: self._parse_date(x.get("published", "")),
            reverse=True
        )
        
        logger.info(f"Fetched total {len(all_articles)} articles from {len(feed_urls)} feeds")
        return all_articles
    
    def filter_by_keywords(
        self,
        articles: List[Dict],
        keywords: List[str],
        company_name: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter articles by keywords and/or company name (backward compatibility).
        
        Args:
            articles: List of articles to filter
            keywords: List of keywords to search for
            company_name: Optional company name to filter by
            
        Returns:
            Filtered list of articles
        """
        if not keywords and not company_name:
            return articles
        
        filtered = []
        search_terms = keywords.copy()
        if company_name:
            search_terms.append(company_name.lower())
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            
            if any(term.lower() in text for term in search_terms):
                filtered.append(article)
        
        logger.info(f"Filtered {len(articles)} articles to {len(filtered)} matching keywords")
        return filtered
    
    def get_recent_news(
        self,
        keywords: Optional[List[str]] = None,
        company_name: Optional[str] = None,
        days: int = 30,
        max_articles: int = 10
    ) -> List[Dict]:
        """
        Get recent news articles matching criteria (backward compatibility).
        
        Args:
            keywords: Optional keywords to filter by
            company_name: Optional company name to filter by
            days: Number of days to look back (default: 30)
            max_articles: Maximum number of articles to return (default: 10)
            
        Returns:
            List of recent news articles
        """
        # Fetch all feeds
        all_articles = self.fetch_multiple_feeds()
        
        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_articles = [
            article for article in all_articles
            if self._parse_date(article.get("published", "")) >= cutoff_date
        ]
        
        # Filter by keywords/company
        if keywords or company_name:
            recent_articles = self.filter_by_keywords(
                recent_articles,
                keywords or [],
                company_name
            )
        
        # Limit results
        return recent_articles[:max_articles]
    
    def format_for_analysis(self, articles: List[Dict]) -> str:
        """
        Format articles as text for analysis context (backward compatibility).
        
        Args:
            articles: List of articles
            
        Returns:
            Formatted text string
        """
        if not articles:
            return "No recent news articles found."
        
        formatted = ["=== RECENT NEWS CONTEXT ===\n"]
        
        for i, article in enumerate(articles, 1):
            formatted.append(f"{i}. {article.get('title', 'No title')}")
            formatted.append(f"   Source: {article.get('source', 'Unknown')}")
            formatted.append(f"   Published: {article.get('published', 'Unknown date')}")
            formatted.append(f"   Summary: {article.get('summary', 'No summary')[:200]}...")
            formatted.append(f"   Link: {article.get('link', '')}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """
        Parse date string to datetime object (backward compatibility).
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Datetime object (defaults to epoch if parsing fails)
        """
        if not date_str:
            return datetime.fromtimestamp(0)
        
        try:
            # Try parsing common RSS date formats
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            try:
                # Try ISO format
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                # Default to epoch
                return datetime.fromtimestamp(0)


# Convenience function
def get_company_news(
    company_name: str,
    keywords: Optional[List[str]] = None,
    days: int = 30
) -> List[Dict]:
    """
    Get recent news for a specific company (backward compatibility).
    
    Args:
        company_name: Company name to search for
        keywords: Optional additional keywords
        days: Number of days to look back
        
    Returns:
        List of relevant news articles
    """
    feed = NewsRSSFeed()
    return feed.get_recent_news(
        keywords=keywords,
        company_name=company_name,
        days=days
    )


def fetch_latest_news(company: str, limit: int = 3) -> List[Dict]:
    """
    Fetch latest business news containing the company name (backward compatibility).
    Simplified function for ExecutorAgent compatibility.
    
    Args:
        company: Company name to search for
        limit: Maximum number of articles to return (default: 3)
        
    Returns:
        List of relevant news articles
    """
    feed = NewsRSSFeed()
    news = feed.fetch(company)
    return news[:limit]
