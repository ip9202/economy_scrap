"""FRED API client for US Federal Funds Rate."""

from datetime import date

import pandas as pd
import requests
from loguru import logger


class FredClient:
    """Client for FRED (Federal Reserve Economic Data) API.

    Attributes:
        api_key: FRED API authentication key
        base_url: FRED API base URL
        timeout: HTTP request timeout in seconds
    """

    def __init__(self, api_key: str, timeout: int = 30) -> None:
        """Initialize the FRED client.

        Args:
            api_key: FRED API authentication key
            timeout: HTTP request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        self.timeout = timeout

    def fetch_us_rates(
        self, start_date: date, end_date: date, series_id: str = "FEDFUNDS"
    ) -> pd.DataFrame:
        """Fetch US Federal Funds Rate time series from FRED.

        Args:
            start_date: Start date for data collection
            end_date: End date for data collection
            series_id: FRED series ID (default: FEDFUNDS = Effective Federal Funds Rate, 월별)

        Returns:
            DataFrame with columns: date, value, unit, name, source

        Raises:
            ValueError: If API request fails or returns no data
        """
        logger.info(
            "Fetching US rates from FRED",
            extra={
                "series": series_id,
                "start_date": str(start_date),
                "end_date": str(end_date),
            },
        )

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date.strftime("%Y-%m-%d"),
            "observation_end": end_date.strftime("%Y-%m-%d"),
        }

        try:
            response = requests.get(
                f"{self.base_url}/series/observations",
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"FRED API request failed: {e}")
            raise ValueError(f"FRED API request failed: {e}") from e

        observations = data.get("observations", [])
        rows = []
        for obs in observations:
            value = obs.get("value", ".")
            # FRED 결측치는 "."로 표시
            if value in (".", ""):
                continue
            rows.append(
                {
                    "date": obs.get("date"),
                    "value": float(value),
                    "unit": "%",
                    "name": "US Federal Funds Rate",
                    "source": "FRED",
                }
            )

        if not rows:
            logger.warning("No US rate observations returned from FRED")
            return pd.DataFrame(columns=["date", "value", "unit", "name", "source"])

        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        logger.info(f"Fetched {len(df)} US rate observations from FRED")
        return df
