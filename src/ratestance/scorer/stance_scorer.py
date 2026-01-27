"""Stance scoring for news articles."""

import pandas as pd
from loguru import logger


class StanceScorer:
    """Scores news articles for hawkish/dovish monetary policy stance.

    Attributes:
        hawk_words: Keywords indicating hawkish stance
        dove_words: Keywords indicating dovish stance
    """

    def __init__(self, hawk_words: list[str], dove_words: list[str]) -> None:
        """Initialize the StanceScorer.

        Args:
            hawk_words: Keywords indicating hawkish stance (rate increase favored)
            dove_words: Keywords indicating dovish stance (rate decrease favored)
        """
        self.hawk_words = [word.lower() for word in hawk_words]
        self.dove_words = [word.lower() for word in dove_words]
        logger.info(
            "StanceScorer initialized",
            extra={
                "hawk_words_count": len(self.hawk_words),
                "dove_words_count": len(self.dove_words),
            },
        )

    def score(self, articles: pd.DataFrame) -> pd.DataFrame:
        """Score articles for hawkish/dovish stance.

        Args:
            articles: DataFrame with columns: query, published_at, title, summary, google_url

        Returns:
            DataFrame with additional columns: text, hawk_count, dove_count, stance_score

        Raises:
            ValueError: If required columns are missing
        """
        # Validate input
        required_columns = ["query", "published_at", "title", "summary", "google_url"]
        for col in required_columns:
            if col not in articles.columns:
                raise ValueError(f"Missing required column: {col}")

        logger.info(f"Scoring {len(articles)} articles for stance")

        # Create copy to avoid modifying original
        df = articles.copy()

        # Combine title and summary into text field
        df["text"] = df["title"] + " " + df["summary"]

        # Count hawkish and dovish keywords
        df["hawk_count"] = df["text"].apply(self._count_keywords, words=self.hawk_words)
        df["dove_count"] = df["text"].apply(self._count_keywords, words=self.dove_words)

        # Calculate stance score
        df["stance_score"] = df["hawk_count"] - df["dove_count"]

        # Log scoring statistics
        hawkish_count = (df["stance_score"] > 0).sum()
        dovish_count = (df["stance_score"] < 0).sum()
        neutral_count = (df["stance_score"] == 0).sum()

        logger.info(
            "Stance scoring complete",
            extra={
                "hawkish_articles": int(hawkish_count),
                "dovish_articles": int(dovish_count),
                "neutral_articles": int(neutral_count),
                "mean_stance_score": float(df["stance_score"].mean()),
                "std_stance_score": float(df["stance_score"].std()),
            },
        )

        return df

    def _count_keywords(self, text: str, words: list[str]) -> int:
        """Count occurrences of keywords in text (case-insensitive).

        Args:
            text: Text to search
            words: List of keywords to count

        Returns:
            Count of keyword occurrences
        """
        text_lower = text.lower()
        count = sum(text_lower.count(word) for word in words)
        return count
