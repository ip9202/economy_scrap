"""API routes for RateStance Dashboard."""

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from loguru import logger

router = APIRouter()

# Data directory path
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


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
