"""API routes for RateStance Dashboard."""

from datetime import date
from pathlib import Path
from typing import Any
from uuid import UUID

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger

from ratestance.api.job_store import job_store
from ratestance.api.refresh_models import (
    JobCreateResponse,
    JobListResponse,
    JobStatus,
    RefreshRequest,
)
from ratestance.config import Settings
from ratestance.pipeline import Pipeline

router = APIRouter()

# Data directory path
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"

# Pipeline stages with progress ranges
PIPELINE_STAGES = {
    "news_collection": {"range": (0, 20), "message": "Collecting news from RSS feeds..."},
    "scoring": {"range": (20, 40), "message": "Scoring articles for stance..."},
    "aggregation": {"range": (40, 60), "message": "Aggregating to daily level..."},
    "rate_fetch": {"range": (60, 80), "message": "Fetching base rates from ECOS API..."},
    "event_detection": {"range": (80, 90), "message": "Detecting rate change events..."},
    "event_study": {"range": (90, 100), "message": "Performing event study analysis..."},
}


async def run_refresh_pipeline(
    job_id: UUID, config: Settings, start_date: date | None = None, end_date: date | None = None
) -> None:
    """Run the RateStance pipeline asynchronously with progress tracking.

    Args:
        job_id: Job identifier for status updates
        config: Pipeline configuration
        start_date: Optional start date for data collection
        end_date: Optional end date for data collection
    """
    logger.info(f"Starting refresh pipeline for job {job_id}")

    def progress_callback(stage: str, progress: int, message: str) -> None:
        """Update job progress during pipeline execution.

        Args:
            stage: Current pipeline stage
            progress: Progress percentage (0-100)
            message: Status message
        """
        job_store.update_job(
            job_id, status="running", progress=progress, stage=stage, message=message
        )
        logger.info(f"Job {job_id}: {stage} - {progress}% - {message}")

    try:
        # Update job status to running
        job_store.update_job(
            job_id, status="running", stage="initializing", message="Initializing pipeline..."
        )

        # Initialize pipeline with optional date range
        pipeline = RefreshPipeline(config, progress_callback, start_date, end_date)

        # Run pipeline with progress tracking
        await pipeline.run()

        # Mark as completed
        job_store.update_job(
            job_id,
            status="completed",
            progress=100,
            stage="completed",
            message="Data refresh completed successfully",
        )
        logger.success(f"Job {job_id} completed successfully")

    except Exception as e:
        # Mark as error
        job_store.update_job(
            job_id, status="error", stage="error", message=f"Pipeline failed: {str(e)}"
        )
        logger.error(f"Job {job_id} failed: {e}")


