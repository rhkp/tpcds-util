# TPC-DS Utility

A simple, user-friendly command-line utility for generating TPC-DS compliant synthetic data and managing TPC-DS benchmarks on Oracle databases.

## Overview

This utility generates realistic synthetic data that complies with the TPC-DS specification. All data is generated programmatically without external dependencies.

## Features

- **Synthetic Data Generation**: Generate TPC-DS compliant data with realistic business patterns
- **Easy Configuration**: Simple setup with interactive configuration
- **Database Management**: Create/drop schemas, test connections
- **Data Loading**: Load data into Oracle with parallel processing
- **Rich CLI**: Beautiful command-line interface with progress bars and tables

## Installation

### Prerequisites

- Python 3.8+
- Oracle Client Libraries (see [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client.html))
- Oracle database with appropriate privileges for schema creation

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

## Quick Start

### 1. Initialize Configuration

```bash
tpcds-util config init
```

This will prompt you for:
- Database connection details
- Default scale factor
- Output directory
- Parallel workers

### 2. Test Database Connection

```bash
tpcds-util db test
```

### 3. Create TPC-DS Schema

```bash
tpcds-util schema create
```

### 4. Generate Synthetic Data

```bash
tpcds-util generate data --scale 1
```

### 5. Load Data into Database

```bash
tpcds-util load data --data-dir ./tpcds_data
```

### 6. Verify Installation

```bash
tpcds-util db info
tpcds-util status
```

## Detailed Usage

### Configuration

Show current configuration:
```bash
tpcds-util config show
```

Update specific settings:
```bash
tpcds-util config set --host mydb.example.com --port 1521
tpcds-util config set --username myuser --default-scale 2
```

### Data Generation

Generate different scale factors:
```bash
# Small dataset (scale factor 1)
tpcds-util generate data --scale 1 --output-dir ./small_data

# Medium dataset (scale factor 10)  
tpcds-util generate data --scale 10 --output-dir ./medium_data

# Custom output directory
tpcds-util generate data --output-dir /custom/path/data
```

The synthetic data generator creates:
- **25 TPC-DS tables** with proper relationships
- **Realistic business patterns** including geographic distribution
- **Seasonal variations** in sales data
- **Multi-channel retail** (store, web, catalog sales)
- **Customer demographics** linked to addresses and purchase behavior

### Data Loading

Load all tables:
```bash
tpcds-util load data --data-dir ./tpcds_data
```

Load specific table:
```bash
tpcds-util load data --data-dir ./tpcds_data --table customer
```

Load with custom parallelism:
```bash
tpcds-util load data --data-dir ./tpcds_data --parallel 8
```

Truncate all data:
```bash
tpcds-util load truncate --confirm
```

### Schema Management

Create schema:
```bash
tpcds-util schema create
```

Drop schema (with confirmation):
```bash
tpcds-util schema drop
```

### Database Operations

Test connection:
```bash
tpcds-util db test
```

Show table information:
```bash
tpcds-util db info
```

Overall status:
```bash
tpcds-util status
```

## Configuration File

The utility stores configuration in `~/.tpcds-util/config.yaml`:

```yaml
database:
  host: localhost
  port: 1521
  service_name: orcl
  username: tpcds
  password: ""
  use_sid: false

default_scale: 1
default_output_dir: ./tpcds_data
parallel_workers: 4
```

## Generated Data Structure

The synthetic data generator creates files for all 25 TPC-DS tables:

**Dimension Tables:**
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

**Fact Tables:**
- `catalog_sales.dat` - Catalog sales transactions
- `catalog_returns.dat` - Catalog returns
- `inventory.dat` - Inventory levels
- `store_sales.dat` - Store sales transactions
- `store_returns.dat` - Store returns
- `web_sales.dat` - Web sales transactions
- `web_returns.dat` - Web returns

**Metadata:**
- `dbgen_version.dat` - Generation metadata

## Data Characteristics

The synthetic data includes:

- **Geographic Distribution**: Customers across 4 US regions with proper timezone mapping
- **Seasonal Patterns**: Sales data reflecting realistic business cycles
- **Product Categories**: Electronics, Clothing, Home & Garden, Sports, Books, Automotive
- **Customer Segments**: Varied demographics, education levels, and income bands
- **Business Relationships**: Proper foreign key relationships across all tables
- **Realistic Volumes**: Configurable scale factors for different dataset sizes

## Platform Support

- **Linux**: Fully supported
- **macOS**: Fully supported  
- **Windows**: Supported via WSL or native Python

## Troubleshooting

### Common Issues

**Database Connection Failed**
- Verify Oracle client libraries are installed
- Check database credentials and connectivity
- Ensure database service is running

**Permission Denied**
- Verify database user has CREATE TABLE privileges
- Check Oracle tablespace permissions

**Data Loading Errors**
- Verify schema exists before loading data
- Check for sufficient database storage space
- Review Oracle error logs for specific issues

**Configuration Issues**
- Check `~/.tpcds-util/config.yaml` syntax
- Verify file permissions on config directory
- Use `tpcds-util config init` to recreate configuration

### Getting Help

```bash
tpcds-util --help
tpcds-util generate --help
tpcds-util load --help
```

## License

This utility is open source. The synthetic data generated is license-free and safe for enterprise use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Check existing GitHub issues
- Create a new issue with detailed information
- Include configuration and error logs when reporting problems