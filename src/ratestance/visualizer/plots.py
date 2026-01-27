"""Visualization for stance analysis and event studies."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger


class Visualizer:
    """Generates visualization plots for stance analysis."""

    def __init__(self, output_dir: str = "outputs") -> None:
        """Initialize the Visualizer.

        Args:
            output_dir: Directory to save output plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configure matplotlib for Korean text support
        plt.rcParams["font.sans-serif"] = ["AppleGothic", "Malgun Gothic", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False

    def plot_timeseries(
        self,
        daily_stance: pd.DataFrame,
        events: pd.DataFrame,
        output_filename: str = "news_stance_timeseries.png",
    ) -> None:
        """Generate time series plot of daily stance scores with event markers.

        Args:
            daily_stance: DataFrame with columns: date, stance_mean
            events: DataFrame with columns: date, event_type
            output_filename: Output filename

        Raises:
            ValueError: If required columns are missing
        """
        # Validate input
        if "date" not in daily_stance.columns or "stance_mean" not in daily_stance.columns:
            raise ValueError("Missing required columns in daily_stance: date, stance_mean")
        if "date" not in events.columns or "event_type" not in events.columns:
            raise ValueError("Missing required columns in events: date, event_type")

        logger.info("Generating time series plot")

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 6))

        # Plot daily stance
        daily_stance = daily_stance.copy()
        daily_stance["date"] = pd.to_datetime(daily_stance["date"])
        ax.plot(
            daily_stance["date"],
            daily_stance["stance_mean"],
            linewidth=1.5,
            alpha=0.7,
            label="Daily Stance Score",
        )

        # Mark rate change events
        events = events.copy()
        events["date"] = pd.to_datetime(events["date"])

        # Raise events (red)
        raise_events = events[events["event_type"] == "raise"]
        if len(raise_events) > 0:
            ax.vlines(
                raise_events["date"],
                ymin=daily_stance["stance_mean"].min(),
                ymax=daily_stance["stance_mean"].max(),
                colors="red",
                linestyles="solid",
                alpha=0.5,
                label="Rate Raise",
            )

        # Cut events (blue)
        cut_events = events[events["event_type"] == "cut"]
        if len(cut_events) > 0:
            ax.vlines(
                cut_events["date"],
                ymin=daily_stance["stance_mean"].min(),
                ymax=daily_stance["stance_mean"].max(),
                colors="blue",
                linestyles="solid",
                alpha=0.5,
                label="Rate Cut",
            )

        # Hold events (gray, lighter)
        hold_events = events[events["event_type"] == "hold"]
        if len(hold_events) > 0 and len(hold_events) < 20:  # Only show if not too many
            ax.vlines(
                hold_events["date"],
                ymin=daily_stance["stance_mean"].min(),
                ymax=daily_stance["stance_mean"].max(),
                colors="gray",
                linestyles="dotted",
                alpha=0.3,
                label="Rate Hold",
            )

        # Add horizontal line at y=0
        ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5, alpha=0.5)

        # Labels and title
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Stance Score (Hawkish - Dovish)", fontsize=12)
        ax.set_title("News Stance Time Series with Rate Change Events", fontsize=14)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)

        # Rotate x-axis labels
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        # Save plot
        output_path = self.output_dir / output_filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Time series plot saved to {output_path}")

    def plot_event_study(
        self,
        event_study_table: pd.DataFrame,
        output_filename: str = "event_study.png",
    ) -> None:
        """Generate event study plot by event type.

        Args:
            event_study_table: DataFrame with columns:
                event_type, day_offset, stance_mean, n_articles
            output_filename: Output filename

        Raises:
            ValueError: If required columns are missing
        """
        # Validate input
        required_cols = ["event_type", "day_offset", "stance_mean", "n_articles"]
        for col in required_cols:
            if col not in event_study_table.columns:
                raise ValueError(f"Missing required column: {col}")

        logger.info("Generating event study plot")

        # Aggregate by event_type and day_offset
        agg_data = (
            event_study_table.groupby(["event_type", "day_offset"])
            .agg({"stance_mean": "mean", "n_articles": "sum"})
            .reset_index()
        )

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot each event type
        for event_type in ["raise", "cut", "hold"]:
            data = agg_data[agg_data["event_type"] == event_type]
            if len(data) > 0:
                label_map = {"raise": "Rate Raise", "cut": "Rate Cut", "hold": "Rate Hold"}
                color_map = {"raise": "red", "cut": "blue", "hold": "gray"}
                ax.plot(
                    data["day_offset"],
                    data["stance_mean"],
                    marker="o",
                    linewidth=2,
                    markersize=4,
                    label=label_map[event_type],
                    color=color_map[event_type],
                    alpha=0.8,
                )

        # Add vertical line at day_offset=0
        ax.axvline(x=0, color="black", linestyle="--", linewidth=1, alpha=0.5)

        # Add horizontal line at y=0
        ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5, alpha=0.5)

        # Labels and title
        ax.set_xlabel("Day Offset Relative to Event", fontsize=12)
        ax.set_ylabel("Average Stance Score", fontsize=12)
        ax.set_title("Event Study: News Stance Around Rate Changes", fontsize=14)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save plot
        output_path = self.output_dir / output_filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Event study plot saved to {output_path}")
