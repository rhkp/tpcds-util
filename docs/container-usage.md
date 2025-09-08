# Container TPC-DS Utility Usage Guide

This guide covers using the TPC-DS utility in containerized environments with Podman or Docker.

## Prerequisites

- **Podman** or **Docker** installed
- **Oracle database** (containerized or external)
- **Network connectivity** between container and database

## Setup Environment Variables

**Before running any commands, set your database password as an environment variable:**

```bash
# Set your Oracle database password
export TPCDS_DB_PASSWORD="<your_secret_password_here>"
```

### Security Note

**⚠️ Never hardcode passwords in scripts or documentation!**

Examples in this guide use `<your_secret_password_here>` placeholder. Always replace with your actual password:

```bash
# ✅ Good - Use environment variables
export TPCDS_DB_PASSWORD="MySecureOraclePass123"

# ❌ Bad - Never hardcode passwords in commands
--env="TPCDS_DB_PASSWORD=MySecureOraclePass123"
```

## Container Images

The utility is available as a container image:

```bash
# Pull latest image
podman pull quay.io/tpcds/tpcds-util:latest

# Or build locally
podman build -t tpcds-util -f Containerfile .
```

## Deployment Approaches

Choose the approach that best fits your environment:

### 🏗️ Approach 1: Full Stack with Podman Compose
**Best for**: Local development, isolated testing, demos

Includes both Oracle database and tpcds-util in containers.

### ⚡ Approach 2: Individual Commands with External Database  
**Best for**: Existing database infrastructure, production deployments, CI/CD

Uses containerized tpcds-util with external Oracle database.

---

## Approach 1: Full Stack with Podman Compose

Perfect for creating a complete isolated environment with both database and utility.

### 1. Start Full Stack

```bash
# Set environment variables
export TPCDS_DB_PASSWORD=<your_secret_password_here>
export ORACLE_PWD=<your_secret_password_here>

# Start both Oracle DB and tpcds-util containers
podman-compose up -d

# Wait for Oracle to be ready (can take 2-3 minutes)
podman logs -f oracle-test-db
```

### 2. Configure for Container Database

```bash
# Configure to use the containerized Oracle database
podman-compose exec tpcds-util tpcds-util config set \
  --host oracle-test-db \
  --service-name FREE \
  --username system \
  --schema-name DEMO_SCHEMA

# Test connection
podman-compose exec tpcds-util tpcds-util db test
```

### 3. Complete Workflow

```bash
# Create schema
podman-compose exec tpcds-util tpcds-util schema create

# Generate data
podman-compose exec tpcds-util tpcds-util generate data --scale 1

# Load data
podman-compose exec tpcds-util tpcds-util load data

# Verify
podman-compose exec tpcds-util tpcds-util db info
```

### 4. Cleanup

```bash
# Stop services
podman-compose down

# Remove volumes (optional - will delete all data)
podman-compose down -v
```

---

## Approach 2: Individual Commands with External Database

Perfect for using containerized tpcds-util with existing database infrastructure.

### 1. Configure for External Database

```bash
# For host database (macOS/Windows)
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=$TPCDS_DB_PASSWORD \
  quay.io/tpcds/tpcds-util:latest \
  config set --host host.containers.internal --schema-name CONTAINER_SCHEMA

# For Linux host database
podman run --rm --network host \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  config set --host localhost --schema-name CONTAINER_SCHEMA

# For external database
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  config set --host mydb.example.com --schema-name CONTAINER_SCHEMA
```

### 2. Complete Workflow

```bash
# Set password environment variable first
export TPCDS_DB_PASSWORD=<your_secret_password_here>

# Test connection
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=$TPCDS_DB_PASSWORD \
  quay.io/tpcds/tpcds-util:latest \
  db test

# Create schema (mount schema file)
podman run --rm \
  -v .:/workspace \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=$TPCDS_DB_PASSWORD \
  quay.io/tpcds/tpcds-util:latest \
  schema create --schema-file /workspace/oracle_tpcds_schema.sql

# Generate data to mounted directory
podman run --rm \
  -v ./container_data:/home/tpcds/tpcds_data \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  quay.io/tpcds/tpcds-util:latest \
  generate data --scale 1

# Load generated data
podman run --rm \
  -v ./container_data:/home/tpcds/tpcds_data \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=$TPCDS_DB_PASSWORD \
  quay.io/tpcds/tpcds-util:latest \
  load data

# Verify results
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=$TPCDS_DB_PASSWORD \
  quay.io/tpcds/tpcds-util:latest \
  db info
```

---

## When to Use Each Approach

