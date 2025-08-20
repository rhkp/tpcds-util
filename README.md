# TPC-DS Utility

A simple, user-friendly command-line utility for managing TPC-DS benchmarks on Oracle databases.

## Important Notice

**This utility is a wrapper around the [TPC-DS Kit](https://www.tpc.org/tpc_documents_current_versions/current_specifications5.asp).** You must obtain and install the TPC-DS Kit separately. The TPC-DS Kit has its own license terms that you are responsible for reviewing and complying with. This utility does not include or redistribute any TPC-DS Kit components.

## Features

- **Easy Configuration**: Simple setup with interactive configuration
- **Database Management**: Create/drop schemas, test connections
- **Data Generation**: Generate TPC-DS data files with configurable scale factors
- **Data Loading**: Load data into Oracle with parallel processing
- **Query Management**: Generate and execute TPC-DS queries
- **Rich CLI**: Beautiful command-line interface with progress bars and tables

## Installation

### Prerequisites

- Python 3.8+
- Oracle Client Libraries (see [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client.html))
- TPC-DS Kit (you must download and build this separately - see setup section below)
- Oracle database with appropriate privileges for schema creation

### Install from Source

```bash
git clone https://github.com/rhkp/TPC-DS_Oracle.git
cd TPC-DS_Oracle/tpcds-util
pip install -e .
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Initialize Configuration

```bash
tpcds-util config init
```

This will prompt you for:
- Database connection details
- TPC-DS kit path
- Default settings

### 2. Test Database Connection

```bash
tpcds-util db test
```

### 3. Create Schema

```bash
tpcds-util schema create
```

### 4. Generate Data

```bash
# Generate scale factor 1 data
tpcds-util generate data --scale 1

# Generate with custom output directory
tpcds-util generate data --scale 5 --output-dir ./sf5_data
```

### 5. Load Data

```bash
# Load all tables
tpcds-util load data

# Load specific table
tpcds-util load data --table store_sales

# Load with parallel processing
tpcds-util load data --parallel 8
```

### 6. Check Status

```bash
tpcds-util status
tpcds-util db info
```

## Command Reference

### Configuration Commands

```bash
# Show current configuration
tpcds-util config show

# Set individual configuration values
tpcds-util config set --host localhost --port 1521
tpcds-util config set --username myuser
tpcds-util config set --tpcds-kit-path /path/to/tpcds-kit

# Initialize configuration with prompts
tpcds-util config init
```

### Database Commands

```bash
# Test database connection
tpcds-util db test

# Show table information
tpcds-util db info
```

### Schema Commands

```bash
# Create TPC-DS schema
tpcds-util schema create

# Drop TPC-DS schema (with confirmation)
tpcds-util schema drop

# Drop without confirmation
tpcds-util schema drop --confirm
```

### Data Generation Commands

```bash
# Generate data with default scale
tpcds-util generate data

# Generate with specific scale factor
tpcds-util generate data --scale 10

# Generate with parallel processing
tpcds-util generate data --scale 5 --parallel 4

# Generate to specific directory
tpcds-util generate data --output-dir /data/tpcds
```

### Data Loading Commands

```bash
# Load all data files
tpcds-util load data

# Load from specific directory
tpcds-util load data --data-dir /data/tpcds

# Load specific table
tpcds-util load data --table customer

# Load with parallel processing
tpcds-util load data --parallel 8

# If loading gets interrupted, clear data first and reload
tpcds-util load truncate --confirm
tpcds-util load data
```

**Note:** If the data loading process gets interrupted for any reason (network issues, timeouts, etc.), it's recommended to truncate all data first before reloading to avoid constraint violations from partial data.

### Utility Commands

```bash
# Show overall system status
tpcds-util status

# Show help
tpcds-util --help
tpcds-util <command> --help
```

## Configuration

The utility stores configuration in `~/.tpcds-util/config.yaml`. You can edit this file directly or use the CLI commands.

Example configuration:

```yaml
database:
  host: localhost
  port: 1521
  service_name: orcl
  username: tpcds_user
  password: ""  # Leave empty to prompt or use environment variable

tpcds_kit_path: /opt/tpcds-kit
default_scale: 1
default_output_dir: ./tpcds_data
parallel_workers: 4
```

### Environment Variables

- `TPCDS_DB_PASSWORD`: Database password (avoids prompting)

## TPC-DS Kit Setup

**Required:** You must set up the TPC-DS Kit before using this utility.

1. Download the TPC-DS Kit from [TPC website](https://www.tpc.org/tpc_documents_current_versions/current_specifications5.asp) or use the [community version](https://github.com/gregrahn/tpcds-kit)

2. Review the TPC-DS Kit license terms (EULA.txt) to ensure compliance with your use case

3. Build the tools:
   ```bash
   cd tpcds-kit/tools
   make
   ```

4. Set the path in configuration:
   ```bash
   tpcds-util config set --tpcds-kit-path /path/to/tpcds-kit
   ```

5. Verify the setup:
   ```bash
   tpcds-util config show
   ```

### Platform Notes

- **macOS**: May require build modifications - see [macOS compatibility notes](https://github.com/rhkp/TPC-DS_Oracle#macos-compatibility-notes)
- **Linux**: Generally builds without issues
- **Windows**: Use WSL or mingw for building TPC-DS Kit

## Examples

### Complete Workflow Example

```bash
# 1. Setup
tpcds-util config init
tpcds-util db test

# 2. Create schema
tpcds-util schema create

# 3. Generate and load scale factor 1 data
tpcds-util generate data --scale 1
tpcds-util load data

# 4. Check results
tpcds-util db info
tpcds-util status
```

### Cleanup Example

```bash
# Drop schema and all data
tpcds-util schema drop --confirm

# Or just truncate tables (keep schema)
tpcds-util load truncate --confirm
```

## Architecture

The utility is built with:

- **Click**: Command-line interface framework
- **cx_Oracle**: Oracle database connectivity
- **Rich**: Beautiful terminal output
- **PyYAML**: Configuration management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- Check the [main repository](https://github.com/rhkp/TPC-DS_Oracle) for issues
- Refer to TPC-DS documentation for benchmark details
- Oracle documentation for database-specific issues