class RefreshPipeline(Pipeline):
    """Extended Pipeline with progress callback support.

    This class extends the base Pipeline to provide progress updates
    during execution for API job tracking.
    """

    def __init__(
        self,
        config: Settings,
        progress_callback: callable,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> None:
        """Initialize pipeline with progress callback.

        Args:
            config: Configuration settings
            progress_callback: Callback function for progress updates
            start_date: Optional start date for data collection
            end_date: Optional end date for data collection
        """
        super().__init__(config)
        self.progress_callback = progress_callback
        self.start_date = start_date
        self.end_date = end_date

    def _calculate_date_range(self) -> tuple[date, date]:
        """Calculate date range using provided dates or default behavior.

        Returns:
            Tuple of (start_date, end_date)
        """
        if self.start_date and self.end_date:
            logger.info(f"Using provided date range: {self.start_date} to {self.end_date}")
            return self.start_date, self.end_date
        else:
            # Use default behavior from parent class
            return super()._calculate_date_range()

    def _collect_news_with_fallback(
        self,
        news_collector: Any,
        gdelt_client: Any,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:
        """Collect news using GDELT for historical data and RSS for current data.

        Strategy:
        - For dates before GDELT_CUTOFF_DATE: Use GDELT (historical backfill)
        - For dates on/after GDELT_CUTOFF_DATE: Use Google News RSS (current data)
        - Combine both datasets seamlessly

        Args:
            news_collector: RSS news collector instance
            gdelt_client: GDELT BigQuery client (optional)
            start_date: Collection start date
            end_date: Collection end date

        Returns:
            Combined DataFrame with news articles from both sources
        """
        cutoff_date = self.config.gdelt_cutoff_date
        all_news = []

        # Collect historical data using GDELT (before cutoff)
        if gdelt_client and gdelt_client.is_available() and start_date < cutoff_date:
            historical_end = min(end_date, cutoff_date - pd.Timedelta(days=1))

            logger.info(f"Using GDELT for historical data: {start_date} to {historical_end}")
            try:
                gdelt_news = gdelt_client.collect(
                    queries=self.config.queries,
                    start_date=start_date,
                    end_date=historical_end,
                    max_items=self.config.max_items_per_query * 3,  # Get more from GDELT
                )
                all_news.append(gdelt_news)
                logger.info(f"GDELT collected {len(gdelt_news)} historical articles")
            except Exception as e:
                logger.warning(
                    f"GDELT collection failed: {e}. Falling back to RSS for historical data."
                )
                # Fallback to RSS if GDELT fails
                gdelt_news = news_collector.collect(
                    queries=self.config.queries,
                    start_date=start_date,
                    end_date=historical_end,
                    max_items=self.config.max_items_per_query,
                )
                all_news.append(gdelt_news)

        # Collect current data using RSS (on/after cutoff)
        rss_start = max(start_date, cutoff_date)
        if rss_start <= end_date:
            logger.info(f"Using RSS for current data: {rss_start} to {end_date}")
            rss_news = news_collector.collect(
                queries=self.config.queries,
                start_date=rss_start,
                end_date=end_date,
                max_items=self.config.max_items_per_query,
            )
            all_news.append(rss_news)
            logger.info(f"RSS collected {len(rss_news)} current articles")

        # Combine and deduplicate
        if all_news:
            combined = pd.concat(all_news, ignore_index=True)
            # Remove duplicates based on title and published_at
            combined = combined.drop_duplicates(subset=["title", "published_at"], keep="first")
            logger.info(f"Combined dataset: {len(combined)} unique articles")
            return combined
        else:
            raise ValueError("No news data collected from any source")

    async def run(self) -> dict[str, pd.DataFrame]:
        """Execute the full pipeline with progress tracking.

        Returns:
            Dictionary containing all pipeline outputs

        Raises:
            ValueError: If pipeline stage fails
        """
        from ratestance.aggregator import DailyAggregator
        from ratestance.analyzer import EventDetector, EventStudy
        from ratestance.collector import EcosClient, GdeltClient, NewsCollector
        from ratestance.scorer import StanceScorer
        from ratestance.visualizer import Visualizer

        logger.info("Starting RateStance pipeline with progress tracking")

        # Stage 1: Calculate date range
        date_range = self._calculate_date_range()
        logger.info(f"Date range: {date_range[0]} to {date_range[1]}")

        # Initialize components
        news_collector = NewsCollector()
        gdelt_client = None
        if self.config.enable_gdelt:
            gdelt_client = GdeltClient(
                project_id=self.config.gdelt_project_id, use_public=self.config.gdelt_use_public
            )
            if not gdelt_client.is_available():
                logger.warning("GDELT client initialization failed, using RSS-only mode")
                gdelt_client = None
        ecos_client = EcosClient(api_key=self.config.ecod_api_key)
        stance_scorer = StanceScorer(
            hawk_words=self.config.hawk_words, dove_words=self.config.dove_words
        )
        daily_aggregator = DailyAggregator()
        event_detector = EventDetector()
        event_study = EventStudy()
        visualizer = Visualizer()

        # Stage 1: Calculate date range
        date_range = self._calculate_date_range()
        logger.info(f"Date range: {date_range[0]} to {date_range[1]}")

        # Stage 2: Collect news (0-20%)
        stage = "news_collection"
        range_start, range_end = PIPELINE_STAGES[stage]["range"]
        self.progress_callback(stage, range_start, PIPELINE_STAGES[stage]["message"])

        news_raw = self._collect_news_with_fallback(
            news_collector, gdelt_client, date_range[0], date_range[1]
        )

        self._save_csv(news_raw, "data/news_raw.csv")
        self.progress_callback(stage, range_end, f"Collected {len(news_raw)} articles")

        # Stage 3: Score articles (20-40%)
        stage = "scoring"
        range_start, range_end = PIPELINE_STAGES[stage]["range"]
        self.progress_callback(stage, range_start, PIPELINE_STAGES[stage]["message"])
        news_scored = stance_scorer.score(news_raw)
        self._save_csv(news_scored, "data/news_scored.csv")
        self.progress_callback(stage, range_end, f"Scored {len(news_scored)} articles")

        # Stage 4: Aggregate daily (40-60%)
        stage = "aggregation"
        range_start, range_end = PIPELINE_STAGES[stage]["range"]
        self.progress_callback(stage, range_start, PIPELINE_STAGES[stage]["message"])
        news_daily = daily_aggregator.aggregate(news_scored)
        self._save_csv(news_daily, "data/news_daily.csv")
        self.progress_callback(stage, range_end, f"Aggregated {len(news_daily)} days")

        # Stage 5: Fetch rates (60-80%)
        stage = "rate_fetch"
        range_start, range_end = PIPELINE_STAGES[stage]["range"]
        self.progress_callback(stage, range_start, PIPELINE_STAGES[stage]["message"])
        rate_series = ecos_client.fetch_base_rates(start_date=date_range[0], end_date=date_range[1])
        self._save_csv(rate_series, "data/rate_series.csv")
        self.progress_callback(stage, range_end, f"Fetched {len(rate_series)} rate records")

        # Stage 6: Detect events (80-90%)
        stage = "event_detection"
        range_start, range_end = PIPELINE_STAGES[stage]["range"]
        self.progress_callback(stage, range_start, PIPELINE_STAGES[stage]["message"])
        events = event_detector.detect(rate_series)
        self._save_csv(events, "data/events.csv")
        self.progress_callback(stage, range_end, f"Detected {len(events)} events")

        # Stage 7: Event study (90-100%)
        stage = "event_study"
        range_start, range_end = PIPELINE_STAGES[stage]["range"]
        self.progress_callback(stage, range_start, PIPELINE_STAGES[stage]["message"])
        event_study_table = event_study.analyze(
            events=events,
            daily_stance=news_daily,
            window_days=self.config.event_window_days,
        )
        self._save_csv(event_study_table, "data/event_study_table.csv")
        self.progress_callback(stage, range_end, "Event study completed")

        # Stage 8: Generate visualizations (100%)
        logger.info("Generating visualizations")
        visualizer.plot_timeseries(news_daily, events)
        visualizer.plot_event_study(event_study_table)

        logger.success("Pipeline completed successfully")

        return {
            "news_raw": news_raw,
            "news_scored": news_scored,
            "news_daily": news_daily,
            "rate_series": rate_series,
            "events": events,
            "event_study_table": event_study_table,
        }


def read_csv_safe(filename: str) -> pd.DataFrame:
    """Safely read CSV file with error handling."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        logger.warning(f"Data file not found: {filepath}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(filepath)
        logger.info(f"Successfully read {filename}: {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error reading {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading data file: {filename}") from e


@router.get("/news-daily")
async def get_news_daily(start_date: str = None, end_date: str = None) -> list[dict]:
    """Get daily news sentiment data.

    Args:
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format

    Returns:
        Filtered daily news sentiment data
    """
    df = read_csv_safe("news_daily.csv")

    if df.empty:
        return []

    # Apply date filtering if provided
    if start_date or end_date:
        df = df.copy()
        df["date_parsed"] = pd.to_datetime(df["date"])
        if start_date:
            df = df[df["date_parsed"] >= start_date]
        if end_date:
            df = df[df["date_parsed"] <= end_date]
        df = df.drop(columns=["date_parsed"])

    # Ensure required columns exist
    required_cols = ["date", "stance_mean", "n_articles"]
    if not all(col in df.columns for col in required_cols):
        logger.error("Missing required columns in news_daily.csv")
        raise HTTPException(status_code=500, detail="Data file missing required columns")

    # Convert to list of dicts
    result = df[required_cols].to_dict(orient="records")

    # Convert date to string and handle NaN
    for row in result:
        row["date"] = str(row["date"])
        if pd.isna(row.get("stance_mean")):
            row["stance_mean"] = 0.0
        if pd.isna(row.get("n_articles")):
            row["n_articles"] = 0

    return result


@router.get("/rate-series")
async def get_rate_series(start_date: str = None, end_date: str = None) -> list[dict]:
    """Get interest rate time series data.

    Args:
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format

    Returns:
        Filtered rate series data
    """
    df = read_csv_safe("rate_series.csv")

    if df.empty:
        return []

    # Apply date filtering if provided
    if start_date or end_date:
        df = df.copy()
        df["date_parsed"] = pd.to_datetime(df["date"])
        if start_date:
            df = df[df["date_parsed"] >= start_date]
        if end_date:
            df = df[df["date_parsed"] <= end_date]
        df = df.drop(columns=["date_parsed"])

    required_cols = ["date", "value", "unit"]
    if not all(col in df.columns for col in required_cols):
        logger.error("Missing required columns in rate_series.csv")
        raise HTTPException(status_code=500, detail="Data file missing required columns")

    result = df[required_cols].to_dict(orient="records")

    for row in result:
        row["date"] = str(row["date"])
        if pd.isna(row.get("value")):
            row["value"] = 0.0
        row["unit"] = str(row.get("unit", "%"))

    return result


@router.get("/events")
async def get_events(start_date: str = None, end_date: str = None) -> list[dict]:
    """Get interest rate change events.

    Args:
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format

    Returns:
        Filtered events data
    """
    df = read_csv_safe("events.csv")

    if df.empty:
        return []

    # Apply date filtering if provided
    if start_date or end_date:
        df = df.copy()
        df["date_parsed"] = pd.to_datetime(df["date"])
        if start_date:
            df = df[df["date_parsed"] >= start_date]
        if end_date:
            df = df[df["date_parsed"] <= end_date]
        df = df.drop(columns=["date_parsed"])

    result = df.to_dict(orient="records")

    for row in result:
        row["date"] = str(row["date"])
        row["event_type"] = str(row.get("event_type", "hold"))
        # Construct description from available data
        event_type_label = {"raise": "금리 인상", "cut": "금리 인하", "hold": "금리 유지"}.get(
            row["event_type"], row["event_type"]
        )
        row["description"] = f"{event_type_label} ({row['date']})"

    return result


@router.get("/event-study")
async def get_event_study(start_date: str = None, end_date: str = None) -> list[dict]:
    """Get event study analysis data.

    Args:
        start_date: Optional start date in YYYY-MM-DD format (filters by event_date)
        end_date: Optional end date in YYYY-MM-DD format (filters by event_date)

    Returns:
        Filtered event study data
    """
    df = read_csv_safe("event_study_table.csv")

    if df.empty:
        return []

    # Apply date filtering if provided (filter by event_date)
    if start_date or end_date:
        df = df.copy()
        df["event_date_parsed"] = pd.to_datetime(df["event_date"])
        if start_date:
            df = df[df["event_date_parsed"] >= start_date]
        if end_date:
            df = df[df["event_date_parsed"] <= end_date]
        df = df.drop(columns=["event_date_parsed"])

    # Expected columns: event_date, event_type, day_offset, stance_mean, stance_std (optional)
    required_cols = ["event_date", "event_type", "day_offset", "stance_mean"]
    if not all(col in df.columns for col in required_cols):
        logger.error("Missing required columns in event_study_table.csv")
        raise HTTPException(status_code=500, detail="Data file missing required columns")

    # Filter out rows where stance_mean is empty/NaN (no news data available for that period)
    df_filtered = df[df["stance_mean"].notna() & (df["stance_mean"] != "")].copy()

    result = df_filtered.to_dict(orient="records")

    for row in result:
        row["event_date"] = str(row["event_date"])
        row["event_type"] = str(row.get("event_type", "hold"))
        row["day_offset"] = int(row.get("day_offset", 0))
        if pd.isna(row.get("stance_mean")):
            row["stance_mean"] = 0.0
        else:
            row["stance_mean"] = float(row["stance_mean"])

        # Include std if available
        if "stance_std" in row and not pd.isna(row.get("stance_std")):
            row["stance_std"] = float(row["stance_std"])

    return result


@router.get("/statistics")
async def get_statistics(start_date: str = None, end_date: str = None) -> dict:
    """Get summary statistics for optional date range.

    Note: event_count and latest_event are always calculated from ALL data (not filtered),
          while total_articles and avg_stance are filtered by the date range.

    Args:
        start_date: Optional start date in YYYY-MM-DD format (only affects articles/stance)
        end_date: Optional end date in YYYY-MM-DD format (only affects articles/stance)

    Returns:
        Statistics with articles/stance for date range, events for all data
    """
    news_daily_df = read_csv_safe("news_daily.csv")
    events_df_all = read_csv_safe("events.csv")

    total_articles = 0
    avg_stance = 0.0
    event_count = 0
    latest_event = "No events"

    # Calculate event statistics from ALL data (no date filtering)
    if not events_df_all.empty:
        # Filter out hold events (no rate change) - only count actual rate changes
        actual_events_df = events_df_all[events_df_all["diff"] != 0].copy()
        event_count = len(actual_events_df)

        # Get the latest actual rate change event
        if not actual_events_df.empty:
            latest = actual_events_df.iloc[0]
            event_type = latest.get("event_type", "hold")
            event_date = latest.get("date", "")
            latest_event = f"{event_type} ({event_date})"
        else:
            # Fallback to first event if no rate changes
            latest = events_df_all.iloc[0]
            event_type = latest.get("event_type", "hold")
            event_date = latest.get("date", "")
            latest_event = f"{event_type} ({event_date})"

    # Calculate article/stance statistics with date filtering
    news_daily_filtered = news_daily_df
    if start_date or end_date:
        if not news_daily_df.empty and "date" in news_daily_df.columns:
            news_daily_filtered = news_daily_df.copy()
            news_daily_filtered["date_parsed"] = pd.to_datetime(news_daily_filtered["date"])
            if start_date:
                news_daily_filtered = news_daily_filtered[
                    news_daily_filtered["date_parsed"] >= start_date
                ]
            if end_date:
                news_daily_filtered = news_daily_filtered[
                    news_daily_filtered["date_parsed"] <= end_date
                ]

    if not news_daily_filtered.empty:
        total_articles = int(news_daily_filtered["n_articles"].sum())
        avg_stance = float(news_daily_filtered["stance_mean"].mean())

    return {
        "total_articles": total_articles,
        "avg_stance": round(avg_stance, 4),
        "event_count": event_count,
        "latest_event": latest_event,
    }


@router.get("/news-articles")
async def get_news_articles(limit: int = 100, offset: int = 0) -> list[dict]:
    """Get news articles with pagination."""
    df = read_csv_safe("news_scored.csv")

    if df.empty:
        return []

    # Apply pagination
    df_slice = df.iloc[offset : offset + limit]

    # Select relevant columns
    cols_to_use = ["date", "title", "stance"]
    if "url" in df.columns:
        cols_to_use.append("url")

    available_cols = [col for col in cols_to_use if col in df.columns]
    result = df_slice[available_cols].to_dict(orient="records")

    for row in result:
        row["date"] = str(row["date"])
        if pd.isna(row.get("stance")):
            row["stance"] = 0.0
        else:
            row["stance"] = float(row["stance"])
        row["title"] = str(row.get("title", ""))
        if "url" in row and pd.notna(row.get("url")):
            row["url"] = str(row["url"])

    return result


@router.get("/news-articles/by-date")
async def get_news_articles_by_date(date: str, days: int = 3) -> list[dict]:
    """Get news articles for a specific date range centered around the given date.

    Args:
        date: Target date in YYYY-MM-DD format (e.g., "2024-01-15")
        days: Number of days to include before and after the target date (default: 3)

    Returns:
        List of news articles sorted by stance score (most hawkish/dovish first)

    Example:
        GET /api/data/news-articles/by-date?date=2024-01-15&days=3
        Returns articles from 2024-01-12 to 2024-01-18
    """
    from datetime import timedelta

    df = read_csv_safe("news_scored.csv")

    if df.empty:
        return []

    # Parse target date
    try:
        target_date = pd.to_datetime(date)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid date format: {date}. Use YYYY-MM-DD."
        ) from None

    # Calculate date range
    start_date = target_date - timedelta(days=days)
    end_date = target_date + timedelta(days=days)

    # Convert date column to datetime if it's not already
    # Check for published_at column (news_scored.csv uses this)
    date_col = "published_at" if "published_at" in df.columns else "date"
    if date_col not in df.columns:
        raise HTTPException(
            status_code=500, detail=f"Data file missing required date column: {date_col}"
        )

    df["date_parsed"] = pd.to_datetime(df[date_col])

    # Filter by date range
    mask = (df["date_parsed"] >= start_date) & (df["date_parsed"] <= end_date)
    filtered_df = df[mask].copy()

    if filtered_df.empty:
        logger.info(f"No articles found for date range {start_date} to {end_date}")
        return []

    # Get stance column
    stance_col = "stance_score" if "stance_score" in filtered_df.columns else "stance"

    # Filter out neutral articles (stance == 0) to show only impactful news
    filtered_df = filtered_df[filtered_df[stance_col] != 0].copy()

    if filtered_df.empty:
        logger.info(f"No impactful articles found for date range {start_date} to {end_date}")
        return []

    # Sort by absolute stance score (most hawkish/dovish first)
    filtered_df["stance_abs"] = filtered_df[stance_col].abs()
    filtered_df = filtered_df.sort_values("stance_abs", ascending=False)

    # Select relevant columns
    cols_to_use = [date_col, "title", stance_col]
    if "google_url" in filtered_df.columns:
        cols_to_use.append("google_url")

    available_cols = [col for col in cols_to_use if col in filtered_df.columns]
    result = filtered_df[available_cols].to_dict(orient="records")

    # Format output - rename columns for consistency
    for row in result:
        # Rename date column to "date" for frontend
        row["date"] = str(row[date_col])
        # Rename stance column to "stance" for frontend
        if pd.isna(row.get(stance_col)):
            row["stance"] = 0.0
        else:
            row["stance"] = float(row[stance_col])
        row["title"] = str(row.get("title", ""))
        # Handle google_url -> url
        if "google_url" in row and pd.notna(row.get("google_url")):
            row["url"] = str(row["google_url"])
        elif "url" in row and pd.notna(row.get("url")):
            row["url"] = str(row["url"])

    logger.info(f"Returning {len(result)} articles for date range {start_date} to {end_date}")
    return result


# ============================================================================
# Data Refresh Endpoints
# ============================================================================


@router.post("/refresh", response_model=JobCreateResponse)
async def start_refresh(
    background_tasks: BackgroundTasks, request: RefreshRequest | None = None
) -> JobCreateResponse:
    """Start a new data refresh job.

    This endpoint initiates an asynchronous pipeline execution that:
    1. Collects news from RSS feeds
    2. Scores articles for monetary policy stance
    3. Aggregates data to daily level
    4. Fetches base rates from ECOS API
    5. Detects rate change events
    6. Performs event study analysis

    Args:
        background_tasks: FastAPI background tasks manager
        request: Optional refresh request with date range parameters

    Returns:
        JobCreateResponse with job_id for tracking progress

    Example:
        POST /api/data/refresh
        Body: {"start_date": "2024-01-01", "end_date": "2024-12-31"}
        Response: {"job_id": "uuid", "status": "pending", "message": "..."}
    """
    try:
        # Create configuration from environment
        config = Settings()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from None

    # Create new job
    job_id = job_store.create_job()

    # Extract dates from request if provided (Pydantic auto-converts strings to date)
    start_date = request.start_date if request else None
    end_date = request.end_date if request else None

    # Add background task to run pipeline
    background_tasks.add_task(run_refresh_pipeline, job_id, config, start_date, end_date)

    # Log date range info
    if start_date and end_date:
        logger.info(f"Started refresh job {job_id} with date range: {start_date} to {end_date}")
    else:
        logger.info(f"Started refresh job {job_id} with default date range")

    return JobCreateResponse(
        job_id=job_id,
        status="pending",
        message="Data refresh job started successfully. Use the job_id to track progress.",
    )


@router.get("/refresh/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: UUID) -> JobStatus:
    """Get the status of a refresh job.

    Args:
        job_id: Job identifier

    Returns:
        JobStatus with current progress and status

    Raises:
        HTTPException: If job not found (404)

    Example:
        GET /api/data/refresh/status/123e4567-e89b-12d3-a456-426614174000
        Response: {
            "job_id": "...",
            "status": "running",
            "progress": 45,
            "stage": "aggregating",
            "message": "Aggregating to daily level...",
            "created_at": "2025-01-27T10:00:00Z",
            "updated_at": "2025-01-27T10:05:00Z"
        }
    """
    job = job_store.get_job(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobStatus(**job)


@router.get("/refresh/jobs", response_model=JobListResponse)
async def list_jobs() -> JobListResponse:
    """List all refresh jobs.

    Returns:
        JobListResponse with all jobs sorted by creation time (newest first)

    Example:
        GET /api/data/refresh/jobs
        Response: {
            "jobs": [...],
            "total": 5
        }
    """
    jobs = job_store.list_jobs()

    return JobListResponse(jobs=[JobStatus(**job) for job in jobs], total=len(jobs))
