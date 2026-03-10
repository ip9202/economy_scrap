"""GDELT BigQuery client for historical Korean financial news collection."""

from datetime import date, datetime

import pandas as pd
from google.cloud import bigquery
from loguru import logger


class GdeltClient:
    """Collects economic news from GDELT BigQuery public dataset.

    GDELT (Global Database of Events, Language, and Tone) provides
    historical news sentiment data with tone/sentiment analysis.

    Attributes:
        project_id: Google Cloud project ID (optional for public dataset)
        use_public: Whether to use public BigQuery dataset
    """

    def __init__(self, project_id: str | None = None, use_public: bool = True) -> None:
        """Initialize the GdeltClient.

        Args:
            project_id: Google Cloud project ID (optional for public dataset access)
            use_public: Use public BigQuery dataset (default: True)
        """
        self.project_id = project_id
        self.use_public = use_public
        self.client: bigquery.Client | None = None

        try:
            if project_id:
                # Use authenticated client with specific project
                self.client = bigquery.Client(project=project_id)
                logger.info(f"BigQuery client initialized for project: {project_id}")
            elif use_public:
                # Use anonymous client for public dataset
                self.client = bigquery.Client()
                logger.info("BigQuery client initialized for public dataset access")
            else:
                logger.warning(
                    "No project_id specified and use_public=False - client not initialized"
                )
        except Exception as e:
            logger.warning(f"BigQuery client initialization failed: {e}")
            logger.info("GDELT client will be disabled - falling back to RSS-only mode")
            self.client = None

    def collect(
        self,
        queries: list[str],
        start_date: date,
        end_date: date,
        max_items: int = 1000,
    ) -> pd.DataFrame:
        """Collect news articles from GDELT BigQuery dataset.

        Args:
            queries: List of search queries (Korean keywords)
            start_date: Start date for filtering articles
            end_date: End date for filtering articles
            max_items: Maximum items to collect (default: 1000)

        Returns:
            DataFrame with columns: query, published_at, title, summary, google_url

        Raises:
            ValueError: If client is not initialized or query fails
        """
        if self.client is None:
            raise ValueError(
                "BigQuery client not initialized. Set GDELT_PROJECT_ID or enable GDELT_USE_PUBLIC."
            )

        logger.info(
            "Starting GDELT news collection",
            extra={
                "queries": queries,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "max_items": max_items,
            },
        )

        # Build BigQuery SQL query
        query = self._build_query(queries, start_date, end_date, max_items)

        try:
            # Execute query
            logger.debug("Executing BigQuery query...")
            query_job = self.client.query(query)
            results = query_job.result()

            # Convert to DataFrame
            df = results.to_dataframe()

            if df.empty:
                logger.warning("No articles found from GDELT for the specified date range")
                return pd.DataFrame(
                    columns=["query", "published_at", "title", "summary", "google_url"]
                )

            # Rename and format columns to match news_collector schema
            df = self._format_columns(df)

            # Ensure required columns exist
            required_cols = ["query", "published_at", "title", "summary", "google_url"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ""

            # Select only required columns
            df = df[required_cols]

            # Deduplicate
            df = self._deduplicate(df)

            logger.info(f"Collected {len(df)} unique articles from GDELT")
            return df

        except Exception as e:
            logger.error(f"GDELT query failed: {e}")
            raise ValueError(f"GDELT query failed: {e}") from e

    def _build_query(
        self,
        queries: list[str],
        start_date: date,
        end_date: date,
        max_items: int,
    ) -> str:
        """Build BigQuery SQL query for GDELT data.

        Args:
            queries: List of search queries
            start_date: Start date
            end_date: End date
            max_items: Maximum results

        Returns:
            SQL query string
        """
        # GDELT table: gdelt-bq.gdeltv2.gkg_partitioned
        # Date format: YYYYMMDDHHMMSS
        start_date_str = start_date.strftime("%Y%m%d") + "000000"
        end_date_str = end_date.strftime("%Y%m%d") + "235959"

        # Build keyword matching conditions
        # GDELT stores themes and locations in separate arrays, we search in common themes
        keyword_conditions = []
        for query in queries:
            # Search for Korean language news containing our keywords
            # GDELT's Themes field contains both English and transliterated keywords
            keyword_conditions.append(f"LOWER(Themes) LIKE '%{query.lower()}%'")

        keyword_filter = " OR ".join(keyword_conditions)

        # GDELT GKG table schema:
        # - DATE: Integer date in YYYYMMDDHHMMSS format
        # - DocumentIdentifier: URL
        # - Themes: Semicolon-separated list of themes
        # - Locations: Semicolon-separated list of locations
        # - V2Locations: Enhanced location data with country codes
        # - Tone: Sentiment score (-100 to +100)
        # - To filter for Korean content, we use V2Locations containing 'KR' (Korea country code)

        sql = f"""
        SELECT
            DATE,
            DocumentIdentifier AS url,
            Themes,
            Locations,
            V2Locations,
            Persons,
            Organizations,
            V2Tone
        FROM
            `gdelt-bq.gdeltv2.gkg_partitioned`
        WHERE
            DATE >= {start_date_str}
            AND DATE <= {end_date_str}
            AND ({keyword_filter})
            AND (V2Locations LIKE '%KR#%' OR V2Locations LIKE '%Korea%')
        ORDER BY
            DATE DESC
        LIMIT
            {max_items}
        """

        return sql

    def _format_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format GDELT columns to match news_collector schema.

        GDELT data needs to be mapped to:
        - query: The search query used (extracted from themes)
        - published_at: Publication date
        - title: Article title (constructed from available data)
        - summary: Article summary/tones
        - google_url: Article URL

        Args:
            df: Raw GDELT DataFrame

        Returns:
            Formatted DataFrame matching news_collector schema
        """
        # Extract published_at from DATE column (uppercase in GDELT)
        if "DATE" in df.columns:
            df["published_at"] = pd.to_datetime(
                df["DATE"].astype(str), format="%Y%m%d%H%M%S", errors="coerce"
            )
        elif "date" in df.columns:
            df["published_at"] = pd.to_datetime(
                df["date"].astype(str), format="%Y%m%d%H%M%S", errors="coerce"
            )
        else:
            df["published_at"] = datetime.now()

        # Construct title from available data (THEMES is uppercase in GDELT)
        if "THEMES" in df.columns:
            df["title"] = df["THEMES"].apply(
                lambda x: str(x)[:200] if pd.notna(x) else "Korean Economic News"
            )
        elif "themes" in df.columns:
            df["title"] = df["themes"].apply(
                lambda x: str(x)[:200] if pd.notna(x) else "Korean Economic News"
            )
        else:
            df["title"] = "Korean Economic News"

        # Construct summary with tone/sentiment data (V2Tone in GDELT v2)
        if "V2Tone" in df.columns:
            df["summary"] = df.apply(lambda row: self._create_summary(row), axis=1)
        elif "Tone" in df.columns:
            df["summary"] = df.apply(lambda row: self._create_summary(row), axis=1)
        elif "tone" in df.columns:
            df["summary"] = df.apply(lambda row: self._create_summary(row), axis=1)
        else:
            df["summary"] = "Economic news article from GDELT database"

        # URL (url is lowercase from the query alias)
        df["google_url"] = df.get("url", "")

        # Query (extract from first matching theme)
        df["query"] = "한국은행 기준금리"  # Default query

        return df

    def _create_summary(self, row: pd.Series) -> str:
        """Create summary from GDELT tone and sentiment data.

        GDELT Tone format:
        - Tone: Float from -100 (very negative) to +100 (very positive)
        - PositiveScore, NegativeScore: Component scores
        - Polarity: Strength of sentiment

        Args:
            row: DataFrame row

        Returns:
            Formatted summary string
        """
        parts = []

        # Check for Tone column (V2Tone in GDELT v2, fallback to Tone/tone)
        tone_col = "V2Tone" if "V2Tone" in row.index else ("Tone" if "Tone" in row.index else "tone")
        positive_col = (
            "V2PositiveScore"
            if "V2PositiveScore" in row.index
            else ("PositiveScore" if "PositiveScore" in row.index else "positive_score")
        )
        negative_col = (
            "V2NegativeScore"
            if "V2NegativeScore" in row.index
            else ("NegativeScore" if "NegativeScore" in row.index else "negative_score")
        )
        persons_col = "Persons" if "Persons" in row.index else "persons"
        orgs_col = "Organizations" if "Organizations" in row.index else "organizations"

        if tone_col in row.index and pd.notna(row[tone_col]):
            tone_val = float(row[tone_col])
            stance = "positive" if tone_val > 0 else "negative" if tone_val < 0 else "neutral"
            parts.append(f"Sentiment: {stance} (tone: {tone_val:.2f})")

        if positive_col in row.index and pd.notna(row[positive_col]):
            parts.append(f"Positive: {row[positive_col]:.2f}")

        if negative_col in row.index and pd.notna(row[negative_col]):
            parts.append(f"Negative: {row[negative_col]:.2f}")

        if persons_col in row.index and pd.notna(row[persons_col]) and str(row[persons_col]) != "nan":
            persons = str(row[persons_col])[:100]
            parts.append(f"Persons: {persons}")

        if orgs_col in row.index and pd.notna(row[orgs_col]) and str(row[orgs_col]) != "nan":
            orgs = str(row[orgs_col])[:100]
            parts.append(f"Organizations: {orgs}")

        return " | ".join(parts) if parts else "Korean economic news"

    def _deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate articles based on URL and (title, date).

        Args:
            df: DataFrame with potential duplicates

        Returns:
            Deduplicated DataFrame
        """
        original_count = len(df)

        # Primary deduplication by google_url
        df = df.drop_duplicates(subset=["google_url"], keep="first")

        # Secondary deduplication by (title, published_at)
        df = df.drop_duplicates(subset=["title", "published_at"], keep="first")

        duplicates_removed = original_count - len(df)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate articles from GDELT")

        return df

    def is_available(self) -> bool:
        """Check if GDELT client is properly initialized.

        Returns:
            True if client is available, False otherwise
        """
        return self.client is not None
