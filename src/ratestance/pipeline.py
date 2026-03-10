"""Pipeline orchestration for RateStance."""

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from loguru import logger

from ratestance.aggregator import DailyAggregator
from ratestance.analyzer import EventDetector, EventStudy
from ratestance.collector import EcosClient, NewsCollector
from ratestance.config import Settings
from ratestance.scorer import StanceScorer
from ratestance.visualizer import Visualizer


class Pipeline:
    """Orchestrates the RateStance data pipeline.

    Attributes:
        config: Configuration settings
        news_collector: News RSS collector
        ecos_client: ECOS API client
        stance_scorer: Stance scoring module
        daily_aggregator: Daily aggregation module
        event_detector: Event detection module
        event_study: Event study module
        visualizer: Visualization module
    """

    def __init__(self, config: Settings) -> None:
        """Initialize the pipeline with configuration.

        Args:
            config: Configuration settings
        """
        self.config = config
        self.news_collector = NewsCollector()
        self.ecos_client = EcosClient(api_key=config.ecod_api_key)
        self.stance_scorer = StanceScorer(
            hawk_words=config.hawk_words, dove_words=config.dove_words
        )
        self.daily_aggregator = DailyAggregator()
        self.event_detector = EventDetector()
        self.event_study = EventStudy()
        self.visualizer = Visualizer()

        # Ensure output directories exist
        Path("data").mkdir(exist_ok=True)
        Path("outputs").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

        logger.info("Pipeline initialized", extra={"config": config.model_dump()})

    def run(self) -> dict[str, pd.DataFrame]:
        """Execute the full pipeline.

        Returns:
            Dictionary containing all pipeline outputs:
                - news_raw: Raw RSS articles
                - news_scored: Articles with stance scores
                - news_daily: Daily aggregated stance
                - rate_series: Base rate time series
                - events: Detected rate change events
                - event_study_table: Event study analysis

        Raises:
            ValueError: If pipeline stage fails
        """
        logger.info("Starting RateStance pipeline")

        # Stage 1: Calculate date range
        date_range = self._calculate_date_range()
        logger.info(
            "Date range calculated",
            extra={
                "start_date": str(date_range[0]),
                "end_date": str(date_range[1]),
                "months_back": self.config.months_back,
            },
        )

        # Stage 2: Collect news from RSS
        logger.info("Stage 2: Collecting news from RSS feeds")
        news_raw = self.news_collector.collect(
            queries=self.config.queries,
            start_date=date_range[0],
            end_date=date_range[1],
            max_items=self.config.max_items_per_query,
        )
        self._save_csv(news_raw, "data/news_raw.csv", merge_on="google_url")

        # Stage 3: Score articles for stance
        logger.info("Stage 3: Scoring articles for stance")
        news_scored = self.stance_scorer.score(news_raw)
        self._save_csv(news_scored, "data/news_scored.csv", merge_on="google_url")

        # Stage 4: Aggregate to daily level
        logger.info("Stage 4: Aggregating to daily level")
        # Load existing news_scored to aggregate all historical data
        news_scored_path = Path("data/news_scored.csv")
        if news_scored_path.exists():
            existing_scored = pd.read_csv(news_scored_path, encoding="utf-8-sig")
            logger.info(f"Loaded {len(existing_scored)} existing scored articles for aggregation")
            news_daily = self.daily_aggregator.aggregate(existing_scored)
        else:
            news_daily = self.daily_aggregator.aggregate(news_scored)
        self._save_csv(news_daily, "data/news_daily.csv", merge_on="date")

        # Stage 5: Collect base rates from ECOS
        logger.info("Stage 5: Collecting base rates from ECOS API")
        rate_series = self.ecos_client.fetch_base_rates(
            start_date=date_range[0], end_date=date_range[1]
        )
        self._save_csv(rate_series, "data/rate_series.csv", merge_on="date")

        # Stage 6: Detect rate change events
        logger.info("Stage 6: Detecting rate change events")
        events = self.event_detector.detect(rate_series)
        self._save_csv(events, "data/events.csv")

        # Stage 7: Perform event study
        logger.info("Stage 7: Performing event study analysis")
        event_study_table = self.event_study.analyze(
            events=events,
            daily_stance=news_daily,
            window_days=self.config.event_window_days,
        )
        self._save_csv(event_study_table, "data/event_study_table.csv")

        # Stage 8: Generate visualizations
        logger.info("Stage 8: Generating visualizations")
        self.visualizer.plot_timeseries(news_daily, events)
        self.visualizer.plot_event_study(event_study_table)

        logger.success("Pipeline completed successfully")

        return {
            "news_raw": news_raw,
            "news_scored": news_scored,
            "news_daily": news_daily,
            "rate_series": rate_series,
            "events": events,
            "event_study_table": event_study_table,
        }

    def _calculate_date_range(self) -> tuple[date, date]:
        """Calculate date range based on months_back configuration.

        Returns:
            Tuple of (start_date, end_date)
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=self.config.months_back * 30)
        return start_date, end_date

    def _save_csv(self, df: pd.DataFrame, filepath: str, merge_on: str | None = None) -> None:
        """Save DataFrame to CSV file, merging with existing data if merge_on is specified.

        Args:
            df: DataFrame to save
            filepath: Output file path
            merge_on: Column name to merge on (prevents duplicates). If None, overwrites.
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # If merge_on is specified and file exists, merge with existing data
        if merge_on and Path(filepath).exists():
            try:
                existing_df = pd.read_csv(filepath, encoding="utf-8-sig")
                # Concatenate and remove duplicates based on merge_on column
                merged_df = pd.concat([existing_df, df], ignore_index=True)
                merged_df = merged_df.drop_duplicates(subset=[merge_on], keep="last")
                merged_df.to_csv(filepath, index=False, encoding="utf-8-sig")
                logger.info(f"Merged and saved {len(merged_df)} rows to {filepath} (added {len(df)} new)")
                return
            except Exception as e:
                logger.warning(f"Failed to merge with existing file: {e}. Saving as new file.")

        # Default behavior: overwrite
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        logger.info(f"Saved {len(df)} rows to {filepath}")
