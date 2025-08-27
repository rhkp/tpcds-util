"""Simple integration tests with SQLite that work with existing API."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.adapters.sqlite_adapter import SQLiteOracleAdapter
from tpcds_util.generator import DataGenerator
from tpcds_util.synthetic_generator import create_synthetic_data


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for output files."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sqlite_adapter():
    """Create SQLite adapter for testing."""
    return SQLiteOracleAdapter()


class TestSQLiteIntegration:
    """Simple integration tests using SQLite backend."""

    def test_sqlite_adapter_basic_functionality(self, sqlite_adapter):
        """Test basic SQLite adapter functionality."""
        # Test database creation
        conn = sqlite_adapter.create_test_database()

        # Test basic SQL operations
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO test VALUES (1, 'test')")
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchone()

        assert result == (1, "test")
        conn.close()

    def test_sql_adaptation(self, sqlite_adapter):
        """Test Oracle to SQLite SQL adaptation."""
        oracle_sql = "CREATE TABLE test (id NUMBER, name VARCHAR2(50))"
        sqlite_sql = sqlite_adapter.adapt_schema_sql(oracle_sql)

        # Verify Oracle types were converted
        assert "NUMBER" not in sqlite_sql.upper()
        assert "VARCHAR2" not in sqlite_sql.upper()
        assert "INTEGER" in sqlite_sql.upper() or "VARCHAR" in sqlite_sql.upper()

    def test_tpcds_schema_creation(self, sqlite_adapter):
        """Test TPC-DS schema creation in SQLite."""
        conn = sqlite_adapter.create_test_database()
        sqlite_adapter.load_tpcds_schema(conn)

        # Verify tables were created
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        table_names = [table[0].lower() for table in tables]
        expected_tables = ["customer", "item", "store", "date_dim"]

        for expected_table in expected_tables:
            assert expected_table in table_names

        conn.close()

    def test_mock_oracle_connection(self, sqlite_adapter):
        """Test mock Oracle connection functionality."""
        mock_conn = sqlite_adapter.create_mock_connection()

        # Test basic operations
        assert mock_conn.ping() is True

        cursor = mock_conn.cursor()
        cursor.execute("CREATE TABLE test_table (id INTEGER, value TEXT)")
        cursor.execute("INSERT INTO test_table VALUES (1, 'test')")
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()

        assert result == (1, "test") or result == (
            1,
            "TEST",
        )  # SQLite may uppercase strings
        mock_conn.close()

    def test_data_generator_with_sqlite_validation(
        self, temp_output_dir, sqlite_adapter
    ):
        """Test data generator with SQLite validation."""
        # Generate synthetic data using test mode for fast execution
        result = create_synthetic_data(scale=0, output_dir=str(temp_output_dir))
        assert result is True

        # Verify files were created
        data_files = list(temp_output_dir.glob("*.dat"))
        assert len(data_files) > 0

        # Test loading one file into SQLite for validation
        customer_file = temp_output_dir / "customer.dat"
        if customer_file.exists():
            conn = sqlite_adapter.create_test_database()
            sqlite_adapter.load_tpcds_schema(conn)

            # Load first few lines of customer data
            cursor = conn.cursor()
            with open(customer_file, "r") as f:
                for i, line in enumerate(f):
                    if i >= 5:  # Only test first 5 lines
                        break

                    fields = line.strip().split("|")[:-1]  # Remove trailing empty field
                    if len(fields) >= 18:
                        # Pad or truncate to match customer table structure
                        while len(fields) < 18:
                            fields.append("")
                        fields = fields[:18]

                        try:
                            placeholders = ",".join(["?" for _ in range(18)])
                            cursor.execute(
                                f"INSERT INTO customer VALUES ({placeholders})", fields
                            )
                        except Exception:
                            # Skip invalid records for this test
                            continue

            conn.commit()

            # Verify some data was loaded
            cursor.execute("SELECT COUNT(*) FROM customer")
            count = cursor.fetchone()[0]
            assert count > 0

            conn.close()

    @patch("tpcds_util.config.config_manager")
    def test_data_generator_api_compatibility(
        self, mock_config_manager, temp_output_dir
    ):
        """Test DataGenerator API compatibility."""
        # Mock the config manager
        from tpcds_util.config import DatabaseConfig, TPCDSConfig

        mock_config = TPCDSConfig(
            database=DatabaseConfig(),
            default_output_dir=str(temp_output_dir),
            default_scale=1,
        )
        mock_config_manager.load.return_value = mock_config

        # Test DataGenerator using test mode for fast execution
        generator = DataGenerator()
        result = generator.generate_data(scale=0, output_dir=str(temp_output_dir))

        assert result is True

        # Verify files were created
        data_files = list(temp_output_dir.glob("*.dat"))
        assert len(data_files) > 0

    def test_file_format_validation(self, temp_output_dir):
        """Test generated file format validation."""
        # Generate data using test mode for fast execution
        result = create_synthetic_data(scale=0, output_dir=str(temp_output_dir))
        assert result is True

        # Check file formats
        for data_file in temp_output_dir.glob("*.dat"):
            with open(data_file, "r") as f:
                lines = f.readlines()

                if len(lines) > 0:
                    # Check TPC-DS format (pipe-delimited)
                    first_line = lines[0].strip()
                    assert "|" in first_line
                    assert first_line.endswith("|")

                    # Check field count is reasonable
                    fields = first_line.split("|")
                    assert (
                        len(fields) >= 3
                    )  # Should have multiple fields (some tables like income_band have few fields)

    def test_data_quality_basic_checks(self, temp_output_dir, sqlite_adapter):
        """Test basic data quality checks."""
        # Generate small dataset using test mode for fast execution
        result = create_synthetic_data(scale=0, output_dir=str(temp_output_dir))
        assert result is True

        # Check customer data quality if available
        customer_file = temp_output_dir / "customer.dat"
        if customer_file.exists():
            conn = sqlite_adapter.create_test_database()
            cursor = conn.cursor()

            # Create simplified customer table for testing
            cursor.execute(
                """
                CREATE TABLE customer_test (
                    c_customer_sk INTEGER,
                    c_customer_id TEXT,
                    c_first_name TEXT,
                    c_last_name TEXT
                )
            """
            )

            # Load sample data
            with open(customer_file, "r") as f:
                for i, line in enumerate(f):
                    if i >= 10:  # Test first 10 records
                        break

                    fields = line.strip().split("|")
                    if len(fields) >= 9:  # Has enough fields
                        try:
                            cursor.execute(
                                "INSERT INTO customer_test VALUES (?, ?, ?, ?)",
                                (fields[0], fields[1], fields[7], fields[8]),
                            )
                        except Exception:
                            continue

            conn.commit()

            # Basic quality checks
            cursor.execute(
                "SELECT COUNT(*) FROM customer_test WHERE c_customer_sk IS NOT NULL"
            )
            valid_sks = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM customer_test")
            total_records = cursor.fetchone()[0]

            if total_records > 0:
                # At least 80% should have valid SKs
                quality_ratio = valid_sks / total_records
                assert quality_ratio >= 0.8

            conn.close()


class TestSQLitePerformance:
    """Test performance aspects of SQLite integration."""

    def test_data_generation_performance(self, temp_output_dir):
        """Test that data generation completes in reasonable time."""
        import time

        start_time = time.time()
        result = create_synthetic_data(scale=0, output_dir=str(temp_output_dir))
        generation_time = time.time() - start_time

        assert result is True
        assert generation_time < 5  # Test mode should complete within 5 seconds

    def test_scale_modes_functionality(self, temp_output_dir):
        """Test that scale=0 (test mode) works correctly."""
        # Test scale=0 (test mode) only - fast execution for CI/CD
        test_dir_0 = temp_output_dir / "scale_0"
        result_0 = create_synthetic_data(scale=0, output_dir=str(test_dir_0))
        assert result_0 is True

        files_0 = list(test_dir_0.glob("*.dat"))
        assert len(files_0) >= 10  # Should have essential tables
        assert len(files_0) <= 15  # Should be limited for test mode

        # Verify test mode generates small files
        customer_0 = test_dir_0 / "customer.dat"
        if customer_0.exists():
            with open(customer_0, "r") as f:
                line_count = len(f.readlines())
            assert line_count <= 10  # Test mode should have very few records

    def test_sqlite_operations_performance(self, sqlite_adapter):
        """Test SQLite operations performance."""
        import time

        conn = sqlite_adapter.create_test_database()

        start_time = time.time()
        sqlite_adapter.load_tpcds_schema(conn)
        schema_time = time.time() - start_time

        assert schema_time < 5  # Schema creation should be fast

        # Test bulk insert performance
        cursor = conn.cursor()
        start_time = time.time()

        for i in range(1000):
            cursor.execute(
                "INSERT INTO customer VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [i, f"CUSTOMER{i:06d}"] + [""] * 16,
            )

        conn.commit()
        insert_time = time.time() - start_time

        assert insert_time < 5  # 1000 inserts should complete within 5 seconds

        conn.close()


class TestSQLiteErrorHandling:
    """Test error handling in SQLite integration."""

    def test_invalid_sql_handling(self, sqlite_adapter):
        """Test handling of invalid SQL."""
        conn = sqlite_adapter.create_test_database()
        cursor = conn.cursor()

        # Test invalid SQL
        with pytest.raises(Exception):
            cursor.execute("INVALID SQL STATEMENT")

        conn.close()

    def test_data_generation_error_recovery(self):
        """Test error recovery in data generation."""
        # Test with invalid output directory (using test mode for speed)
        result = create_synthetic_data(scale=0, output_dir="/invalid/nonexistent/path")
        assert result is False

    def test_sql_adaptation_edge_cases(self, sqlite_adapter):
        """Test SQL adaptation with edge cases."""
        # Test empty SQL
        result = sqlite_adapter.adapt_schema_sql("")
        assert result == ""

        # Test SQL with complex Oracle constructs
        complex_sql = (
            "CREATE TABLE test (id NUMBER(10,2), data VARCHAR2(4000) DEFAULT SYSDATE)"
        )
        adapted_sql = sqlite_adapter.adapt_schema_sql(complex_sql)

        # Should not contain Oracle-specific elements
        assert "NUMBER(10,2)" not in adapted_sql
        assert "VARCHAR2(4000)" not in adapted_sql
        assert "SYSDATE" not in adapted_sql
