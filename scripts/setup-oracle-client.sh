#!/bin/bash
# Setup Oracle Instant Client for tpcds-util container
# This script helps users download and install Oracle client libraries legally

set -euo pipefail

ORACLE_VERSION="19.23.0.0.0"
ORACLE_DIR="/opt/oracle/instantclient"
TEMP_DIR="/tmp/oracle-install"

echo "🔧 Oracle Instant Client Setup for TPC-DS Utility"
echo "=================================================="
echo ""
echo "⚠️  IMPORTANT LICENSING NOTICE:"
echo "   By proceeding, you agree to Oracle's Instant Client license terms:"
echo "   https://www.oracle.com/downloads/licenses/instant-client-lic.html"
echo ""
echo "   Key requirements:"
echo "   - Use for business operations and development/testing only"
echo "   - Do not redistribute or charge end users"
echo "   - Comply with export control laws"
echo ""

read -p "Do you accept Oracle's license terms? (y/N): " accept_license
if [[ ! "$accept_license" =~ ^[Yy]$ ]]; then
    echo "❌ License not accepted. Exiting."
    exit 1
fi

echo ""
echo "📥 Detecting system architecture..."

# Detect architecture
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        ARCH_SUFFIX="linux.x64"
        ;;
    aarch64|arm64)
        ARCH_SUFFIX="linux.arm64"
        ;;
    *)
        echo "❌ Unsupported architecture: $ARCH"
        echo "   Supported: x86_64, aarch64/arm64"
        exit 1
        ;;
esac

echo "✅ Architecture: $ARCH ($ARCH_SUFFIX)"

# Create directories
echo ""
echo "📁 Creating directories..."
sudo mkdir -p "$ORACLE_DIR"
mkdir -p "$TEMP_DIR"

# Download URLs
BASE_URL="https://download.oracle.com/otn_software/linux/instantclient/1923000"
BASIC_ZIP="instantclient-basic-${ARCH_SUFFIX}-${ORACLE_VERSION}dbru.zip"
DEVEL_ZIP="instantclient-devel-${ARCH_SUFFIX}-${ORACLE_VERSION}dbru.zip"

echo ""
echo "⬇️  Downloading Oracle Instant Client packages..."
echo "   This may take a few minutes..."

cd "$TEMP_DIR"

# Download basic package
echo "   Downloading basic package..."
if ! wget -q --show-progress "$BASE_URL/$BASIC_ZIP"; then
    echo "❌ Failed to download basic package"
    echo "   Please manually download from:"
    echo "   https://www.oracle.com/database/technologies/instant-client.html"
    exit 1
fi

# Download devel package
echo "   Downloading devel package..."
if ! wget -q --show-progress "$BASE_URL/$DEVEL_ZIP"; then
    echo "❌ Failed to download devel package"
    exit 1
fi

echo ""
echo "📦 Extracting packages..."

# Extract packages
unzip -q "$BASIC_ZIP"
unzip -q "$DEVEL_ZIP"

# Move to final location
echo "   Installing to $ORACLE_DIR..."
sudo cp -r instantclient_*/* "$ORACLE_DIR/"
sudo chown -R root:root "$ORACLE_DIR"
sudo chmod -R 755 "$ORACLE_DIR"

# Create symbolic links if needed
echo "   Creating symbolic links..."
cd "$ORACLE_DIR"
if [[ ! -e libclntsh.so ]]; then
    sudo ln -sf libclntsh.so.* libclntsh.so
fi

# Cleanup
echo ""
echo "🧹 Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

# Verify installation
echo ""
echo "✅ Verifying installation..."
if [[ -f "$ORACLE_DIR/libclntsh.so" ]]; then
    echo "   Oracle Instant Client installed successfully!"
    echo "   Location: $ORACLE_DIR"
    echo "   Version: $ORACLE_VERSION"
else
    echo "❌ Installation verification failed"
    exit 1
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Build the container:"
echo "   podman build -t tpcds-util -f Containerfile ."
echo ""
echo "2. Run with Oracle client mounted:"
echo "   podman run -v $ORACLE_DIR:$ORACLE_DIR:ro tpcds-util"
echo ""
echo "3. Or use podman-compose:"
echo "   podman-compose up tpcds-util"
echo ""
echo "📋 Environment variables set:"
echo "   ORACLE_HOME=$ORACLE_DIR"
echo "   Add to your shell profile:"
echo "   export ORACLE_HOME=$ORACLE_DIR"
echo "   export LD_LIBRARY_PATH=\$ORACLE_HOME:\$LD_LIBRARY_PATH"
echo ""