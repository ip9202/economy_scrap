"""ECOS API client for fetching Bank of Korea base rates."""

from datetime import date
from typing import Any

import pandas as pd
import requests
from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class EcosClient:
    """Client for ECOS (Economic Statistics System) API.

    Attributes:
        api_key: ECOS API authentication key
        base_url: ECOS API base URL
        timeout: HTTP request timeout in seconds
    """

    def __init__(self, api_key: str, timeout: int = 30) -> None:
        """Initialize the ECOS client.

        Args:
            api_key: ECOS API authentication key
            timeout: HTTP request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = "https://ecos.bok.or.kr/api"
        self.timeout = timeout

    def fetch_base_rates(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Fetch base rate time series from ECOS API.

        Args:
            start_date: Start date for data collection
            end_date: End date for data collection

        Returns:
            DataFrame with columns: date, value, unit, name, source

        Raises:
            ValueError: If API request fails or returns no data
        """
        logger.info(
            "Fetching base rates from ECOS API",
            extra={
                "start_date": str(start_date),
                "end_date": str(end_date),
            },
        )

        # Try to discover the statistic code for "한국은행 기준금리"
        stat_code = self._discover_base_rate_statistic()

        # Fetch time series data
        data = self._fetch_time_series(stat_code, start_date, end_date)

        if not data:
            raise ValueError("No data returned from ECOS API")

        # Create DataFrame
        df = pd.DataFrame(data)

        # Ensure required columns
        if "date" not in df.columns or "value" not in df.columns:
            raise ValueError("API response missing required columns")

        # Filter by date range
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

        logger.info(f"Fetched {len(df)} data points from ECOS API")

        return df

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout)),
    )
    def _discover_base_rate_statistic(self) -> str:
        """Discover the statistic code for '한국은행 기준금리'.

        Returns:
            Statistic code string

        Raises:
            ValueError: If discovery fails
        """
        logger.info("Discovering statistic code for '한국은행 기준금리'")

        # Use KeyStatisticList endpoint to search for base rate
        url = f"{self.base_url}/KeyStatisticList/{self.api_key}/json/kr/1/100//"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Parse response defensively
            if data.get("KeyStatisticList") and data["KeyStatisticList"].get("row"):
                rows = data["KeyStatisticList"]["row"]

                # Search for "한국은행 기준금리" in the results
                for row in rows:
                    stat_name = row.get("STAT_NAME", "")
                    if "한국은행 기준금리" in stat_name or "기준금리" in stat_name:
                        stat_code = row.get("STAT_CODE", "")
                        logger.info(f"Found statistic: {stat_name} (code: {stat_code})")
                        return str(stat_code)

            # Fallback: Try common statistic codes
            fallback_codes = ["722Y001", "010Y002", "722Y002"]
            for code in fallback_codes:
                logger.warning(f"Using fallback statistic code: {code}")
                return code

            raise ValueError("Could not discover statistic code for base rate")

        except requests.RequestException as e:
            logger.error(f"ECOS API request failed: {e}")
            raise ValueError(f"ECOS API request failed: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout)),
    )
    def _fetch_time_series(
        self, stat_code: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        """Fetch time series data for a specific statistic.

        Args:
            stat_code: Statistic code
            start_date: Start date
            end_date: End date

        Returns:
            List of data points

        Raises:
            ValueError: If API request fails
        """
        # Format dates for API (YYYYMMDD)
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")

        url = (
            f"{self.base_url}/StatisticSearch/{self.api_key}/json/kr/1/10000/"
            f"{stat_code}/D/{start_str}/{end_str}/0101000/"
        )

        logger.debug(f"Fetching time series from: {url}")

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Parse response defensively
            results = []
            if data.get("StatisticSearch") and data["StatisticSearch"].get("row"):
                rows = data["StatisticSearch"]["row"]

                for row in rows:
                    data_point = {
                        "date": row.get("TIME", ""),
                        "value": self._parse_float(row.get("DATA_VALUE", "0")),
                        "unit": row.get("UNIT_NAME", ""),
                        "name": row.get("STAT_NAME", "한국은행 기준금리"),
                        "source": "ECOS",
                    }
                    results.append(data_point)

            return results

        except requests.RequestException as e:
            logger.error(f"ECOS API time series request failed: {e}")
            raise ValueError(f"ECOS API time series request failed: {e}") from e

    def _parse_float(self, value: str) -> float:
        """Parse float value with defensive error handling.

        Args:
            value: String value to parse

        Returns:
            Parsed float value

        Raises:
            ValueError: If value cannot be parsed
        """
        try:
            # Remove common formatting characters
            cleaned = value.replace(",", "").strip()
            return float(cleaned)
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not parse float value: {value}")
            raise ValueError(f"Invalid float value: {value}") from e
