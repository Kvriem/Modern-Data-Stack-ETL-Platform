"""
ETL Configuration Module

Handles environment variables and database connection settings.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    host: str
    port: int
    name: str
    user: str
    password: str

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def psycopg2_params(self) -> dict:
        """Generate psycopg2 connection parameters."""
        return {
            "host": self.host,
            "port": self.port,
            "dbname": self.name,
            "user": self.user,
            "password": self.password,
        }


@dataclass
class ETLConfig:
    """Main ETL configuration."""
    source_db: DatabaseConfig
    target_db: DatabaseConfig
    batch_size: int = 1000
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "ETLConfig":
        """Create configuration from environment variables."""
        source_db = DatabaseConfig(
            host=os.getenv("SOURCE_DB_HOST", "localhost"),
            port=int(os.getenv("SOURCE_DB_PORT", "5432")),
            name=os.getenv("SOURCE_DB_NAME", "source_oltp"),
            user=os.getenv("SOURCE_DB_USER", "source_user"),
            password=os.getenv("SOURCE_DB_PASSWORD", ""),
        )

        target_db = DatabaseConfig(
            host=os.getenv("TARGET_DB_HOST", "localhost"),
            port=int(os.getenv("TARGET_DB_PORT", "5432")),
            name=os.getenv("TARGET_DB_NAME", "target_dwh"),
            user=os.getenv("TARGET_DB_USER", "target_user"),
            password=os.getenv("TARGET_DB_PASSWORD", ""),
        )

        return cls(
            source_db=source_db,
            target_db=target_db,
            batch_size=int(os.getenv("ETL_BATCH_SIZE", "1000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


# Tables to process in ETL
ETL_TABLES = [
    "customers",
    "products",
    "orders",
    "order_items",
]
