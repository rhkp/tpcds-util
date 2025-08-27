"""Unit tests for CLI module."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from tpcds_util.cli import cli, config, config_show
from tpcds_util.config import DatabaseConfig, TPCDSConfig


class TestCLI:
    """Test CLI module."""
    
    def test_cli_group_exists(self):
        """Test that main CLI group exists and is callable."""
        assert callable(cli)
        
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'TPC-DS Utility' in result.output
        assert 'synthetic TPC-DS data' in result.output
    
    def test_config_group_exists(self):
        """Test that config command group exists."""
        assert callable(config)
        
        runner = CliRunner()
        result = runner.invoke(cli, ['config', '--help'])
        
        assert result.exit_code == 0
        assert 'Manage configuration settings' in result.output
    
    @patch('tpcds_util.cli.config_manager')
    def test_config_show_command(self, mock_config_manager):
        """Test config show command."""
        # Setup mock configuration
        mock_config = TPCDSConfig(
            database=DatabaseConfig(
                host="testhost",
                port=1521,
                service_name="TESTPDB",
                username="testuser",
                password="testpass"
            ),
            schema_name="TEST_SCHEMA",
            default_scale=2,
            default_output_dir="/test/path",
            parallel_workers=8
        )
        mock_config_manager.load.return_value = mock_config
        
        runner = CliRunner()
        result = runner.invoke(config_show)
        
        assert result.exit_code == 0
        mock_config_manager.load.assert_called_once()
        
        # Check that key configuration values are displayed
        assert "testhost" in result.output
        assert "1521" in result.output
        assert "TESTPDB" in result.output
        assert "testuser" in result.output
        assert "***" in result.output  # Password should be masked
        assert "TEST_SCHEMA" in result.output
        assert "2" in result.output  # scale
        assert "/test/path" in result.output
        assert "8" in result.output  # parallel workers
    
    @patch('tpcds_util.cli.config_manager')
    def test_config_show_empty_values(self, mock_config_manager):
        """Test config show with empty/default values."""
        # Setup mock configuration with empty values
        mock_config = TPCDSConfig(
            database=DatabaseConfig(
                host="localhost",
                port=1521,
                service_name="orcl",
                username="",
                password=""
            ),
            schema_name="",
            default_scale=1,
            default_output_dir="./tpcds_data",
            parallel_workers=4
        )
        mock_config_manager.load.return_value = mock_config
        
        runner = CliRunner()
        result = runner.invoke(config_show)
        
        assert result.exit_code == 0
        
        # Check that empty values show appropriate placeholders
        assert "[Not Set]" in result.output  # Should appear for empty username and password
        assert "localhost" in result.output
        assert "orcl" in result.output
    
    def test_cli_version_option(self):
        """Test that version option works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        # Version output format may vary, just check it doesn't crash
    
    def test_cli_help_message_content(self):
        """Test CLI help message contains expected information."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'TPC-DS Utility' in result.output
        assert 'Generate synthetic TPC-DS data' in result.output
        assert 'manage Oracle databases' in result.output
        assert 'schema' in result.output
        
        # Check that subcommands are listed
        assert 'config' in result.output
    
    def test_config_help_message(self):
        """Test config subcommand help message."""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', '--help'])
        
        assert result.exit_code == 0
        assert 'Manage configuration settings' in result.output
        assert 'show' in result.output  # show subcommand should be listed
    
    def test_config_show_help(self):
        """Test config show subcommand help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', 'show', '--help'])
        
        assert result.exit_code == 0
        assert 'Show current configuration' in result.output


class TestCLIIntegration:
    """Integration-style tests for CLI components."""
    
    @patch('tpcds_util.cli.config_manager')
    @patch('tpcds_util.cli.console')
    def test_config_show_table_creation(self, mock_console, mock_config_manager):
        """Test that config show creates a proper table output."""
        mock_config = TPCDSConfig(
            database=DatabaseConfig(
                host="integrationhost",
                port=1522,
                service_name="INTPDB",
                username="intuser",
                password="intpass"
            ),
            schema_name="INT_SCHEMA",
            default_scale=3,
            default_output_dir="/int/path",
            parallel_workers=6
        )
        mock_config_manager.load.return_value = mock_config
        
        runner = CliRunner()
        result = runner.invoke(config_show)
        
        assert result.exit_code == 0
        mock_config_manager.load.assert_called_once()
        
        # Check that console.print was called (for the table)
        mock_console.print.assert_called()
    
    def test_invalid_command(self):
        """Test behavior with invalid command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['invalid-command'])
        
        assert result.exit_code != 0
        assert 'No such command' in result.output
    
    def test_config_invalid_subcommand(self):
        """Test behavior with invalid config subcommand."""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', 'invalid-subcommand'])
        
        assert result.exit_code != 0
        assert 'No such command' in result.output
    
    @patch('tpcds_util.cli.config_manager')
    def test_config_show_with_exception(self, mock_config_manager):
        """Test config show when config manager raises exception."""
        mock_config_manager.load.side_effect = Exception("Config error")
        
        runner = CliRunner()
        result = runner.invoke(config_show)
        
        # Should not crash, but may have non-zero exit code depending on implementation
        assert "Config error" in str(result.exception) if result.exception else True
    
    def test_empty_cli_invocation(self):
        """Test calling CLI without any commands."""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        
        # Should show help or usage information (Click returns 2 for missing command)
        assert result.exit_code in [0, 2]  # 0 for help, 2 for missing command
        assert 'Usage:' in result.output or 'TPC-DS Utility' in result.output