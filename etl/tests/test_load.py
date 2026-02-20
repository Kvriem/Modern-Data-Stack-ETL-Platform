"""
Unit tests for the ETL load module.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.load import Loader


class TestLoader:
    """Tests for Loader class."""

    def test_loader_initialization(self, mock_db_config):
        """Test loader initialization."""
        loader = Loader(mock_db_config)
        
        assert loader.config == mock_db_config
        assert loader._connection is None

    @patch('src.load.psycopg2.connect')
    def test_connect(self, mock_connect, mock_db_config):
        """Test database connection."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        loader = Loader(mock_db_config)
        loader.connect()
        
        assert loader._connection == mock_connection
        mock_connect.assert_called_once()

    def test_disconnect(self, mock_db_config):
        """Test database disconnection."""
        loader = Loader(mock_db_config)
        mock_connection = MagicMock()
        loader._connection = mock_connection
        
        loader.disconnect()
        
        mock_connection.close.assert_called_once()
        assert loader._connection is None

    @patch('src.load.psycopg2.connect')
    def test_context_manager(self, mock_connect, mock_db_config):
        """Test loader as context manager."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        with Loader(mock_db_config) as loader:
            assert loader._connection == mock_connection
        
        mock_connection.close.assert_called_once()

    def test_get_watermark_not_connected(self, mock_db_config):
        """Test get_watermark raises error when not connected."""
        loader = Loader(mock_db_config)
        
        with pytest.raises(RuntimeError, match="Not connected"):
            loader.get_watermark('test_table')

    def test_get_watermark(self, mock_db_config):
        """Test getting watermark."""
        loader = Loader(mock_db_config)
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        test_date = datetime(2026, 1, 1)
        mock_cursor.fetchone.return_value = (test_date,)
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        loader._connection = mock_connection
        
        watermark = loader.get_watermark('test_table')
        
        assert watermark == test_date
        mock_cursor.execute.assert_called_once()

    def test_get_watermark_none(self, mock_db_config):
        """Test getting watermark when none exists."""
        loader = Loader(mock_db_config)
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        loader._connection = mock_connection
        
        watermark = loader.get_watermark('test_table')
        
        assert watermark is None

    def test_update_watermark_not_connected(self, mock_db_config):
        """Test update_watermark raises error when not connected."""
        loader = Loader(mock_db_config)
        
        with pytest.raises(RuntimeError, match="Not connected"):
            loader.update_watermark('test_table', datetime.now(), 100)

    def test_update_watermark(self, mock_db_config):
        """Test updating watermark."""
        loader = Loader(mock_db_config)
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        loader._connection = mock_connection
        
        test_date = datetime(2026, 1, 1)
        loader.update_watermark('test_table', test_date, 100)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
