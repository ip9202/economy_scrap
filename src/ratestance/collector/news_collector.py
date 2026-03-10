"""News collection from Google News RSS feeds."""

from datetime import date, datetime
from typing import Any
from urllib.parse import quote

import feedparser
import pandas as pd
from loguru import logger


class NewsCollector:
    """Collects economic news from Google News RSS feeds.

    Attributes:
        user_agent: User agent string for HTTP requests
    """

    def __init__(self) -> None:
        """Initialize the NewsCollector."""
        self.user_agent = "RateStance/0.1.0"

    def collect(
        self,
        queries: list[str],
        start_date: date,
        end_date: date,
        max_items: int = 100,
    ) -> pd.DataFrame:
        """Collect news articles from Google News RSS feeds.

        Args:
            queries: List of search queries
            start_date: Start date for filtering articles
            end_date: End date for filtering articles
            max_items: Maximum items to collect per query

        Returns:
            DataFrame with columns: query, published_at, title, summary, google_url

        Raises:
            ValueError: If no articles are collected
        """
        logger.info(
            "Starting news collection",
            extra={
                "queries": queries,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "max_items": max_items,
            },
        )

        all_articles = []

        for query in queries:
            logger.info(f"Collecting articles for query: {query}")
            articles = self._fetch_rss(query, max_items)
            all_articles.extend(articles)

        if not all_articles:
            raise ValueError("No articles collected from RSS feeds")

        # Create DataFrame
        df = pd.DataFrame(all_articles)

        # Convert published_at to datetime
        df["published_at"] = pd.to_datetime(df["published_at"])

        # Filter by date range
        df = df[
            (df["published_at"].dt.date >= start_date) & (df["published_at"].dt.date <= end_date)
        ]

        # Deduplicate
        df = self._deduplicate(df)

        # Warn if low article count
        if len(df) < 10:
            logger.warning(
                f"Low article count detected: {len(df)} articles. "
                "Analysis may have higher variance."
            )

        logger.info(f"Collected {len(df)} unique articles after filtering and deduplication")

        return df

    def _fetch_rss(self, query: str, max_items: int) -> list[dict[str, Any]]:
        """Fetch articles from Google News RSS for a single query.

        Args:
            query: Search query string
            max_items: Maximum items to fetch

        Returns:
            List of article dictionaries
        """
        # Construct RSS URL
        encoded_query = quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"

        logger.debug(f"Fetching RSS from: {url}")

        # Parse RSS feed
        feed = feedparser.parse(url)

        if feed.bozo:
            logger.warning(f"RSS feed parsing warning for query '{query}': {feed.bozo_exception}")

        articles = []
        for entry in feed.entries[:max_items]:
            article = {
                "query": query,
                "published_at": self._parse_date(entry),
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "google_url": entry.get("link", ""),
            }
            articles.append(article)

        logger.debug(f"Fetched {len(articles)} articles for query: {query}")
        return articles

    def _parse_date(self, entry: feedparser.FeedParserDict) -> str:
        """Parse publication date from RSS entry.

        Args:
            entry: Feedparser entry

        Returns:
            ISO format date string or current datetime if not found
        """
        if "published" in entry:
            try:
                parsed = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
                return parsed.isoformat()
            except (ValueError, TypeError):
                pass

        # Fallback to current time
        logger.warning("Could not parse publication date, using current time")
        return datetime.now().isoformat()

    def _deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate articles based on google_url and (title, date).

        Args:
            df: DataFrame with potential duplicates

        Returns:
            Deduplicated DataFrame
        """
        original_count = len(df)

        # Primary deduplication by google_url
        df = df.drop_duplicates(subset=["google_url"], keep="first")

        # Normalize titles for better duplicate detection
        # Remove HTML tags, source suffixes like " - 경향신문", " - v.daum.net"
        df["title_normalized"] = df["title"].str.strip()
        # Remove common source suffixes
        df["title_normalized"] = df["title_normalized"].str.replace(
            r"\s*[-–—]\s*(v\.daum\.net|news\.google\.com|경향신문|연합뉴스|조선일보|중앙일보|동아일보|MBC|KBS|SBS|YTN|연합뉴스TV).*",
            "",
            regex=True,
        )
        # Remove HTML tags and extra whitespace
        df["title_normalized"] = df["title_normalized"].str.replace(r"<[^>]+>", "", regex=True)
        df["title_normalized"] = df["title_normalized"].str.replace(r"\s+", " ", regex=True).str.strip()

        # Secondary deduplication by (normalized_title, published_at)
        df = df.drop_duplicates(subset=["title_normalized", "published_at"], keep="first")

        # Drop the temporary column
        df = df.drop(columns=["title_normalized"])

        duplicates_removed = original_count - len(df)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate articles")

        return df
