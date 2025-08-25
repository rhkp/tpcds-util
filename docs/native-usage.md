# Native TPC-DS Utility Usage Guide

This guide covers native installation and usage of the TPC-DS utility directly on your system.

## Prerequisites

- **Python 3.8+**
- **Oracle Client Libraries** (see [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client.html))
- **Oracle database** with appropriate user privileges

## Installation

### Install from Source

```bash
git clone https://github.com/rhkp/tpcds-util.git
cd tpcds-util
pip install -e .
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Interactive Setup

```bash
tpcds-util config init
```

This will prompt you for:
- Database connection details (host, port, service name)
- Database username and password
- Target schema name (optional)
- Default scale factor
- Output directory
- Parallel workers

### Manual Configuration

```bash
# Database connection
tpcds-util config set --host mydb.example.com --port 1521
tpcds-util config set --service-name freepdb1
tpcds-util config set --username system

# Schema targeting
tpcds-util config set --schema-name TPCDSV1

# Performance settings
tpcds-util config set --default-scale 2 --parallel-workers 4
```

### View Configuration

```bash
tpcds-util config show
```

## Database Operations

### Test Connection

```bash
tpcds-util db test
```

### Schema Management

#### Create Schema

```bash
# Create in current user's schema
tpcds-util schema create

# Create in specific schema
tpcds-util schema create --schema TPCDSV1

# Use custom schema file
tpcds-util schema create --schema-file custom_schema.sql
```

#### Drop Schema

```bash
# Drop with confirmation prompt
tpcds-util schema drop

# Drop without confirmation
tpcds-util schema drop --confirm

# Drop from specific schema
tpcds-util schema drop --schema TPCDSV1 --confirm
```

### Database Information

```bash
# Show table information
tpcds-util db info

# Show specific schema tables
tpcds-util db info --schema TPCDSV1

# Overall system status
tpcds-util status
```

## Data Generation

### Generate Synthetic Data

```bash
# Default scale (from config)
tpcds-util generate data

# Specific scale factor
tpcds-util generate data --scale 1

# Custom output directory
tpcds-util generate data --scale 1 --output-dir ./my_data

# Custom parallelism
tpcds-util generate data --scale 1 --parallel 8
```

### Scale Factor Guidelines

- **Scale 1**: ~1GB data, good for development
- **Scale 10**: ~10GB data, suitable for testing
- **Scale 100**: ~100GB data, performance benchmarking
- **Scale 1000**: ~1TB data, enterprise testing

## Data Loading

### Load All Tables

```bash
# Load from default directory
tpcds-util load data

# Load from specific directory
tpcds-util load data --data-dir ./my_data

# Load with custom parallelism
tpcds-util load data --parallel 8
```

### Load Specific Tables

```bash
# Load single table
tpcds-util load data --table customer

# Load multiple tables (run command multiple times)
tpcds-util load data --table store_sales
tpcds-util load data --table catalog_sales
```

### Load to Specific Schema

```bash
# Load to configured schema
tpcds-util load data --schema PRODUCTION_SCHEMA

# Load specific table to schema
tpcds-util load data --table customer --schema TEST_SCHEMA
```

### Data Management

#### Truncate Tables

```bash
# Truncate with confirmation
tpcds-util load truncate

# Truncate without confirmation
tpcds-util load truncate --confirm

# Truncate specific schema
tpcds-util load truncate --schema TPCDSV1 --confirm
```

## Multi-Schema Workflows

### Development Environment

```bash
# Setup development schema
tpcds-util config set --username system --schema-name DEV_TPCDS
tpcds-util schema create
tpcds-util generate data --scale 1
tpcds-util load data
```

### Production Environment

```bash
# Setup production schema
tpcds-util config set --username system --schema-name PROD_TPCDS
tpcds-util schema create
tpcds-util generate data --scale 100
tpcds-util load data --parallel 16
```

### Testing Environment

```bash
# Setup testing schema
tpcds-util config set --username system --schema-name TEST_TPCDS
tpcds-util schema create
tpcds-util generate data --scale 10
tpcds-util load data
```

## Configuration File

The utility stores configuration in `~/.tpcds-util/config.yaml`:

```yaml
database:
  host: localhost
  port: 1521
  service_name: freepdb1
  username: system
  password: ""  # Set via environment variable
  use_sid: false

