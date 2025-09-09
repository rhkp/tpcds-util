"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from tpcds_util.config import ConfigManager, DatabaseConfig, TPCDSConfig
from tpcds_util.synthetic_generator import DataGenerationConfig


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_database_config():
    """Create a mock database configuration."""
    return DatabaseConfig(
        host="test-host",
        port=1521,
        service_name="TESTPDB",
        username="testuser",
        password="testpass",
        use_sid=False,
    )


@pytest.fixture
def mock_tpcds_config(mock_database_config):
    """Create a mock TPC-DS configuration."""
    return TPCDSConfig(
        database=mock_database_config,
        schema_name="TEST_SCHEMA",
        default_scale=2,
        default_output_dir="/test/output",
        parallel_workers=4,
    )


@pytest.fixture
def mock_config_manager(mock_tpcds_config, temp_config_dir):
    """Create a mock config manager."""
    config_path = temp_config_dir / "test_config.yaml"
    manager = ConfigManager(config_path=config_path)
    manager._config = mock_tpcds_config
    return manager


@pytest.fixture
def mock_data_generation_config():
    """Create a mock data generation configuration."""
    return DataGenerationConfig(
        scale_factor=1,
        num_customers=1000,
        num_items=100,
        num_stores=2,
        num_warehouses=1,
    )


@pytest.fixture
def mock_console():
    """Create a mock console for testing rich output."""
    with patch("tpcds_util.generator.console") as mock:
        yield mock


@pytest.fixture
def mock_click_echo():
    """Create a mock click.echo for testing CLI output."""
    with patch("click.echo") as mock:
        yield mock


@pytest.fixture(autouse=True)
def reset_global_config():
    """Reset global config manager state between tests."""
    from tpcds_util.config import config_manager

    config_manager._config = None
    yield
    config_manager._config = None


@pytest.fixture
def mock_faker():
    """Create a mock Faker instance."""
    faker_mock = Mock()
    faker_mock.name.return_value = "Test Name"
    faker_mock.address.return_value = "123 Test St"
    faker_mock.email.return_value = "test@example.com"
    faker_mock.phone_number.return_value = "555-1234"
    faker_mock.company.return_value = "Test Company"
    return faker_mock


# Pytest markers for test categorization
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
pytest.mark.oracle = pytest.mark.oracle
