"""Configuration management for RateStance pipeline."""

from datetime import date

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for RateStance pipeline.

    Attributes:
        ecod_api_key: ECOS API authentication key
        months_back: Historical data collection window in months
        event_window_days: Event study window size in days (±N days)
        queries: News search queries for RSS feeds
        hawk_words: Keywords indicating hawkish stance
        dove_words: Keywords indicating dovish stance
        max_items_per_query: Maximum RSS items per query
    """

    ecod_api_key: str = Field(..., alias="ECOS_API_KEY")
    months_back: int = 6
    event_window_days: int = 14
    queries: list[str] = Field(
        default=[
            "한국은행 기준금리",
            "통화정책",
            "금리",
            # English keywords for GDELT matching
            "Bank of Korea interest rate",
            "BOK rate",
            "Korea monetary policy",
        ],
        alias="QUERIES"
    )
    hawk_words: list[str] = Field(
        default=["인상", "긴축", "물가압력", "과열", "억제", "경계", "매파"], alias="HAWK_WORDS"
    )
    dove_words: list[str] = Field(
        default=["인하", "완화", "둔화", "부양", "하방", "지원", "비둘기"], alias="DOVE_WORDS"
    )
    max_items_per_query: int = 100

    # GDELT BigQuery Configuration
    gdelt_project_id: str | None = Field(default=None, alias="GDELT_PROJECT_ID")
    gdelt_use_public: bool = Field(default=True, alias="GDELT_USE_PUBLIC")
    enable_gdelt: bool = Field(default=True, alias="ENABLE_GDELT")
    gdelt_cutoff_date: date = Field(default=date(2025, 8, 1), alias="GDELT_CUTOFF_DATE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("ecod_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that ECOS API key is not empty.

        Args:
            v: API key value

        Returns:
            Validated API key

        Raises:
            ValueError: If API key is empty or None
        """
        if not v or v.strip() == "" or v == "your_api_key_here":
            raise ValueError(
                "ECOS_API_KEY environment variable is required. "
                "Get your API key from https://ecos.bok.or.kr/api/"
            )
        return v

    @field_validator("months_back", "event_window_days", "max_items_per_query")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Validate that numeric parameters are positive integers.

        Args:
            v: Integer value to validate

        Returns:
            Validated positive integer

        Raises:
            ValueError: If value is not positive
        """
        if v <= 0:
            raise ValueError(f"Must be positive integer, got {v}")
        return v

    @field_validator("queries", "hawk_words", "dove_words")
    @classmethod
    def validate_non_empty_list(cls, v: list[str]) -> list[str]:
        """Validate that list parameters are not empty.

        Args:
            v: List value to validate

        Returns:
            Validated non-empty list

        Raises:
            ValueError: If list is empty
        """
        if not v:
            raise ValueError("Cannot be empty list")
        return v
