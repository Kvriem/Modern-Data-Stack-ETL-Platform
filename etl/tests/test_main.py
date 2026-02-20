"""
Unit tests for the ETL main module.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.main import run_etl
from src.config import ETLConfig


class TestMainETL:
    """Tests for main ETL orchestration."""

    @patch('src.main.Extractor')
    @patch('src.main.Loader')
    def test_run_etl_success(self, mock_loader_class, mock_extractor_class, mock_etl_config):
        """Test successful ETL run."""
        # Setup mocks
        mock_extractor = MagicMock()
        mock_loader = MagicMock()
        mock_extractor_class.return_value.__enter__.return_value = mock_extractor
        mock_loader_class.return_value.__enter__.return_value = mock_loader
        
        # Mock watermark and extraction
        mock_loader.get_watermark.return_value = None
        mock_extractor.extract_full_table.return_value = [
            {'id': 1, 'name': 'test1'},
            {'id': 2, 'name': 'test2'}
        ]
        mock_loader.load_data.return_value = 2
        
        # Run ETL
        result = run_etl(config=mock_etl_config, tables=['test_table'])
        
        # Assertions
        assert result['status'] == 'success'
        assert 'test_table' in result['tables']
        mock_extractor.extract_full_table.assert_called_once()
        mock_loader.load_data.assert_called_once()

    @patch('src.main.Extractor')
    @patch('src.main.Loader')
    def test_run_etl_no_new_rows(self, mock_loader_class, mock_extractor_class, mock_etl_config):
        """Test ETL run with no new rows."""
        # Setup mocks
        mock_extractor = MagicMock()
        mock_loader = MagicMock()
        mock_extractor_class.return_value.__enter__.return_value = mock_extractor
        mock_loader_class.return_value.__enter__.return_value = mock_loader
        
        # Mock no new data
        mock_loader.get_watermark.return_value = None
        mock_extractor.extract_full_table.return_value = []
        
        # Run ETL
        result = run_etl(config=mock_etl_config, tables=['test_table'])
        
        # Assertions
        assert result['status'] == 'success'
        assert result['tables']['test_table']['status'] == 'skipped'
        mock_loader.load_data.assert_not_called()

    @patch('src.main.Extractor')
    @patch('src.main.Loader')
    def test_run_etl_with_watermark(self, mock_loader_class, mock_extractor_class, mock_etl_config):
        """Test ETL run with incremental watermark."""
        from datetime import datetime
        
        # Setup mocks
        mock_extractor = MagicMock()
        mock_loader = MagicMock()
        mock_extractor_class.return_value.__enter__.return_value = mock_extractor
        mock_loader_class.return_value.__enter__.return_value = mock_loader
        
        # Mock watermark exists
        watermark = datetime(2026, 1, 1)
        mock_loader.get_watermark.return_value = watermark
        mock_extractor.extract_full_table.return_value = [{'id': 1}]
        mock_loader.load_data.return_value = 1
        
        # Run ETL with incremental load
        result = run_etl(config=mock_etl_config, tables=['test_table'], full_refresh=False)
        
        # Verify watermark was used
        mock_extractor.extract_full_table.assert_called_once_with('test_table', watermark=watermark)

    @patch('src.main.Extractor')
    @patch('src.main.Loader')
    def test_run_etl_full_refresh(self, mock_loader_class, mock_extractor_class, mock_etl_config):
        """Test ETL run with full refresh (ignore watermark)."""
        # Setup mocks
        mock_extractor = MagicMock()
        mock_loader = MagicMock()
        mock_extractor_class.return_value.__enter__.return_value = mock_extractor
        mock_loader_class.return_value.__enter__.return_value = mock_loader
        
        mock_extractor.extract_full_table.return_value = [{'id': 1}]
        mock_loader.load_data.return_value = 1
        
        # Run ETL with full refresh
        result = run_etl(config=mock_etl_config, tables=['test_table'], full_refresh=True)
        
        # Verify watermark was not retrieved
        mock_loader.get_watermark.assert_not_called()
        # Verify extraction called with no watermark
        mock_extractor.extract_full_table.assert_called_once_with('test_table', watermark=None)