### 🏗️ Use Approach 1 (Podman Compose) When:
- ✅ **Local development** and testing
- ✅ **Demo environments** for presentations
- ✅ **Isolated testing** without affecting other systems
- ✅ **Learning TPC-DS** concepts
- ✅ **Quick proof-of-concepts**

### ⚡ Use Approach 2 (Individual Commands) When:
- ✅ **Production deployments** with existing Oracle infrastructure
- ✅ **CI/CD pipelines** requiring specific data loading
- ✅ **Integration testing** against real databases
- ✅ **Kubernetes/OpenShift** deployments
- ✅ **Multiple environment** management (dev/test/prod)

## Container Configuration

### Environment Variables

```bash
# Required
export TPCDS_DB_PASSWORD=<your_secret_password_here>

# Optional
export ORACLE_HOME=/opt/oracle/instantclient
export LD_LIBRARY_PATH=/opt/oracle/instantclient
```

### Volume Mounts

```bash
# Configuration persistence
-v tpcds-config:/home/tpcds/.tpcds-util

# Data output
-v ./tpcds_data:/home/tpcds/tpcds_data

# Schema files (for creation)
-v .:/workspace
```

### Network Configuration

#### For Local Database (macOS/Windows)

```bash
# Use host.containers.internal
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  config set --host host.containers.internal
```

#### For Linux Host Database

```bash
# Use host networking
podman run --rm --network host \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  config set --host localhost
```

#### For External Database

```bash
# Use database hostname/IP
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  config set --host mydb.example.com
```

## Container Operations

### Database Operations

```bash
# Test connection
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  db test

# Show configuration
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  quay.io/tpcds/tpcds-util:latest \
  config show

# Check database info
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  db info
```

### Schema Management

```bash
# Create schema (mount schema file)
podman run --rm \
  -v .:/workspace \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  schema create --schema-file /workspace/oracle_tpcds_schema.sql

# Drop schema
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  schema drop --confirm
```

### Data Generation

```bash
# Generate data to mounted volume
podman run --rm \
  -v ./tpcds_data:/home/tpcds/tpcds_data \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  quay.io/tpcds/tpcds-util:latest \
  generate data --scale 1

# Generate with custom settings
podman run --rm \
  -v ./output:/home/tpcds/tpcds_data \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  quay.io/tpcds/tpcds-util:latest \
  generate data --scale 10 --parallel 8
```

### Data Loading

```bash
# Load data from mounted directory
podman run --rm \
  -v ./tpcds_data:/home/tpcds/tpcds_data \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  load data

# Load specific table
podman run --rm \
  -v ./tpcds_data:/home/tpcds/tpcds_data \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD=<your_secret_password_here> \
  quay.io/tpcds/tpcds-util:latest \
  load data --table customer
```

## Production Kubernetes Deployment

### Using Kubernetes Jobs

```yaml
# kubernetes/tpcds-schema-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: tpcds-schema-setup
spec:
  template:
    spec:
      containers:
      - name: tpcds-util
        image: quay.io/tpcds/tpcds-util:latest
        env:
        - name: TPCDS_DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: oracle-secret
              key: password
        command: ["tpcds-util"]
        args: 
        - "config"
        - "set"
        - "--host"
        - "oracle-service"
        - "--schema-name"
        - "TPCDS_PROD"
        volumeMounts:
        - name: config-volume
          mountPath: /home/tpcds/.tpcds-util
      volumes:
      - name: config-volume
        persistentVolumeClaim:
          claimName: tpcds-config
      restartPolicy: Never
```

```yaml
# kubernetes/tpcds-data-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: tpcds-data-generation
spec:
  template:
    spec:
      containers:
      - name: tpcds-util
        image: quay.io/tpcds/tpcds-util:latest
        env:
        - name: TPCDS_DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: oracle-secret
              key: password
        command: ["tpcds-util"]
        args: ["schema", "create"]
        volumeMounts:
        - name: config-volume
          mountPath: /home/tpcds/.tpcds-util
        - name: data-volume
          mountPath: /home/tpcds/tpcds_data
        - name: schema-volume
          mountPath: /workspace
      volumes:
      - name: config-volume
        persistentVolumeClaim:
          claimName: tpcds-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: tpcds-data
      - name: schema-volume
        configMap:
          name: tpcds-schema
      restartPolicy: Never
```

### Deploy Jobs

```bash
# Create namespace
kubectl create namespace tpcds

# Deploy configuration
kubectl apply -f kubernetes/tpcds-schema-job.yaml -n tpcds
kubectl apply -f kubernetes/tpcds-data-job.yaml -n tpcds

# Monitor progress
kubectl logs -f job/tpcds-schema-setup -n tpcds
kubectl logs -f job/tpcds-data-generation -n tpcds
```

