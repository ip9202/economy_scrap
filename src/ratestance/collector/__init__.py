"""Data collection modules for RateStance pipeline."""

from ratestance.collector.ecos_client import EcosClient
from ratestance.collector.news_collector import NewsCollector

__all__ = ["NewsCollector", "EcosClient"]
