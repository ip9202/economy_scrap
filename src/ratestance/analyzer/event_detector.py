"""Rate change event detection."""

import pandas as pd
from loguru import logger


class EventDetector:
    """Detects rate change events from base rate time series."""

    def detect(self, rate_series: pd.DataFrame) -> pd.DataFrame:
        """Detect rate change events from time series.

        Args:
            rate_series: DataFrame with columns: date, value

        Returns:
            DataFrame with columns: date, prev_value, value, diff, event_type
            - event_type is 'raise' if diff > 0
            - event_type is 'cut' if diff < 0
            - event_type is 'hold' if diff == 0

        Raises:
            ValueError: If required columns are missing
        """
        # Validate input
        if "date" not in rate_series.columns:
            raise ValueError("Missing required column: date")
        if "value" not in rate_series.columns:
            raise ValueError("Missing required column: value")

        logger.info(f"Detecting events from {len(rate_series)} rate data points")

        # Create copy to avoid modifying original
        df = rate_series.copy()

        # Sort by date
        df = df.sort_values("date")

        # Calculate previous value
        df["prev_value"] = df["value"].shift(1)

        # Calculate difference
        df["diff"] = df["value"] - df["prev_value"]

        # Classify event type
        df["event_type"] = df["diff"].apply(self._classify_event)

        # Remove first row (no previous value)
        df = df[df["prev_value"].notna()]

        # Select and rename columns
        events = df[["date", "prev_value", "value", "diff", "event_type"]].copy()

        # Log event statistics
        event_counts = events["event_type"].value_counts()
        logger.info(
            "Event detection complete",
            extra={
                "total_events": len(events),
                "raise_events": int(event_counts.get("raise", 0)),
                "cut_events": int(event_counts.get("cut", 0)),
                "hold_events": int(event_counts.get("hold", 0)),
            },
        )

        # Warn if no rate changes detected
        if event_counts.get("raise", 0) + event_counts.get("cut", 0) == 0:
            logger.warning(
                "No raise/cut events detected, analyzing hold events only. "
                "This may indicate a period of policy stability."
            )

        return events

    def _classify_event(self, diff: float) -> str:
        """Classify event type based on rate difference.

        Args:
            diff: Rate difference (current - previous)

        Returns:
            Event type: 'raise', 'cut', or 'hold'
        """
        if diff > 0:
            return "raise"
        elif diff < 0:
            return "cut"
        else:
            return "hold"
