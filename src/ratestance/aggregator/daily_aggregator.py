"""Daily aggregation of stance scores."""

import pandas as pd
from loguru import logger


class DailyAggregator:
    """Aggregates article-level stance scores to daily level."""

    def aggregate(self, news_scored: pd.DataFrame) -> pd.DataFrame:
        """Aggregate scored articles to daily level.

        Args:
            news_scored: DataFrame with article-level scores including:
                - published_at (datetime)
                - stance_score (int)
                - All other article columns

        Returns:
            DataFrame with daily aggregates: date, n_articles, stance_mean, stance_sum

        Raises:
            ValueError: If required columns are missing
        """
        # Validate input
        if "published_at" not in news_scored.columns:
            raise ValueError("Missing required column: published_at")
        if "stance_score" not in news_scored.columns:
            raise ValueError("Missing required column: stance_score")

        logger.info(f"Aggregating {len(news_scored)} articles to daily level")

        # Create copy to avoid modifying original
        df = news_scored.copy()

        # Extract date from datetime
        df["date"] = pd.to_datetime(df["published_at"]).dt.date

        # Aggregate by date
        daily = (
            df.groupby("date")
            .agg(
                n_articles=("stance_score", "size"),
                stance_mean=("stance_score", "mean"),
                stance_sum=("stance_score", "sum"),
            )
            .reset_index()
        )

        # Sort by date
        daily = daily.sort_values("date")

        # Fill missing days with NaN (to preserve time series structure)
        date_range = pd.date_range(start=daily["date"].min(), end=daily["date"].max(), freq="D")
        daily = daily.set_index("date").reindex(date_range).reset_index()
        daily.rename(columns={"index": "date"}, inplace=True)

        logger.info(
            "Daily aggregation complete",
            extra={
                "days_with_articles": int(daily["n_articles"].notna().sum()),
                "total_days": len(daily),
                "mean_articles_per_day": float(daily["n_articles"].mean()),
            },
        )

        return daily
