"""SQLite adapter for Oracle database testing."""

import sqlite3
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile


class SQLiteOracleAdapter:
    """Adapts Oracle-specific SQL to SQLite for testing."""

    def __init__(self):
        self.type_mappings = {
            "VARCHAR2": "VARCHAR",
            "NUMBER": "INTEGER",
            "NUMBER(\\d+,\\d+)": "REAL",  # NUMBER(10,2) -> REAL
            "NUMBER(\\d+)": "INTEGER",  # NUMBER(10) -> INTEGER
            "CLOB": "TEXT",
            "BLOB": "BLOB",
            "TIMESTAMP": "TEXT",
            "DATE": "TEXT",
            "CHAR": "TEXT",
            "NVARCHAR2": "VARCHAR",
            "NCHAR": "TEXT",
        }

        self.function_mappings = {
            "SYSDATE": 'datetime("now")',
            "SYSTIMESTAMP": 'datetime("now")',
            "USER": '"testuser"',
            "DUAL": "(SELECT 1 as dummy)",
            "ROWNUM": "rowid",
            "NVL": "COALESCE",
            "TO_CHAR": "CAST",
            "TO_NUMBER": "CAST",
        }

    def adapt_schema_sql(self, oracle_sql: str) -> str:
        """Convert Oracle DDL to SQLite-compatible SQL."""
        sql = oracle_sql.upper()

        # Handle data types
        for oracle_type, sqlite_type in self.type_mappings.items():
            if "(" in oracle_type:  # Regex pattern
                sql = re.sub(oracle_type, sqlite_type, sql)
            else:
                # Use word boundaries to avoid replacing parts of table names
                sql = re.sub(r"\b" + oracle_type + r"\b", sqlite_type, sql)

        # Handle Oracle-specific functions
        for oracle_func, sqlite_func in self.function_mappings.items():
            sql = sql.replace(oracle_func, sqlite_func)

        # Remove Oracle-specific constraints and options
        sql = re.sub(r"TABLESPACE\s+\w+", "", sql)
        sql = re.sub(r"STORAGE\s*\([^)]+\)", "", sql)
        sql = re.sub(r"PCTFREE\s+\d+", "", sql)
        sql = re.sub(r"PCTUSED\s+\d+", "", sql)
        sql = re.sub(r"INITRANS\s+\d+", "", sql)
        sql = re.sub(r"MAXTRANS\s+\d+", "", sql)
        sql = re.sub(r"ENABLE\s+VALIDATE", "", sql)
        sql = re.sub(r"USING\s+INDEX", "", sql)

        # Handle sequences (SQLite uses AUTOINCREMENT)
        sql = re.sub(r"DEFAULT\s+\w+\.NEXTVAL", "PRIMARY KEY AUTOINCREMENT", sql)

        # Remove schema prefixes
        sql = re.sub(r"\w+\.(\w+)", r"\1", sql)

        # Clean up extra whitespace
        sql = re.sub(r"\s+", " ", sql).strip()

        return sql

    def create_test_database(self, in_memory: bool = True) -> sqlite3.Connection:
        """Create SQLite database for testing."""
        if in_memory:
            conn = sqlite3.connect(":memory:")
        else:
            # Create temporary file-based database
            temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
            conn = sqlite3.connect(temp_file.name)

        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")

        # Set SQLite to be more Oracle-like
        conn.execute("PRAGMA case_sensitive_like = ON")

        return conn

    def load_tpcds_schema(
        self, conn: sqlite3.Connection, schema_file_path: Optional[str] = None
    ) -> None:
        """Load TPC-DS schema into SQLite database."""
        if schema_file_path is None:
            schema_file_path = (
                Path(__file__).parent.parent.parent / "oracle_tpcds_schema.sql"
            )

        if not Path(schema_file_path).exists():
            # Create a minimal TPC-DS schema for testing
            self._create_minimal_tpcds_schema(conn)
            return

        with open(schema_file_path, "r") as f:
            oracle_sql = f.read()

        # Split into individual statements
        statements = [stmt.strip() for stmt in oracle_sql.split(";") if stmt.strip()]

        for statement in statements:
            try:
                sqlite_sql = self.adapt_schema_sql(statement)
                if sqlite_sql and not sqlite_sql.startswith("--"):
                    conn.execute(sqlite_sql)
            except sqlite3.Error as e:
                # Log but continue with other statements
                print(f"Warning: Could not execute statement: {e}")
                continue

        conn.commit()

    def _create_minimal_tpcds_schema(self, conn: sqlite3.Connection) -> None:
        """Create minimal TPC-DS schema for testing when full schema is not available."""

        # Core TPC-DS tables simplified for SQLite
        tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS date_dim (
                d_date_sk INTEGER PRIMARY KEY,
                d_date_id VARCHAR(16),
                d_date TEXT,
                d_month_seq INTEGER,
                d_week_seq INTEGER,
                d_quarter_seq INTEGER,
                d_year INTEGER,
                d_dow INTEGER,
                d_moy INTEGER,
                d_dom INTEGER,
                d_qoy INTEGER,
                d_fy_year INTEGER,
                d_fy_quarter_seq INTEGER,
                d_fy_week_seq INTEGER,
                d_day_name VARCHAR(9),
                d_quarter_name VARCHAR(6),
                d_holiday VARCHAR(1),
                d_weekend VARCHAR(1),
                d_following_holiday VARCHAR(1),
                d_first_dom INTEGER,
                d_last_dom INTEGER,
                d_same_day_ly INTEGER,
                d_same_day_lq INTEGER,
                d_current_day VARCHAR(1),
                d_current_week VARCHAR(1),
                d_current_month VARCHAR(1),
                d_current_quarter VARCHAR(1),
                d_current_year VARCHAR(1)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS customer (
                c_customer_sk INTEGER PRIMARY KEY,
                c_customer_id VARCHAR(16),
                c_current_cdemo_sk INTEGER,
                c_current_hdemo_sk INTEGER,
                c_current_addr_sk INTEGER,
                c_first_shipto_date_sk INTEGER,
                c_first_sales_date_sk INTEGER,
                c_salutation VARCHAR(10),
                c_first_name VARCHAR(20),
                c_last_name VARCHAR(30),
                c_preferred_cust_flag VARCHAR(1),
                c_birth_day INTEGER,
                c_birth_month INTEGER,
                c_birth_year INTEGER,
                c_birth_country VARCHAR(20),
                c_login VARCHAR(13),
                c_email_address VARCHAR(50),
                c_last_review_date INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS item (
                i_item_sk INTEGER PRIMARY KEY,
                i_item_id VARCHAR(16),
                i_rec_start_date TEXT,
                i_rec_end_date TEXT,
                i_item_desc VARCHAR(200),
                i_current_price REAL,
                i_wholesale_cost REAL,
                i_brand_id INTEGER,
                i_brand VARCHAR(50),
                i_class_id INTEGER,
                i_class VARCHAR(50),
                i_category_id INTEGER,
                i_category VARCHAR(50),
                i_manufact_id INTEGER,
                i_manufact VARCHAR(50),
                i_size VARCHAR(20),
                i_formulation VARCHAR(20),
                i_color VARCHAR(20),
                i_units VARCHAR(10),
                i_container VARCHAR(10),
                i_manager_id INTEGER,
                i_product_name VARCHAR(50)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS store (
                s_store_sk INTEGER PRIMARY KEY,
                s_store_id VARCHAR(16),
                s_rec_start_date TEXT,
                s_rec_end_date TEXT,
                s_closed_date_sk INTEGER,
                s_store_name VARCHAR(50),
                s_number_employees INTEGER,
                s_floor_space INTEGER,
                s_hours VARCHAR(20),
                s_manager VARCHAR(40),
                s_market_id INTEGER,
                s_geography_class VARCHAR(100),
                s_market_desc VARCHAR(100),
                s_market_manager VARCHAR(40),
                s_division_id INTEGER,
                s_division_name VARCHAR(50),
                s_company_id INTEGER,
                s_company_name VARCHAR(50),
                s_street_number VARCHAR(10),
                s_street_name VARCHAR(60),
                s_street_type VARCHAR(15),
                s_suite_number VARCHAR(10),
                s_city VARCHAR(60),
                s_county VARCHAR(30),
                s_state VARCHAR(2),
                s_zip VARCHAR(10),
                s_country VARCHAR(20),
                s_gmt_offset REAL,
                s_tax_precentage REAL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS store_sales (
                ss_sold_date_sk INTEGER,
                ss_sold_time_sk INTEGER,
                ss_item_sk INTEGER,
                ss_customer_sk INTEGER,
                ss_cdemo_sk INTEGER,
                ss_hdemo_sk INTEGER,
                ss_addr_sk INTEGER,
                ss_store_sk INTEGER,
                ss_promo_sk INTEGER,
                ss_ticket_number INTEGER,
                ss_quantity INTEGER,
                ss_wholesale_cost REAL,
                ss_list_price REAL,
                ss_sales_price REAL,
                ss_ext_discount_amt REAL,
                ss_ext_sales_price REAL,
                ss_ext_wholesale_cost REAL,
                ss_ext_list_price REAL,
                ss_ext_tax REAL,
                ss_coupon_amt REAL,
                ss_net_paid REAL,
                ss_net_paid_inc_tax REAL,
                ss_net_profit REAL,
                PRIMARY KEY (ss_item_sk, ss_ticket_number)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS warehouse (
                w_warehouse_sk INTEGER PRIMARY KEY,
                w_warehouse_id VARCHAR(16),
                w_warehouse_name VARCHAR(20),
                w_warehouse_sq_ft INTEGER,
                w_street_number VARCHAR(10),
                w_street_name VARCHAR(60),
                w_street_type VARCHAR(15),
                w_suite_number VARCHAR(10),
                w_city VARCHAR(60),
                w_county VARCHAR(30),
                w_state VARCHAR(2),
                w_zip VARCHAR(10),
                w_country VARCHAR(20),
                w_gmt_offset REAL
            )
            """,
        ]

        for table_sql in tables_sql:
            conn.execute(table_sql)

        conn.commit()

    def create_mock_connection(self) -> "MockOracleConnection":
        """Create a mock Oracle connection that uses SQLite backend."""
        return MockOracleConnection(self.create_test_database())


class MockOracleConnection:
    """Mock Oracle connection that uses SQLite backend for testing."""

    def __init__(self, sqlite_conn: sqlite3.Connection):
        self.sqlite_conn = sqlite_conn
        self.adapter = SQLiteOracleAdapter()
        self._autocommit = False

    def cursor(self):
        """Return a mock Oracle cursor."""
        return MockOracleCursor(self.sqlite_conn, self.adapter)

    def commit(self):
        """Commit transaction."""
        self.sqlite_conn.commit()

    def rollback(self):
        """Rollback transaction."""
        self.sqlite_conn.rollback()

    def close(self):
        """Close connection."""
        self.sqlite_conn.close()

    def ping(self):
        """Test connection."""
        try:
            self.sqlite_conn.execute("SELECT 1").fetchone()
            return True
        except:
            return False

    @property
    def autocommit(self):
        """Get autocommit status."""
        return self._autocommit

    @autocommit.setter
    def autocommit(self, value):
        """Set autocommit status."""
        self._autocommit = value
        if value:
            self.sqlite_conn.isolation_level = None
        else:
            self.sqlite_conn.isolation_level = "DEFERRED"


class MockOracleCursor:
    """Mock Oracle cursor that uses SQLite backend for testing."""

    def __init__(self, sqlite_conn: sqlite3.Connection, adapter: SQLiteOracleAdapter):
        self.sqlite_conn = sqlite_conn
        self.adapter = adapter
        self.sqlite_cursor = sqlite_conn.cursor()
        self._rowcount = 0
        self._description = None

    def execute(self, sql: str, parameters=None):
        """Execute SQL statement."""
        # Adapt Oracle SQL to SQLite
        sqlite_sql = self.adapter.adapt_schema_sql(sql)

        try:
            if parameters:
                result = self.sqlite_cursor.execute(sqlite_sql, parameters)
            else:
                result = self.sqlite_cursor.execute(sqlite_sql)

            self._rowcount = self.sqlite_cursor.rowcount
            self._description = self.sqlite_cursor.description
            return result
        except sqlite3.Error as e:
            # Convert SQLite errors to Oracle-like errors
            raise Exception(f"ORA-00001: {e}")

    def executemany(self, sql: str, parameters_list):
        """Execute SQL statement with multiple parameter sets."""
        sqlite_sql = self.adapter.adapt_schema_sql(sql)

        try:
            result = self.sqlite_cursor.executemany(sqlite_sql, parameters_list)
            self._rowcount = self.sqlite_cursor.rowcount
            return result
        except sqlite3.Error as e:
            raise Exception(f"ORA-00001: {e}")

    def fetchone(self):
        """Fetch one row."""
        return self.sqlite_cursor.fetchone()

    def fetchall(self):
        """Fetch all rows."""
        return self.sqlite_cursor.fetchall()

    def fetchmany(self, size=None):
        """Fetch multiple rows."""
        if size is None:
            return self.sqlite_cursor.fetchmany()
        return self.sqlite_cursor.fetchmany(size)

    def close(self):
        """Close cursor."""
        self.sqlite_cursor.close()

    @property
    def rowcount(self):
        """Return number of affected rows."""
        return self._rowcount

    @property
    def description(self):
        """Return column description."""
        return self._description

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
