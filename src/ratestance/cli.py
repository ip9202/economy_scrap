"""Command-line interface for RateStance."""

import argparse
import sys

from dotenv import load_dotenv
from loguru import logger

from ratestance.config import Settings
from ratestance.pipeline import Pipeline


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="RateStance MVP - Monetary Policy News Analysis Pipeline"
    )
    parser.add_argument(
        "--months-back",
        type=int,
        help="Historical data window in months (default: from .env or 6)",
    )
    parser.add_argument(
        "--event-window",
        type=int,
        help="Event study window in days (default: from .env or 14)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Output directory for plots (default: outputs)",
    )

    args = parser.parse_args()

    # Configure logging
    logger.remove()  # Remove default handler
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stderr,
        level="INFO",
        format=log_format,
    )
    logger.add(
        "logs/ratestance_{time:YYYYMMDD}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
    )

    try:
        # Load environment variables
        logger.info("Loading environment variables from .env")
        load_dotenv()

        # Load configuration (with CLI overrides)
        config_kwargs = {}
        if args.months_back is not None:
            config_kwargs["months_back"] = args.months_back
        if args.event_window is not None:
            config_kwargs["event_window_days"] = args.event_window

        logger.info("Initializing configuration")
        config = Settings(**config_kwargs)

        # Create and run pipeline
        logger.info("Creating pipeline")
        pipeline = Pipeline(config)

        logger.info("Running pipeline")
        results = pipeline.run()

        # Print summary
        logger.success("Pipeline execution completed successfully")
        logger.info(f"Collected {len(results['news_raw'])} articles")
        logger.info(f"Detected {len(results['events'])} rate events")
        logger.info(f"Generated {len(results['event_study_table'])} event study data points")
        logger.info(f"Outputs saved to {args.output_dir}/")

        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Pipeline execution failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
