"""Database connection and operations for Oracle."""

import oracledb
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from pathlib import Path
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import config_manager


console = Console()


class DatabaseManager:
    """Manages Oracle database connections and operations."""
    
    def __init__(self):
        self.config = config_manager.load()
    
    @contextmanager
    def get_connection(self) -> Generator[oracledb.Connection, None, None]:
        """Get database connection context manager."""
        password = config_manager.get_password()
        
        try:
            connection = oracledb.connect(
                user=self.config.database.username,
                password=password,
                dsn=self.config.database.dsn
            )
            yield connection
        except oracledb.Error as e:
            click.echo(f"Database connection error: {e}", err=True)
            raise
        finally:
            if 'connection' in locals():
                connection.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM DUAL")
                    result = cursor.fetchone()
                    return result is not None
        except Exception:
            return False
    
    def execute_sql_file(self, sql_file: Path) -> bool:
        """Execute SQL statements from a file."""
        if not sql_file.exists():
            click.echo(f"SQL file not found: {sql_file}", err=True)
            return False
        
        try:
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            # Handle Oracle PL/SQL blocks which end with /
            # Split by / when it's on its own line, otherwise split by ;
            statements = []
            current_stmt = ""
            lines = sql_content.split('\n')
            
            for line in lines:
                stripped_line = line.strip()
                
                # Skip comment lines
                if stripped_line.startswith('--') or not stripped_line:
                    continue
                    
                if stripped_line == '/':
                    # End of PL/SQL block
                    if current_stmt.strip():
                        statements.append(current_stmt.strip())
                        current_stmt = ""
                elif stripped_line.endswith(';') and not any(keyword in current_stmt.upper() for keyword in ['BEGIN', 'DECLARE']):
                    # Regular SQL statement - remove the semicolon and add to statements
                    current_stmt += stripped_line[:-1]  # Remove semicolon
                    if current_stmt.strip():
                        statements.append(current_stmt.strip())
                    current_stmt = ""
                else:
                    # Continue building statement
                    if current_stmt:
                        current_stmt += '\n' + stripped_line
                    else:
                        current_stmt = stripped_line
            
            # Add any remaining statement
            if current_stmt.strip():
                statements.append(current_stmt.strip())
            
            # Filter out empty statements and comments
            statements = [stmt for stmt in statements if stmt.strip() and not stmt.strip().startswith('--')]
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task(f"Executing {sql_file.name}...", total=len(statements))
                        
                        for i, stmt in enumerate(statements):
                            if stmt.strip():
                                try:
                                    # Debug: print first few statements
                                    if i < 3:
                                        console.print(f"Executing statement {i+1}: {stmt[:100]}...", style="cyan")
                                    cursor.execute(stmt)
                                    progress.advance(task)
                                except oracledb.Error as e:
                                    # Log the error but continue with next statement
                                    console.print(f"Error in statement {i+1}: {str(e)[:150]}", style="red")
                                    if i < 3:
                                        console.print(f"Failed statement: {stmt[:200]}", style="red")
                                    progress.advance(task)
                        
                        conn.commit()
            
            console.print(f"✅ Successfully executed {sql_file.name}", style="green")
            return True
            
        except Exception as e:
            click.echo(f"Error executing SQL file {sql_file}: {e}", err=True)
            return False
    
    def create_schema(self, schema_file: Optional[Path] = None) -> bool:
        """Create TPC-DS schema."""
        if schema_file is None:
            # Look for tpcds.sql in current directory or TPC-DS_Oracle repo
            candidates = [
                Path("tpcds.sql"),
                Path("../TPC-DS_Oracle/tpcds.sql"),
                Path("scripts/side_files/tpcds.sql")
            ]
            
            for candidate in candidates:
                if candidate.exists():
                    schema_file = candidate
                    break
            
            if schema_file is None:
                click.echo("Schema file (tpcds.sql) not found. Please specify path with --schema-file", err=True)
                return False
        
        console.print(f"Creating TPC-DS schema from {schema_file}")
        return self.execute_sql_file(schema_file)
    
    def drop_schema(self, confirm: bool = False) -> bool:
        """Drop TPC-DS schema (with confirmation)."""
        if not confirm:
            if not click.confirm("This will drop all TPC-DS tables and data. Continue?"):
                click.echo("Operation cancelled.")
                return False
        
        drop_statements = [
            "DROP TABLE call_center CASCADE CONSTRAINTS",
            "DROP TABLE catalog_page CASCADE CONSTRAINTS",
            "DROP TABLE catalog_returns CASCADE CONSTRAINTS",
            "DROP TABLE catalog_sales CASCADE CONSTRAINTS",
            "DROP TABLE customer CASCADE CONSTRAINTS",
            "DROP TABLE customer_address CASCADE CONSTRAINTS",
            "DROP TABLE customer_demographics CASCADE CONSTRAINTS",
            "DROP TABLE date_dim CASCADE CONSTRAINTS",
            "DROP TABLE household_demographics CASCADE CONSTRAINTS",
            "DROP TABLE income_band CASCADE CONSTRAINTS",
            "DROP TABLE inventory CASCADE CONSTRAINTS",
            "DROP TABLE item CASCADE CONSTRAINTS",
            "DROP TABLE promotion CASCADE CONSTRAINTS",
            "DROP TABLE reason CASCADE CONSTRAINTS",
            "DROP TABLE ship_mode CASCADE CONSTRAINTS",
            "DROP TABLE store CASCADE CONSTRAINTS",
            "DROP TABLE store_returns CASCADE CONSTRAINTS",
            "DROP TABLE store_sales CASCADE CONSTRAINTS",
            "DROP TABLE time_dim CASCADE CONSTRAINTS",
            "DROP TABLE warehouse CASCADE CONSTRAINTS",
            "DROP TABLE web_page CASCADE CONSTRAINTS",
            "DROP TABLE web_returns CASCADE CONSTRAINTS",
            "DROP TABLE web_sales CASCADE CONSTRAINTS",
            "DROP TABLE web_site CASCADE CONSTRAINTS"
        ]
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("Dropping TPC-DS tables...", total=len(drop_statements))
                        
                        for stmt in drop_statements:
                            try:
                                cursor.execute(stmt)
                                progress.advance(task)
                            except oracledb.Error as e:
                                # Ignore "table or view does not exist" errors
                                if "ORA-00942" not in str(e):
                                    console.print(f"Warning: {e}", style="yellow")
                                progress.advance(task)
                        
                        conn.commit()
            
            console.print("✅ Schema dropped successfully", style="green")
            return True
            
        except Exception as e:
            click.echo(f"Error dropping schema: {e}", err=True)
            return False
    
    def get_table_info(self) -> List[Dict[str, Any]]:
        """Get information about TPC-DS tables."""
        query = """
        SELECT table_name, num_rows, blocks, avg_row_len
        FROM user_tables 
        WHERE table_name IN (
            'CALL_CENTER', 'CATALOG_PAGE', 'CATALOG_RETURNS', 'CATALOG_SALES',
            'CUSTOMER', 'CUSTOMER_ADDRESS', 'CUSTOMER_DEMOGRAPHICS', 'DATE_DIM',
            'HOUSEHOLD_DEMOGRAPHICS', 'INCOME_BAND', 'INVENTORY', 'ITEM',
            'PROMOTION', 'REASON', 'SHIP_MODE', 'STORE', 'STORE_RETURNS',
            'STORE_SALES', 'TIME_DIM', 'WAREHOUSE', 'WEB_PAGE', 'WEB_RETURNS',
            'WEB_SALES', 'WEB_SITE'
        )
        ORDER BY table_name
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            click.echo(f"Error getting table info: {e}", err=True)
            return []


# Global database manager instance
db_manager = DatabaseManager()