## Integration with Oracle Helm Chart

When using with the Oracle 23ai Helm chart:

### 1. Deploy Oracle Database

```bash
# Deploy Oracle 23ai
helm install oracle23ai /path/to/oracle23ai/helm \
  --set secret.password="<your_secret_password_here>"
```

### 2. Configure TPC-DS for Oracle Service

```bash
# Configure for Kubernetes Oracle service
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  -e TPCDS_DB_PASSWORD="<your_secret_password_here>" \
  quay.io/tpcds/tpcds-util:latest \
  config set \
  --host oracle23ai \
  --service-name FREEPDB1 \
  --username system \
  --schema-name TPCDS_AI
```

### 3. Run Data Generation

```bash
# Generate and load data for AI workloads
kubectl run tpcds-setup --rm -it \
  --image=quay.io/tpcds/tpcds-util:latest \
  --env="TPCDS_DB_PASSWORD=<your_secret_password_here>" \
  -- schema create

kubectl run tpcds-load --rm -it \
  --image=quay.io/tpcds/tpcds-util:latest \
  --env="TPCDS_DB_PASSWORD=<your_secret_password_here>" \
  -- load data --scale 10
```

## Container Compose Configuration

The `podman-compose.yml` file provides a complete setup:

```yaml
version: '3.8'

services:
  # Oracle database (optional)
  oracle-db:
    image: container-registry.oracle.com/database/free:23.4.0.0
    environment:
      - ORACLE_PWD=${ORACLE_PWD:-TestPassword123}
    ports:
      - "1521:1521"
    volumes:
      - oracle-data:/opt/oracle/oradata

  # TPC-DS utility
  tpcds-util:
    build:
      context: .
      dockerfile: Containerfile
    image: quay.io/tpcds/tpcds-util:latest
    depends_on:
      - oracle-db
    volumes:
      - ./tpcds_data:/home/tpcds/tpcds_data
      - tpcds-config:/home/tpcds/.tpcds-util
    environment:
      - TPCDS_DB_PASSWORD=${TPCDS_DB_PASSWORD}
    command: ["--help"]

volumes:
  tpcds-config:
  oracle-data:
```

## Troubleshooting Containers

### Connection Issues

```bash
# Check network connectivity
podman run --rm \
  --entrypoint /bin/bash \
  quay.io/tpcds/tpcds-util:latest \
  -c "ping -c 3 your-db-host"

# Check Oracle port
podman run --rm \
  --entrypoint /bin/bash \
  quay.io/tpcds/tpcds-util:latest \
  -c "nc -zv your-db-host 1521"
```

### Configuration Issues

```bash
# Check container configuration
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  quay.io/tpcds/tpcds-util:latest \
  config show

# Reset configuration
podman volume rm tpcds-config
```

### Permission Issues

```bash
# Check volume permissions
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  --entrypoint /bin/bash \
  quay.io/tpcds/tpcds-util:latest \
  -c "ls -la /home/tpcds/.tpcds-util"

# Fix volume ownership
podman run --rm \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  --user root \
  --entrypoint /bin/bash \
  quay.io/tpcds/tpcds-util:latest \
  -c "chown -R 1001:1001 /home/tpcds/.tpcds-util"
```

## Best Practices

### Security

```bash
# Use secrets for passwords
echo "<your_secret_password_here>" | podman secret create db-password -

# Use secret in container
podman run --rm \
  --secret db-password,type=env,target=TPCDS_DB_PASSWORD \
  quay.io/tpcds/tpcds-util:latest \
  db test
```

### Performance

```bash
# Use specific CPU/memory limits
podman run --rm \
  --cpus="2.0" \
  --memory="4g" \
  -v tpcds-config:/home/tpcds/.tpcds-util \
  quay.io/tpcds/tpcds-util:latest \
  generate data --scale 100
```

### Data Management

```bash
# Use named volumes for persistence
podman volume create tpcds-data
podman volume create tpcds-config

# Backup configuration
podman run --rm \
  -v tpcds-config:/source \
  -v ./backup:/backup \
  alpine tar czf /backup/tpcds-config.tar.gz -C /source .
```

---

**Next Steps:**
- 📖 [Native Usage Guide](native-usage.md) - For development setup
- 🏠 [Main README](../README.md) - Back to overview
- 🎯 [Oracle Helm Chart Integration](/path/to/oracle23ai/helm) - Production deployment