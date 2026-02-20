"""
Unit tests for the ETL configuration module.
"""

import os
import pytest
from src.config import DatabaseConfig, ETLConfig


class TestDatabaseConfig:
    """Tests for DatabaseConfig class."""

    def test_database_config_creation(self):
        """Test creating a database configuration."""
        config = DatabaseConfig(
            host='localhost',
            port=5432,
            name='test_db',
            user='test_user',
            password='test_password'
        )
        
        assert config.host == 'localhost'
        assert config.port == 5432
        assert config.name == 'test_db'
        assert config.user == 'test_user'
        assert config.password == 'test_password'

    def test_psycopg2_params(self):
        """Test psycopg2 connection parameters."""
        config = DatabaseConfig(
            host='localhost',
            port=5432,
            name='test_db',
            user='test_user',
            password='test_password'
        )
        
        params = config.psycopg2_params
        
        assert params['host'] == 'localhost'
        assert params['port'] == 5432
        assert params['dbname'] == 'test_db'
        assert params['user'] == 'test_user'
        assert params['password'] == 'test_password'


class TestETLConfig:
    """Tests for ETLConfig class."""

    def test_etl_config_creation(self):
        """Test creating an ETL configuration."""
        source = DatabaseConfig(
            host='source',
            port=5432,
            name='source_db',
            user='source_user',
            password='source_pass'
        )
        
        target = DatabaseConfig(
            host='target',
            port=5432,
            name='target_db',
            user='target_user',
            password='target_pass'
        )
        
        config = ETLConfig(source_db=source, target_db=target)
        
        assert config.source_db.host == 'source'
        assert config.target_db.host == 'target'

    def test_from_env_missing_vars(self):
        """Test from_env raises error when environment variables are missing."""
        # Clear relevant environment variables
        for key in ['SOURCE_DB_HOST', 'TARGET_DB_HOST']:
            if key in os.environ:
                del os.environ[key]
        
        with pytest.raises((KeyError, ValueError)):
            ETLConfig.from_env()
