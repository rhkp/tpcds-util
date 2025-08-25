"""Command Line Interface for TPC-DS utility."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
import yaml

from .config import config_manager
from .database import db_manager
from .generator import DataGenerator
from .loader import DataLoader


console = Console()


@click.group()
@click.version_option()
def cli():
    """TPC-DS Utility - Manage TPC-DS benchmarks on Oracle databases."""
    pass


@cli.group()
def config():
    """Manage configuration settings."""
    pass


@config.command('show')
def config_show():
    """Show current configuration."""
    cfg = config_manager.load()
    
    table = Table(title="TPC-DS Utility Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    # Database settings
    table.add_row("Database Host", cfg.database.host)
    table.add_row("Database Port", str(cfg.database.port))
    table.add_row("Service Name", cfg.database.service_name)
    table.add_row("Username", cfg.database.username or "[Not Set]")
    table.add_row("Password", "***" if cfg.database.password else "[Not Set]")
    
    # TPC-DS settings
    table.add_row("TPC-DS Kit Path", cfg.tpcds_kit_path or "[Not Set]")
    table.add_row("Default Scale", str(cfg.default_scale))
    table.add_row("Output Directory", cfg.default_output_dir)
    table.add_row("Parallel Workers", str(cfg.parallel_workers))
    
    console.print(table)


@config.command('set')
@click.option('--host', help='Database host')
@click.option('--port', type=int, help='Database port')
@click.option('--service-name', help='Database service name or SID')
@click.option('--username', help='Database username')
@click.option('--password', help='Database password')
@click.option('--use-sid', is_flag=True, help='Use SID instead of service name')
@click.option('--tpcds-kit-path', help='Path to TPC-DS kit')
@click.option('--default-scale', type=int, help='Default scale factor')
@click.option('--output-dir', help='Default output directory')
@click.option('--parallel-workers', type=int, help='Number of parallel workers')
def config_set(**kwargs):
    """Set configuration values."""
    # Filter out None values
    updates = {k: v for k, v in kwargs.items() if v is not None}
    
    if not updates:
        click.echo("No configuration changes specified.")
        return
    
    config_manager.update(**updates)
    console.print("✅ Configuration updated successfully", style="green")


@config.command('init')
def config_init():
    """Initialize configuration with prompts."""
    click.echo("Setting up TPC-DS Utility configuration...")
    
    # Database configuration
    host = click.prompt('Database host', default='localhost')
    port = click.prompt('Database port', default=1521, type=int)
    service_name = click.prompt('Database service name', default='orcl')
    username = click.prompt('Database username')
    
    # TPC-DS kit path
    kit_path = click.prompt('TPC-DS kit path (optional)', default='', show_default=False)
    
    # Other settings
    scale = click.prompt('Default scale factor', default=1, type=int)
    output_dir = click.prompt('Default output directory', default='./tpcds_data')
    workers = click.prompt('Parallel workers', default=4, type=int)
    
    config_manager.update(
        host=host,
        port=port,
        service_name=service_name,
        username=username,
        tpcds_kit_path=kit_path,
        default_scale=scale,
        default_output_dir=output_dir,
        parallel_workers=workers
    )
    
    console.print("✅ Configuration initialized successfully", style="green")


@cli.group()
def db():
    """Database operations."""
    pass


@db.command('test')
def db_test():
    """Test database connection."""
    console.print("Testing database connection...")
    
    if db_manager.test_connection():
        console.print("✅ Database connection successful", style="green")
    else:
        console.print("❌ Database connection failed", style="red")
        click.echo("Please check your configuration with 'tpcds-util config show'", err=True)


@db.command('info')
def db_info():
    """Show database table information."""
    tables = db_manager.get_table_info()
    
    if not tables:
        console.print("No TPC-DS tables found. Create schema first with 'tpcds-util schema create'", style="yellow")
        return
    
    table = Table(title="TPC-DS Tables")
    table.add_column("Table Name", style="cyan")
    table.add_column("Rows", justify="right", style="green")
    table.add_column("Blocks", justify="right")
    table.add_column("Avg Row Length", justify="right")
    
    for t in tables:
        table.add_row(
            t['TABLE_NAME'],
            str(t['NUM_ROWS']) if t['NUM_ROWS'] else "0",
            str(t['BLOCKS']) if t['BLOCKS'] else "0",
            str(t['AVG_ROW_LEN']) if t['AVG_ROW_LEN'] else "0"
        )
    
    console.print(table)


@cli.group()
def schema():
    """Schema management operations."""
    pass


@schema.command('create')
@click.option('--schema-file', type=click.Path(exists=True), help='Path to schema SQL file')
def schema_create(schema_file):
    """Create TPC-DS schema."""
    schema_path = Path(schema_file) if schema_file else None
    
    if db_manager.create_schema(schema_path):
        console.print("✅ Schema created successfully", style="green")
    else:
        console.print("❌ Schema creation failed", style="red")


@schema.command('drop')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def schema_drop(confirm):
    """Drop TPC-DS schema."""
    if db_manager.drop_schema(confirm):
        console.print("✅ Schema dropped successfully", style="green")
    else:
        console.print("❌ Schema drop failed", style="red")


@cli.group()
def generate():
    """Data generation operations."""
    pass


@generate.command('data')
@click.option('--scale', type=int, help='Scale factor (default from config)')
@click.option('--output-dir', type=click.Path(), help='Output directory (default from config)')
@click.option('--parallel', type=int, help='Parallel workers (default from config)')
@click.option('--synthetic', is_flag=True, help='Generate synthetic data instead of using TPC-DS kit (license-free)')
def generate_data(scale, output_dir, parallel, synthetic):
    """Generate TPC-DS data files."""
    generator = DataGenerator()
    
    if generator.generate_data(scale, output_dir, parallel, synthetic):
        console.print("✅ Data generation completed", style="green")
    else:
        console.print("❌ Data generation failed", style="red")


@cli.group()
def load():
    """Data loading operations."""
    pass


@load.command('data')
@click.option('--data-dir', type=click.Path(exists=True), help='Directory containing data files')
@click.option('--parallel', type=int, help='Parallel workers (default from config)')
@click.option('--table', help='Load specific table only')
def load_data(data_dir, parallel, table):
    """Load data into TPC-DS tables."""
    loader = DataLoader()
    
    if loader.load_data(data_dir, parallel, table):
        console.print("✅ Data loading completed", style="green")
    else:
        console.print("❌ Data loading failed", style="red")


@load.command('truncate')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def truncate_data(confirm):
    """Truncate all TPC-DS tables (remove all data)."""
    loader = DataLoader()
    
    if loader.truncate_tables(confirm):
        console.print("✅ Data truncation completed", style="green")
    else:
        console.print("❌ Data truncation failed", style="red")


@cli.command('status')
def status():
    """Show overall system status."""
    console.print("TPC-DS Utility Status", style="bold blue")
    console.print()
    
    # Configuration status
    cfg = config_manager.load()
    if cfg.database.username and cfg.tpcds_kit_path:
        console.print("✅ Configuration: Complete", style="green")
    else:
        console.print("⚠️  Configuration: Incomplete", style="yellow")
    
    # Database connection
    if db_manager.test_connection():
        console.print("✅ Database: Connected", style="green")
    else:
        console.print("❌ Database: Connection failed", style="red")
    
    # Schema status
    tables = db_manager.get_table_info()
    if tables:
        console.print(f"✅ Schema: {len(tables)} tables found", style="green")
    else:
        console.print("⚠️  Schema: No tables found", style="yellow")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()