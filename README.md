# TPC-DS Utility

A modern, user-friendly command-line utility for generating TPC-DS compliant synthetic data and managing TPC-DS benchmarks on Oracle databases.

## Overview

This utility generates realistic synthetic data that complies with the TPC-DS specification. All data is generated programmatically without external dependencies, making it perfect for database testing, AI/ML training datasets, and performance benchmarking.

## Features

- **🔄 Synthetic Data Generation**: Generate TPC-DS compliant data with realistic business patterns
- **🎯 Multi-Schema Support**: Target specific schemas for all database operations  
- **⚙️ Easy Configuration**: Simple setup with interactive configuration
- **🛠️ Database Management**: Create/drop schemas, test connections
- **📊 Data Loading**: Load data into Oracle with parallel processing and autocommit protection
- **🎨 Rich CLI**: Beautiful command-line interface with progress bars and tables
- **🐳 Container Support**: Full containerization with Podman/Docker support
- **☸️ Kubernetes Ready**: Enterprise-grade Helm charts with integrated Oracle deployment
- **🔒 Enterprise Security**: Secure implementation without external dependencies or downloads

## Quick Start

Choose your preferred approach:

### 🖥️ Native Installation
Perfect for development and direct database access.

**[📖 Native Usage Guide →](docs/native-usage.md)**

```bash
# Install and configure
pip install -e .
tpcds-util config init

# Generate and load data
tpcds-util schema create
tpcds-util generate data --scale 1
tpcds-util load data
```

### 🐳 Container Usage  
Ideal for production deployments and isolated environments.

**[📖 Container Usage Guide →](docs/container-usage.md)**

#### 🏗️ Full Stack (with Oracle DB)
```bash
# Complete isolated environment
export TPCDS_DB_PASSWORD=TestPassword123
podman-compose up -d
podman-compose exec tpcds-util tpcds-util schema create
```

#### ⚡ External Database (production)
```bash
# Use with existing Oracle infrastructure
podman run --rm quay.io/rhkp/tpcds-util:latest \
  config set --host your-db-host
podman run --rm quay.io/rhkp/tpcds-util:latest \
  schema create
```

### ☸️ Kubernetes/OpenShift Deployment
Enterprise-ready deployment with integrated Oracle database and secure TPC-DS data loading.

#### 🎯 Integrated Oracle + TPC-DS (Recommended)
```bash
# Deploy complete Oracle 23ai + TPC-DS solution
helm install oracle23ai ./helm --namespace your-namespace

# Monitor data loading progress
oc logs -f job/oracle23ai-tpcds-populate -n your-namespace

# Verify data loading
oc exec oracle23ai-0 -n your-namespace -- \
  sqlplus -s tpcds/password@FREEPDB1 << 'EOF'
SELECT table_name, COUNT(*) FROM user_tables;
EOF
```

**Features:**
- ✅ **Secure**: No external binary downloads or kubectl dependencies
- ✅ **Automated**: Full Oracle initialization and TPC-DS user creation
- ✅ **Integrated**: Oracle 23ai with TPC-DS in single Helm deployment
- ✅ **Production-Ready**: Enterprise security standards and autocommit protection

## Generated Data

The utility creates **25 TPC-DS tables** with realistic business data:

- **📋 Dimension Tables**: customers, products, stores, dates, promotions
- **📊 Fact Tables**: sales transactions, returns, inventory levels  
- **🌍 Geographic Distribution**: Multi-region customer data
- **📈 Business Relationships**: Proper foreign key relationships
- **⏰ Temporal Patterns**: Seasonal sales variations

## Database User Configuration

The utility supports flexible database user configuration:

```bash
# Use DBA users for cross-schema operations (recommended)
tpcds-util config set --username system --schema-name TPCDSV1

# Use regular users for single-schema operations  
tpcds-util config set --username myuser --schema-name ""
```

**DBA Users (SYSTEM, SYS)**:
- ✅ Can create/drop tables in any schema
- ✅ No additional privilege grants needed
- ✅ Recommended for cross-schema operations

**Regular Users**: 
- ✅ Work within their own schema by default
- ⚠️ Require additional privileges for cross-schema operations

## Security & Enterprise Features

### 🔒 Enterprise Security
- **✅ No External Downloads**: Self-contained solution without runtime dependencies
- **✅ Secure Credential Handling**: Environment variables and Kubernetes secrets
- **✅ Transaction Protection**: Autocommit prevents data loss on container termination
- **✅ Supply Chain Security**: No third-party binary downloads or kubectl dependencies
- **✅ Container Security**: Minimal attack surface with proper user privileges

### 📋 Compliance
- **License-Free Data**: All generated data is synthetic and license-free
- **Apache 2.0 Licensed**: Enterprise-friendly open source license
- **Oracle Compatibility**: Works with Oracle Free, Standard, and Enterprise editions
- **Audit-Ready**: Comprehensive logging and verification capabilities

## Platform Support

- **Linux**: Fully supported (native and containerized)
- **macOS**: Fully supported (native and containerized)  
- **Windows**: Supported via WSL or native Python
- **Containers**: Podman and Docker compatible
- **Kubernetes**: OpenShift and Kubernetes with Helm charts

## Quick Help

```bash
# Show help
tpcds-util --help

# Check status
tpcds-util status

# Test database connection
tpcds-util db test

# Show configuration
tpcds-util config show
```

## Contributing

1. Fork the repository
2. Create a feature branch  
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This utility is open source. The synthetic data generated is license-free and safe for enterprise use.

---

**Need Help?** 
- 📖 [Native Usage Guide](docs/native-usage.md)
- 🐳 [Container Usage Guide](docs/container-usage.md)
- 🐛 [Report Issues](https://github.com/rhkp/tpcds-util/issues)