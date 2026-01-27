"""Event study analysis for stance dynamics around rate events."""

import pandas as pd
from loguru import logger


class EventStudy:
    """Performs event study analysis of news stance around rate change events."""

    def analyze(
        self,
        events: pd.DataFrame,
        daily_stance: pd.DataFrame,
        window_days: int = 14,
    ) -> pd.DataFrame:
        """Perform event study analysis around rate change events.

        Args:
            events: DataFrame with columns: date, event_type
            daily_stance: DataFrame with columns: date, stance_mean, n_articles
            window_days: Number of days before/after event to include

        Returns:
            DataFrame with columns: event_date, event_type, date, day_offset,
            stance_mean, n_articles

        Raises:
            ValueError: If required columns are missing
        """
        # Validate input
        if "date" not in events.columns or "event_type" not in events.columns:
            raise ValueError("Missing required columns in events: date, event_type")
        if "date" not in daily_stance.columns:
            raise ValueError("Missing required column in daily_stance: date")

        logger.info(
            "Performing event study analysis",
            extra={
                "num_events": len(events),
                "window_days": window_days,
            },
        )

        # Ensure dates are in the same format
        events = events.copy()
        events["date"] = pd.to_datetime(events["date"]).dt.date

        daily_stance = daily_stance.copy()
        daily_stance["date"] = pd.to_datetime(daily_stance["date"]).dt.date

        # Generate event study table
        study_rows = []

        for _, event in events.iterrows():
            event_date = event["date"]
            event_type = event["event_type"]

            # Create window around event
            for day_offset in range(-window_days, window_days + 1):
                window_date = event_date + pd.Timedelta(days=day_offset)

                # Find stance data for this date
                stance_row = daily_stance[daily_stance["date"] == window_date]

                if len(stance_row) > 0:
                    stance_mean = stance_row["stance_mean"].iloc[0]
                    n_articles = stance_row["n_articles"].iloc[0]
                else:
                    stance_mean = float("nan")
                    n_articles = 0

                study_rows.append(
                    {
                        "event_date": event_date,
                        "event_type": event_type,
                        "date": window_date,
                        "day_offset": day_offset,
                        "stance_mean": stance_mean,
                        "n_articles": n_articles,
                    }
                )

        # Create DataFrame
        event_study_table = pd.DataFrame(study_rows)

        logger.info(
            "Event study analysis complete",
            extra={
                "total_rows": len(event_study_table),
                "unique_events": event_study_table["event_date"].nunique(),
            },
        )

        return event_study_table