schema_name: "TPCDSV1"  # Target schema name
default_scale: 1
default_output_dir: ./tpcds_data
parallel_workers: 4
```

## Environment Variables

### Database Password

```bash
# Set password via environment variable (recommended)
export TPCDS_DB_PASSWORD="your_password"
tpcds-util db test
```

### Batch Operations

```bash
# Run multiple operations
export TPCDS_DB_PASSWORD="your_password"
tpcds-util schema create
tpcds-util generate data --scale 1
tpcds-util load data
tpcds-util db info
```

## Generated Data Structure

The utility generates files for all 25 TPC-DS tables:

### Dimension Tables
- `call_center.dat` - Call center information
- `catalog_page.dat` - Catalog page details  
- `customer.dat` - Customer information
- `customer_address.dat` - Customer addresses
- `customer_demographics.dat` - Customer demographics
- `date_dim.dat` - Date dimension
- `household_demographics.dat` - Household demographics
- `income_band.dat` - Income bands
- `item.dat` - Product items
- `promotion.dat` - Promotional campaigns
- `reason.dat` - Return reasons
- `ship_mode.dat` - Shipping methods
- `store.dat` - Store information
- `time_dim.dat` - Time dimension
- `warehouse.dat` - Warehouse information
- `web_page.dat` - Web page details
- `web_site.dat` - Web site information

### Fact Tables
- `catalog_sales.dat` - Catalog sales transactions
- `catalog_returns.dat` - Catalog returns
- `inventory.dat` - Inventory levels
- `store_sales.dat` - Store sales transactions
- `store_returns.dat` - Store returns
- `web_sales.dat` - Web sales transactions
- `web_returns.dat` - Web returns

### Metadata
- `dbgen_version.dat` - Generation metadata

## Troubleshooting

### Database Connection Issues

```bash
# Check configuration
tpcds-util config show

# Test connection
tpcds-util db test

# Check Oracle client installation
python -c "import oracledb; print('Oracle client OK')"
```

### Permission Issues

```bash
# Use DBA user for cross-schema operations
tpcds-util config set --username system

# Or grant privileges to regular user (not recommended)
# GRANT CREATE ANY TABLE TO your_user;
# GRANT DROP ANY TABLE TO your_user;
```

### Performance Issues

```bash
# Increase parallelism
tpcds-util config set --parallel-workers 8

# Use smaller scale for testing
tpcds-util generate data --scale 1

# Check system resources during load
tpcds-util load data --parallel 4
```

### Data Loading Errors

```bash
# Verify schema exists
tpcds-util db info

# Check Oracle error logs
# Review tablespace space
# Verify file permissions on data directory
```

## Advanced Usage

### Custom Schema Files

```bash
# Use custom schema definition
tpcds-util schema create --schema-file my_custom_schema.sql
```

### Scripting and Automation

```bash
#!/bin/bash
# Automated TPC-DS setup script

export TPCDS_DB_PASSWORD="your_password"

# Setup multiple environments
for env in dev test prod; do
    echo "Setting up $env environment..."
    tpcds-util config set --schema-name "${env^^}_TPCDS"
    tpcds-util schema create
    
    # Different scales for different environments
    case $env in
        dev) scale=1 ;;
        test) scale=10 ;;
        prod) scale=100 ;;
    esac
    
    tpcds-util generate data --scale $scale
    tpcds-util load data
    echo "$env environment ready!"
done
```

---

**Next Steps:**
- 🐳 [Container Usage Guide](container-usage.md) - For production deployments
- 🏠 [Main README](../README.md) - Back to overview