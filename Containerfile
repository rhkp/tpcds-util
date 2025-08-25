# Use Red Hat UBI as the base image for enterprise compatibility
FROM registry.access.redhat.com/ubi9/ubi:latest

# Set labels for better container management
LABEL name="tpcds-util" \
      version="1.0.0" \
      description="TPC-DS utility for synthetic data generation and Oracle database management" \
      maintainer="TPC-DS Utility Team" \
      license="Apache-2.0"

# Install system dependencies and Oracle prerequisites
RUN dnf update -y && \
    dnf install -y \
        python3 \
        python3-pip \
        python3-devel \
        gcc \
        libaio \
        wget \
        unzip \
        which \
        procps \
    && dnf clean all

# Set environment variables for Oracle client (will use thick mode if available)
ENV ORACLE_HOME=/opt/oracle/instantclient
ENV LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
ENV PATH=$ORACLE_HOME:$PATH

# Note: Oracle client will use thin mode by default (no client libraries needed)
# For thick mode support, mount Oracle client libraries from host or init container

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY setup.py .
COPY README.md .
COPY oracle_tpcds_schema.sql .

# Install the application
RUN pip3 install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1001 tpcds && \
    chown -R tpcds:tpcds /app

# Switch to non-root user
USER tpcds

# Create user directories
RUN mkdir -p /home/tpcds/.tpcds-util

# Set working directory to user home
WORKDIR /home/tpcds

# Set entrypoint
ENTRYPOINT ["tpcds-util"]
CMD ["--help"]