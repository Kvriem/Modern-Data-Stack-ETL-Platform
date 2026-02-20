"""
ETL Load Module

Handles data loading to the target database with upsert (merge) strategy.
"""

import structlog
import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config import DatabaseConfig

logger = structlog.get_logger(__name__)


class Loader:
    """Handles data loading to target database."""

    def __init__(self, config: DatabaseConfig):
        """
        Initialize loader with database configuration.

        Args:
            config: Target database configuration
        """
        self.config = config
        self._connection: Optional[psycopg2.extensions.connection] = None

    def connect(self) -> None:
        """Establish connection to target database."""
        logger.info(
            "Connecting to target database", host=self.config.host, db=self.config.name
        )
        self._connection = psycopg2.connect(**self.config.psycopg2_params)
        logger.info("Connected to target database successfully")

    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Disconnected from target database")

    def __enter__(self) -> "Loader":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()

    def get_watermark(self, table_name: str) -> Optional[datetime]:
        """
        Get the last extraction watermark for a table.

        Args:
            table_name: Name of the table

        Returns:
            Last extraction timestamp or None
        """
        if not self._connection:
            raise RuntimeError("Not connected to database")

        with self._connection.cursor() as cursor:
            query = """
                SELECT last_extracted_at
                FROM raw._etl_watermarks
                WHERE table_name = %s
            """
            cursor.execute(query, (table_name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def update_watermark(
        self, table_name: str, watermark: datetime, rows_processed: int
    ) -> None:
        """
        Update the extraction watermark for a table.

        Args:
            table_name: Name of the table
            watermark: New watermark timestamp
            rows_processed: Number of rows processed
        """
        if not self._connection:
            raise RuntimeError("Not connected to database")

        with self._connection.cursor() as cursor:
            query = """
                INSERT INTO raw._etl_watermarks (
                    table_name, last_extracted_at, last_loaded_at, rows_processed
                )
                VALUES (%s, %s, CURRENT_TIMESTAMP, %s)
                ON CONFLICT (table_name)
                DO UPDATE SET
                    last_extracted_at = EXCLUDED.last_extracted_at,
                    last_loaded_at = CURRENT_TIMESTAMP,
                    rows_processed = EXCLUDED.rows_processed
            """
            cursor.execute(query, (table_name, watermark, rows_processed))
            self._connection.commit()
            logger.info(
                "Updated watermark",
                table=table_name,
                watermark=watermark.isoformat(),
                rows_processed=rows_processed,
            )

    def upsert_batch(
        self, table_name: str, rows: List[Dict[str, Any]], primary_key: str = "id"
    ) -> int:
        """
        Upsert a batch of rows to the target table.

        Uses PostgreSQL ON CONFLICT for idempotent upserts.

        Args:
            table_name: Name of the target table (in raw schema)
            rows: List of rows to upsert
            primary_key: Name of the primary key column

        Returns:
            Number of rows upserted
        """
        if not self._connection or not rows:
            return 0

        # Get columns from first row
        columns = list(rows[0].keys())

        # Add ETL metadata column
        if "_etl_loaded_at" not in columns:
            columns.append("_etl_loaded_at")
            for row in rows:
                row["_etl_loaded_at"] = datetime.now()

        # Build upsert query
        columns_str = ", ".join(columns)
        update_cols = [
            f"{col} = EXCLUDED.{col}" for col in columns if col != primary_key
        ]
        update_str = ", ".join(update_cols)

        query = f"""
            INSERT INTO raw.{table_name} ({columns_str})
            VALUES %s
            ON CONFLICT ({primary_key})
            DO UPDATE SET {update_str}
        """

        # Prepare values
        values = [tuple(row.get(col) for col in columns) for row in rows]

        try:
            with self._connection.cursor() as cursor:
                execute_values(cursor, query, values, page_size=1000)
                self._connection.commit()
                logger.debug("Upserted batch", table=table_name, rows=len(rows))
                return len(rows)
        except Exception as e:
            self._connection.rollback()
            logger.error("Failed to upsert batch", table=table_name, error=str(e))
            raise

    def load_table(
        self,
        table_name: str,
        rows: List[Dict[str, Any]],
        batch_size: int = 1000,
        primary_key: str = "id",
    ) -> int:
        """
        Load all rows to a target table in batches.

        Args:
            table_name: Name of the target table
            rows: List of all rows to load
            batch_size: Number of rows per batch
            primary_key: Name of the primary key column

        Returns:
            Total number of rows loaded
        """
        if not rows:
            logger.info("No rows to load", table=table_name)
            return 0

        logger.info(
            "Starting load",
            table=table_name,
            total_rows=len(rows),
            batch_size=batch_size,
        )

        total_loaded = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            loaded = self.upsert_batch(table_name, batch, primary_key)
            total_loaded += loaded

        logger.info("Load complete", table=table_name, total_loaded=total_loaded)

        return total_loaded

    def truncate_table(self, table_name: str) -> None:
        """
        Truncate a table (for full refresh).

        Args:
            table_name: Name of the table to truncate
        """
        if not self._connection:
            raise RuntimeError("Not connected to database")

        with self._connection.cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE raw.{table_name}")
            self._connection.commit()
            logger.info("Truncated table", table=table_name)
