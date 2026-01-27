"""API routes for RateStance Dashboard."""

from pathlib import Path
from uuid import UUID

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger

from ratestance.api.job_store import job_store
from ratestance.api.refresh_models import JobCreateResponse, JobListResponse, JobStatus
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


async def run_refresh_pipeline(job_id: UUID, config: Settings) -> None:
    """Run the RateStance pipeline asynchronously with progress tracking.

    Args:
        job_id: Job identifier for status updates
        config: Pipeline configuration
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

        # Initialize pipeline
        pipeline = RefreshPipeline(config, progress_callback)

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

    def __init__(self, config: Settings, progress_callback: callable) -> None:
        """Initialize pipeline with progress callback.

        Args:
            config: Configuration settings
            progress_callback: Callback function for progress updates
        """
        super().__init__(config)
        self.progress_callback = progress_callback

    async def run(self) -> dict[str, pd.DataFrame]:
        """Execute the full pipeline with progress tracking.

        Returns:
            Dictionary containing all pipeline outputs

        Raises:
            ValueError: If pipeline stage fails
        """
        from ratestance.aggregator import DailyAggregator
        from ratestance.analyzer import EventDetector, EventStudy
        from ratestance.collector import EcosClient, NewsCollector
        from ratestance.scorer import StanceScorer
        from ratestance.visualizer import Visualizer

        logger.info("Starting RateStance pipeline with progress tracking")

        # Initialize components
        news_collector = NewsCollector()
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
        news_raw = news_collector.collect(
            queries=self.config.queries,
            start_date=date_range[0],
            end_date=date_range[1],
            max_items=self.config.max_items_per_query,
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
async def get_news_daily() -> list[dict]:
    """Get daily news sentiment data."""
    df = read_csv_safe("news_daily.csv")

    if df.empty:
        return []

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
async def get_rate_series() -> list[dict]:
    """Get interest rate time series data."""
    df = read_csv_safe("rate_series.csv")

    if df.empty:
        return []

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
async def get_events() -> list[dict]:
    """Get interest rate change events."""
    df = read_csv_safe("events.csv")

    if df.empty:
        return []

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
async def get_event_study() -> list[dict]:
    """Get event study analysis data."""
    df = read_csv_safe("event_study_table.csv")

    if df.empty:
        return []

    # Expected columns: event_date, event_type, day_offset, stance_mean, stance_std (optional)
    required_cols = ["event_date", "event_type", "day_offset", "stance_mean"]
    if not all(col in df.columns for col in required_cols):
        logger.error("Missing required columns in event_study_table.csv")
        raise HTTPException(status_code=500, detail="Data file missing required columns")

    result = df.to_dict(orient="records")

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
async def get_statistics() -> dict:
    """Get summary statistics."""
    news_daily_df = read_csv_safe("news_daily.csv")
    events_df = read_csv_safe("events.csv")

    total_articles = 0
    avg_stance = 0.0
    event_count = 0
    latest_event = "No events"

    if not news_daily_df.empty:
        total_articles = int(news_daily_df["n_articles"].sum())
        avg_stance = float(news_daily_df["stance_mean"].mean())

    if not events_df.empty:
        event_count = len(events_df)
        # Create description from available columns
        latest = events_df.iloc[0]
        event_type = latest.get("event_type", "hold")
        event_date = latest.get("date", "")
        latest_event = f"{event_type} ({event_date})"

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


# ============================================================================
# Data Refresh Endpoints
# ============================================================================


@router.post("/refresh", response_model=JobCreateResponse)
async def start_refresh(background_tasks: BackgroundTasks) -> JobCreateResponse:
    """Start a new data refresh job.

    This endpoint initiates an asynchronous pipeline execution that:
    1. Collects news from RSS feeds
    2. Scores articles for monetary policy stance
    3. Aggregates data to daily level
    4. Fetches base rates from ECOS API
    5. Detects rate change events
    6. Performs event study analysis

    Returns:
        JobCreateResponse with job_id for tracking progress

    Example:
        POST /api/data/refresh
        Response: {"job_id": "uuid", "status": "pending", "message": "..."}
    """
    try:
        # Create configuration from environment
        config = Settings()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    # Create new job
    job_id = job_store.create_job()

    # Add background task to run pipeline
    background_tasks.add_task(run_refresh_pipeline, job_id, config)

    logger.info(f"Started refresh job {job_id}")

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
