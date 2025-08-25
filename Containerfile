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

# Oracle Instant Client will be provided by init container at runtime
# This approach ensures licensing compliance while supporting OpenShift deployments
# See: https://www.oracle.com/downloads/licenses/instant-client-lic.html
#
# Oracle client libraries will be downloaded to shared volume by init container
# Users accept Oracle license terms through environment variable ACCEPT_ORACLE_LICENSE=yes
#
# Set Oracle environment variables (client provided by init container)
ENV ORACLE_HOME=/opt/oracle/instantclient
ENV LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
ENV PATH=$ORACLE_HOME:$PATH

# Create application directory
WORKDIR /app

# Copy Python requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/
COPY setup.py .
COPY README.md .
COPY oracle_tpcds_schema.sql .

# Install the tpcds-util package
RUN pip3 install --no-cache-dir -e .

# Create non-root user for security
RUN useradd -m -u 1001 tpcds && \
    chown -R tpcds:tpcds /app

# Switch to non-root user
USER tpcds

# Create config directory
RUN mkdir -p /home/tpcds/.tpcds-util

# Set default working directory for data generation
WORKDIR /home/tpcds

# Expose any ports if needed (none for CLI tool)
# EXPOSE 8080

# Set default entrypoint
ENTRYPOINT ["tpcds-util"]

# Default command
CMD ["--help"]