"""
Unit tests for the ETL extract module.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.extract import Extractor


class TestExtractor:
    """Tests for Extractor class."""

    def test_extractor_initialization(self, mock_db_config):
        """Test extractor initialization."""
        extractor = Extractor(mock_db_config)
        
        assert extractor.config == mock_db_config
        assert extractor._connection is None

    @patch('src.extract.psycopg2.connect')
    def test_connect(self, mock_connect, mock_db_config):
        """Test database connection."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        extractor = Extractor(mock_db_config)
        extractor.connect()
        
        assert extractor._connection == mock_connection
        mock_connect.assert_called_once()

    def test_disconnect(self, mock_db_config):
        """Test database disconnection."""
        extractor = Extractor(mock_db_config)
        mock_connection = MagicMock()
        extractor._connection = mock_connection
        
        extractor.disconnect()
        
        mock_connection.close.assert_called_once()
        assert extractor._connection is None

    @patch('src.extract.psycopg2.connect')
    def test_context_manager(self, mock_connect, mock_db_config):
        """Test extractor as context manager."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        with Extractor(mock_db_config) as extractor:
            assert extractor._connection == mock_connection
        
        mock_connection.close.assert_called_once()

    def test_get_row_count_not_connected(self, mock_db_config):
        """Test get_row_count raises error when not connected."""
        extractor = Extractor(mock_db_config)
        
        with pytest.raises(RuntimeError, match="Not connected"):
            extractor.get_row_count('test_table')

    def test_get_row_count(self, mock_db_config):
        """Test getting row count."""
        extractor = Extractor(mock_db_config)
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (100,)
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        extractor._connection = mock_connection
        
        count = extractor.get_row_count('test_table')
        
        assert count == 100
        mock_cursor.execute.assert_called_once()

    def test_get_row_count_with_watermark(self, mock_db_config):
        """Test getting row count with watermark."""
        extractor = Extractor(mock_db_config)
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (50,)
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        extractor._connection = mock_connection
        
        watermark = datetime(2026, 1, 1)
        count = extractor.get_row_count('test_table', watermark=watermark)
        
        assert count == 50
        # Verify watermark was used in query
        call_args = mock_cursor.execute.call_args
        assert 'WHERE updated_at >' in call_args[0][0]

    def test_extract_table_not_connected(self, mock_db_config):
        """Test extract_table raises error when not connected."""
        extractor = Extractor(mock_db_config)
        
        with pytest.raises(RuntimeError, match="Not connected"):
            list(extractor.extract_table('test_table'))
