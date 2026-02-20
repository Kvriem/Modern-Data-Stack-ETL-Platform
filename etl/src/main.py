"""
ETL Main Module

Orchestrates the extract-load process for all configured tables.
"""

import sys
import structlog
from datetime import datetime
from typing import Optional

from .config import ETLConfig, ETL_TABLES
from .extract import Extractor
from .load import Loader

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


def run_etl(
    config: Optional[ETLConfig] = None,
    tables: Optional[list] = None,
    full_refresh: bool = False
) -> dict:
    """
    Run the ETL process for all configured tables.

    Args:
        config: ETL configuration (uses env vars if not provided)
        tables: List of tables to process (uses ETL_TABLES if not provided)
        full_refresh: If True, ignore watermarks and do full extraction

    Returns:
        Dictionary with ETL results
    """
    config = config or ETLConfig.from_env()
    tables = tables or ETL_TABLES

    logger.info(
        "Starting ETL process",
        tables=tables,
        full_refresh=full_refresh,
        source_db=config.source_db.host,
        target_db=config.target_db.host
    )

    results = {
        "status": "success",
        "started_at": datetime.now().isoformat(),
        "tables": {},
        "total_rows": 0,
        "errors": []
    }

    try:
        with Extractor(config.source_db) as extractor, Loader(config.target_db) as loader:
            for table_name in tables:
                logger.info("Processing table", table=table_name)

                try:
                    # Get watermark for incremental loading
                    watermark = None
                    if not full_refresh:
                        watermark = loader.get_watermark(table_name)
                        if watermark:
                            logger.info(
                                "Using incremental extraction",
                                table=table_name,
                                watermark=watermark.isoformat()
                            )

                    # Extract data
                    rows = extractor.extract_full_table(table_name, watermark=watermark)

                    if not rows:
                        logger.info("No new rows to load", table=table_name)
                        results["tables"][table_name] = {
                            "status": "skipped",
                            "rows_extracted": 0,
                            "rows_loaded": 0
                        }
                        continue

                    # Load data
                    rows_loaded = loader.load_table(
                        table_name,
                        rows,
                        batch_size=config.batch_size
                    )

                    # Update watermark
                    max_updated_at = extractor.get_max_updated_at(table_name)
                    if max_updated_at:
                        loader.update_watermark(table_name, max_updated_at, rows_loaded)

                    results["tables"][table_name] = {
                        "status": "success",
                        "rows_extracted": len(rows),
                        "rows_loaded": rows_loaded
                    }
                    results["total_rows"] += rows_loaded

                    logger.info(
                        "Table processed successfully",
                        table=table_name,
                        rows_extracted=len(rows),
                        rows_loaded=rows_loaded
                    )

                except Exception as e:
                    error_msg = f"Error processing table {table_name}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    results["tables"][table_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    results["errors"].append(error_msg)

    except Exception as e:
        error_msg = f"ETL process failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        results["status"] = "failed"
        results["errors"].append(error_msg)

    results["completed_at"] = datetime.now().isoformat()

    if results["errors"]:
        results["status"] = "partial" if results["total_rows"] > 0 else "failed"

    logger.info(
        "ETL process completed",
        status=results["status"],
        total_rows=results["total_rows"],
        errors=len(results["errors"])
    )

    return results


def main() -> int:
    """
    Main entry point for ETL process.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info("=" * 60)
    logger.info("ETL PIPELINE STARTED")
    logger.info("=" * 60)

    try:
        results = run_etl()

        if results["status"] == "failed":
            logger.error("ETL pipeline failed", errors=results["errors"])
            return 1

        if results["status"] == "partial":
            logger.warning("ETL pipeline completed with errors", errors=results["errors"])
            return 1

        logger.info("ETL pipeline completed successfully")
        return 0

    except Exception as e:
        logger.error("Unexpected error in ETL pipeline", error=str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
