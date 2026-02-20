"""
Pytest configuration and fixtures for ETL tests.
"""

import pytest
from unittest.mock import MagicMock
from src.config import DatabaseConfig, ETLConfig


@pytest.fixture
def mock_db_config():
    """Create a mock database configuration."""
    return DatabaseConfig(
        host='localhost',
        port=5432,
        name='test_db',
        user='test_user',
        password='test_password'
    )


@pytest.fixture
def mock_etl_config(mock_db_config):
    """Create a mock ETL configuration."""
    return ETLConfig(
        source_db=mock_db_config,
        target_db=mock_db_config
    )


@pytest.fixture
def mock_connection():
    """Create a mock database connection."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_conn, mock_cursor
