"""
ETL Extract Module

Handles data extraction from the source database with incremental loading support.
"""

import structlog
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Generator, Dict, Any, List, Optional
from datetime import datetime

from .config import DatabaseConfig

logger = structlog.get_logger(__name__)


class Extractor:
    """Handles data extraction from source database."""

    def __init__(self, config: DatabaseConfig):
        """
        Initialize extractor with database configuration.

        Args:
            config: Source database configuration
        """
        self.config = config
        self._connection: Optional[psycopg2.extensions.connection] = None

    def connect(self) -> None:
        """Establish connection to source database."""
        logger.info(
            "Connecting to source database", host=self.config.host, db=self.config.name
        )
        self._connection = psycopg2.connect(**self.config.psycopg2_params)
        logger.info("Connected to source database successfully")

    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Disconnected from source database")

    def __enter__(self) -> "Extractor":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()

    def get_row_count(
        self, table_name: str, watermark: Optional[datetime] = None
    ) -> int:
        """
        Get count of rows to extract.

        Args:
            table_name: Name of the table
            watermark: Optional timestamp for incremental extraction

        Returns:
            Number of rows matching criteria
        """
        if not self._connection:
            raise RuntimeError("Not connected to database")

        with self._connection.cursor() as cursor:
            if watermark:
                query = f"SELECT COUNT(*) FROM {table_name} WHERE updated_at > %s"
                cursor.execute(query, (watermark,))
            else:
                query = f"SELECT COUNT(*) FROM {table_name}"
                cursor.execute(query)

            result = cursor.fetchone()
            return result[0] if result else 0

    def extract_table(
        self,
        table_name: str,
        batch_size: int = 1000,
        watermark: Optional[datetime] = None,
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Extract data from a table in batches.

        Args:
            table_name: Name of the table to extract
            batch_size: Number of rows per batch
            watermark: Optional timestamp for incremental extraction

        Yields:
            Batches of rows as dictionaries
        """
        if not self._connection:
            raise RuntimeError("Not connected to database")

        total_rows = self.get_row_count(table_name, watermark)
        logger.info(
            "Starting extraction",
            table=table_name,
            total_rows=total_rows,
            batch_size=batch_size,
            incremental=watermark is not None,
        )

        with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
            if watermark:
                query = f"""
                    SELECT * FROM {table_name}
                    WHERE updated_at > %s
                    ORDER BY updated_at ASC
                """
                cursor.execute(query, (watermark,))
            else:
                query = f"SELECT * FROM {table_name} ORDER BY id"
                cursor.execute(query)

            batch_num = 0
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break

                batch_num += 1
                logger.debug(
                    "Extracted batch",
                    table=table_name,
                    batch_num=batch_num,
                    rows_in_batch=len(rows),
                )
                yield [dict(row) for row in rows]

        logger.info(
            "Extraction complete",
            table=table_name,
            total_batches=batch_num,
            total_rows=total_rows,
        )

    def extract_full_table(
        self, table_name: str, watermark: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract all data from a table at once.

        Args:
            table_name: Name of the table to extract
            watermark: Optional timestamp for incremental extraction

        Returns:
            List of all rows as dictionaries
        """
        all_rows = []
        for batch in self.extract_table(
            table_name, batch_size=10000, watermark=watermark
        ):
            all_rows.extend(batch)
        return all_rows

    def get_max_updated_at(self, table_name: str) -> Optional[datetime]:
        """
        Get the maximum updated_at value for a table.

        Args:
            table_name: Name of the table

        Returns:
            Maximum updated_at timestamp or None if table is empty
        """
        if not self._connection:
            raise RuntimeError("Not connected to database")

        with self._connection.cursor() as cursor:
            query = f"SELECT MAX(updated_at) FROM {table_name}"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
