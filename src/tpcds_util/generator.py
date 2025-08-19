"""Data generation utilities for TPC-DS."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import config_manager


console = Console()


class DataGenerator:
    """Handles TPC-DS data generation using dsdgen."""
    
    def __init__(self):
        self.config = config_manager.load()
    
    def _find_dsdgen(self) -> Optional[Path]:
        """Find dsdgen executable."""
        # Check configured path first
        if self.config.tpcds_kit_path:
            kit_path = Path(self.config.tpcds_kit_path)
            dsdgen_path = kit_path / "tools" / "dsdgen"
            if dsdgen_path.exists():
                return dsdgen_path
        
        # Check common locations
        common_paths = [
            Path("./tools/dsdgen"),
            Path("../tpcds-kit/tools/dsdgen"),
            Path("./dsdgen"),
        ]
        
        for path in common_paths:
            if path.exists():
                return path
        
        # Check if dsdgen is in PATH
        dsdgen_in_path = shutil.which("dsdgen")
        if dsdgen_in_path:
            return Path(dsdgen_in_path)
        
        return None
    
    def generate_data(self, scale: Optional[int] = None, 
                     output_dir: Optional[str] = None,
                     parallel: Optional[int] = None) -> bool:
        """Generate TPC-DS data files."""
        
        # Use defaults from config if not specified
        scale = scale or self.config.default_scale
        output_dir = output_dir or self.config.default_output_dir
        parallel = parallel or self.config.parallel_workers
        
        # Find dsdgen executable
        dsdgen_path = self._find_dsdgen()
        if not dsdgen_path:
            click.echo("dsdgen executable not found. Please check your TPC-DS kit installation.", err=True)
            click.echo("Set the path with: tpcds-util config set --tpcds-kit-path /path/to/tpcds-kit", err=True)
            return False
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        console.print(f"Generating TPC-DS data (scale factor: {scale})")
        console.print(f"Output directory: {output_path.absolute()}")
        console.print(f"Using: {dsdgen_path}")
        
        try:
            # Build dsdgen command (simplified - no parallel for now)
            cmd = [
                str(dsdgen_path),
                "-scale", str(scale),
                "-dir", str(output_path.absolute()),
            ]
            
            console.print("Generating TPC-DS data files...")
            
            # Run single process generation
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Generating data files...", total=None)
                
                result = subprocess.run(
                    cmd,
                    cwd=dsdgen_path.parent,
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minutes timeout
                )
                
                progress.stop()
                
                if result.returncode != 0:
                    click.echo(f"dsdgen failed: {result.stderr or result.stdout}", err=True)
                    return False
            
            # Verify generated files
            generated_files = list(output_path.glob("*.dat"))
            if not generated_files:
                click.echo("No data files were generated.", err=True)
                return False
            
            console.print(f"✅ Generated {len(generated_files)} data files", style="green")
            
            # Show file sizes
            table = Table(title="Generated Data Files")
            table.add_column("File", style="cyan")
            table.add_column("Size", justify="right", style="green")
            
            for file_path in sorted(generated_files):
                size_mb = file_path.stat().st_size / (1024 * 1024)
                table.add_row(file_path.name, f"{size_mb:.1f} MB")
            
            console.print(table)
            
            return True
            
        except Exception as e:
            click.echo(f"Error generating data: {e}", err=True)
            return False
    
    def generate_queries(self, output_dir: Optional[str] = None,
                        scale: Optional[int] = None) -> bool:
        """Generate TPC-DS query files."""
        
        # Find dsqgen executable
        dsqgen_path = None
        if self.config.tpcds_kit_path:
            kit_path = Path(self.config.tpcds_kit_path)
            dsqgen_path = kit_path / "tools" / "dsqgen"
        
        if not dsqgen_path or not dsqgen_path.exists():
            # Check if dsqgen is in PATH
            dsqgen_in_path = shutil.which("dsqgen")
            if dsqgen_in_path:
                dsqgen_path = Path(dsqgen_in_path)
            else:
                click.echo("dsqgen executable not found.", err=True)
                return False
        
        scale = scale or self.config.default_scale
        output_dir = output_dir or f"./queries_scale_{scale}"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Look for oracle templates
        template_paths = [
            Path("../TPC-DS_Oracle/queries/oracle_templates"),
            Path("./oracle_templates"),
            Path("queries/oracle_templates")
        ]
        
        template_path = None
        for path in template_paths:
            if path.exists() and (path / "oracle.tpl").exists():
                template_path = path
                break
        
        if not template_path:
            click.echo("Oracle query templates not found.", err=True)
            return False
        
        console.print(f"Generating TPC-DS queries (scale factor: {scale})")
        console.print(f"Template directory: {template_path.absolute()}")
        console.print(f"Output directory: {output_path.absolute()}")
        
        try:
            cmd = [
                str(dsqgen_path),
                "-directory", str(template_path.absolute()),
                "-input", str(template_path.absolute()),
                "-templates.lst",
                "-verbose", "y",
                "-qualify", "y",
                "-scale", str(scale),
                "-dialect", "oracle",
                "-output_dir", str(output_path.absolute())
            ]
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Generating query files...")
                
                result = subprocess.run(
                    cmd,
                    cwd=dsqgen_path.parent,
                    capture_output=True,
                    text=True
                )
                
                progress.update(task, completed=True)
                
                if result.returncode != 0:
                    click.echo(f"dsqgen failed: {result.stderr}", err=True)
                    return False
            
            # Count generated query files
            query_files = list(output_path.glob("query*.sql"))
            console.print(f"✅ Generated {len(query_files)} query files", style="green")
            
            return True
            
        except Exception as e:
            click.echo(f"Error generating queries: {e}", err=True)
            return False