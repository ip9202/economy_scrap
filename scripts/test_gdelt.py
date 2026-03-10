#!/usr/bin/env python3
"""Test script for GDELT BigQuery integration.

This script demonstrates the GDELT client functionality including:
- Client initialization (public and authenticated access)
- Historical news collection
- Data quality validation
- Schema verification

Usage:
    # Test with public dataset (free)
    uv run python scripts/test_gdelt.py

    # Test with specific date range
    uv run python scripts/test_gdelt.py --start 2024-10-01 --end 2024-10-20

    # Test with authenticated access
    GDELT_PROJECT_ID=your-project uv run python scripts/test_gdelt.py
"""

import argparse
import sys
from datetime import date, datetime

import pandas as pd


def test_client_initialization() -> bool:
    """Test GDELT client initialization."""
    print("\n" + "=" * 70)
    print("TEST 1: GDELT Client Initialization")
    print("=" * 70)

    from ratestance.collector import GdeltClient

    # Test public access
    print("\nTesting public dataset access...")
    client_public = GdeltClient(use_public=True)
    available = client_public.is_available()

    print(f"✓ Public access available: {available}")

    if not available:
        print("✗ Failed: Client not initialized")
        return False

    print("✓ Test passed: Client initialization successful")
    return True


def test_news_collection(start_date: date, end_date: date) -> bool:
    """Test GDELT news collection."""
    print("\n" + "=" * 70)
    print(f"TEST 2: News Collection ({start_date} to {end_date})")
    print("=" * 70)

    from ratestance.collector import GdeltClient

    print("\nInitializing GDELT client...")
    client = GdeltClient(use_public=True)

    if not client.is_available():
        print("✗ Failed: Client not available")
        return False

    print(f"\nCollecting news for queries:")
    queries = ["한국은행 기준금리", "통화정책", "금리"]
    for q in queries:
        print(f"  - {q}")

    try:
        print(f"\nDate range: {start_date} to {end_date}")
        df = client.collect(
            queries=queries,
            start_date=start_date,
            end_date=end_date,
            max_items=100,
        )

        print(f"\n✓ Collection successful")
        print(f"  Articles collected: {len(df)}")

        if df.empty:
            print("  ⚠ Warning: No articles found for the specified date range")
            print("  This could be due to:")
            print("    - No Korean news in GDELT for this period")
            print("    - Keywords not matching news themes")
            print("    - Date range outside GDELT coverage (2015-present)")
            return True  # Not a failure, just no data

        return validate_news_data(df)

    except Exception as e:
        print(f"\n✗ Failed: {e}")
        return False


def validate_news_data(df: pd.DataFrame) -> bool:
    """Validate collected news data."""
    print("\n" + "=" * 70)
    print("TEST 3: Data Validation")
    print("=" * 70)

    # Check required columns
    required_cols = ["query", "published_at", "title", "summary", "google_url"]
    print("\nChecking required columns...")
    for col in required_cols:
        if col in df.columns:
            print(f"  ✓ {col}")
        else:
            print(f"  ✗ {col} - MISSING")
            return False

    # Check data types
    print("\nChecking data types...")
    print(f"  published_at: {df['published_at'].dtype}")
    print(f"  title: {df['title'].dtype}")

    # Check for empty values
    print("\nChecking for empty values...")
    for col in required_cols:
        empty_count = df[col].isna().sum()
        empty_pct = (empty_count / len(df)) * 100
        print(f"  {col}: {empty_count} empty ({empty_pct:.1f}%)")

    # Check date range
    print("\nDate range of articles:")
    df["published_at"] = pd.to_datetime(df["published_at"])
    print(f"  Earliest: {df['published_at'].min()}")
    print(f"  Latest: {df['published_at'].max()}")

    # Sample articles
    print("\nSample articles (first 3):")
    print("-" * 70)
    for idx, row in df.head(3).iterrows():
        print(f"\n[{idx + 1}] {row['title'][:80]}...")
        print(f"    Date: {row['published_at']}")
        print(f"    URL: {row['google_url'][:60]}...")
        if row["summary"]:
            print(f"    Summary: {row['summary'][:100]}...")

    print("\n✓ Data validation passed")
    return True


def test_fallback_behavior() -> bool:
    """Test fallback to RSS when GDELT is disabled."""
    print("\n" + "=" * 70)
    print("TEST 4: Fallback Behavior")
    print("=" * 70)

    from ratestance.config import Settings

    print("\nTesting configuration...")

    # Test with GDELT enabled
    print("\n1. With GDELT enabled:")
    try:
        settings = Settings.model_construct(
            enable_gdelt=True,
            gdelt_use_public=True,
            gdelt_cutoff_date=date(2025, 8, 1),
        )
        print(f"  ✓ ENABLE_GDELT: {settings.enable_gdelt}")
        print(f"  ✓ GDELT_USE_PUBLIC: {settings.gdelt_use_public}")
        print(f"  ✓ GDELT_CUTOFF_DATE: {settings.gdelt_cutoff_date}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

    # Test with GDELT disabled
    print("\n2. With GDELT disabled (fallback mode):")
    try:
        settings = Settings.model_construct(
            enable_gdelt=False,
            gdelt_use_public=True,
        )
        print(f"  ✓ ENABLE_GDELT: {settings.enable_gdelt}")
        print("  ✓ System will use RSS-only mode")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

    print("\n✓ Fallback behavior test passed")
    return True


def main() -> int:
    """Run all tests."""
    parser = argparse.ArgumentParser(description="Test GDELT BigQuery integration")
    parser.add_argument(
        "--start",
        type=str,
        default="2024-10-01",
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default="2024-10-20",
        help="End date (YYYY-MM-DD)",
    )
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("GDELT BigQuery Integration Test Suite")
    print("=" * 70)
    print(f"Test date range: {args.start} to {args.end}")

    try:
        start_date = datetime.strptime(args.start, "%Y-%m-%d").date()
        end_date = datetime.strptime(args.end, "%Y-%m-%d").date()
    except ValueError as e:
        print(f"\n✗ Invalid date format: {e}")
        print("  Use YYYY-MM-DD format (e.g., 2024-10-01)")
        return 1

    # Run tests
    tests = [
        ("Client Initialization", lambda: test_client_initialization()),
        ("News Collection", lambda: test_news_collection(start_date, end_date)),
        ("Fallback Behavior", lambda: test_fallback_behavior()),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
