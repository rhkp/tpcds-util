#!/bin/bash
# Oracle Instant Client Download Script for Init Container
# Downloads Oracle client libraries to shared volume at runtime

set -euo pipefail

# Configuration
ORACLE_VERSION="19.23.0.0.0"
ORACLE_DIR="/opt/oracle/instantclient"
BASE_URL="https://download.oracle.com/otn_software/linux/instantclient/1923000"

echo "🏗️  Oracle Instant Client Init Container"
echo "========================================"
echo ""

# Check license acceptance
if [[ "${ACCEPT_ORACLE_LICENSE:-no}" != "yes" ]]; then
    echo "❌ ERROR: Oracle license not accepted"
    echo ""
    echo "   To use Oracle Instant Client, you must accept Oracle's license terms:"
    echo "   https://www.oracle.com/downloads/licenses/instant-client-lic.html"
    echo ""
    echo "   Set environment variable: ACCEPT_ORACLE_LICENSE=yes"
    echo ""
    echo "   Key license requirements:"
    echo "   - Use for business operations and development/testing only"
    echo "   - Do not redistribute or charge end users"  
    echo "   - Comply with export control laws"
    echo ""
    exit 1
fi

echo "✅ Oracle license acceptance confirmed"

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

echo "🔍 Detected architecture: $ARCH ($ARCH_SUFFIX)"

# Check if Oracle client already exists (for cached volumes)
if [[ -f "$ORACLE_DIR/libclntsh.so" ]]; then
    echo "✅ Oracle Instant Client already available in shared volume"
    echo "   Location: $ORACLE_DIR"
    echo "   Verifying installation..."
    
    if "$ORACLE_DIR/sqlplus" -v >/dev/null 2>&1 || [[ -f "$ORACLE_DIR/libclntsh.so" ]]; then
        echo "✅ Oracle client verification successful"
        exit 0
    else
        echo "⚠️  Existing installation appears corrupted, re-downloading..."
        rm -rf "$ORACLE_DIR"/*
    fi
fi

# Package names
BASIC_ZIP="instantclient-basic-${ARCH_SUFFIX}-${ORACLE_VERSION}dbru.zip"
DEVEL_ZIP="instantclient-devel-${ARCH_SUFFIX}-${ORACLE_VERSION}dbru.zip"

echo ""
echo "⬇️  Downloading Oracle Instant Client packages..."
echo "   This may take a few minutes depending on network speed..."

# Download basic package
echo "   📦 Downloading basic package: $BASIC_ZIP"
if ! wget -q --show-progress --timeout=300 "$BASE_URL/$BASIC_ZIP"; then
    echo "❌ Failed to download basic package"
    echo "   URL: $BASE_URL/$BASIC_ZIP"
    echo "   Check network connectivity and Oracle download site availability"
    exit 1
fi

# Download devel package (optional - some architectures may not have it)
echo "   📦 Downloading devel package: $DEVEL_ZIP"
if ! wget -q --show-progress --timeout=300 "$BASE_URL/$DEVEL_ZIP"; then
    echo "⚠️  Devel package not available for $ARCH_SUFFIX architecture"
    echo "   URL: $BASE_URL/$DEVEL_ZIP"
    echo "   Continuing with basic package only (sufficient for most operations)"
    DEVEL_ZIP=""  # Skip devel package extraction
fi

echo ""
echo "📂 Extracting Oracle Instant Client..."

# Extract packages
unzip -q "$BASIC_ZIP"
if [[ -n "$DEVEL_ZIP" ]]; then
    unzip -q "$DEVEL_ZIP"
fi

# Move to shared volume
echo "   📁 Installing to shared volume: $ORACLE_DIR"
mkdir -p "$ORACLE_DIR"
cp -r instantclient_*/* "$ORACLE_DIR/"

# Set permissions
chmod -R 755 "$ORACLE_DIR"

# Create symbolic links
echo "   🔗 Creating symbolic links..."
cd "$ORACLE_DIR"
if [[ ! -e libclntsh.so ]] && ls libclntsh.so.* >/dev/null 2>&1; then
    ln -sf libclntsh.so.* libclntsh.so
fi

# Cleanup temporary files
echo ""
echo "🧹 Cleaning up temporary files..."
cd /tmp
rm -f *.zip
rm -rf instantclient_*

# Verify installation
echo ""
echo "✅ Verifying Oracle Instant Client installation..."
if [[ -f "$ORACLE_DIR/libclntsh.so" ]]; then
    echo "   ✅ libclntsh.so found"
else
    echo "   ❌ libclntsh.so missing"
    exit 1
fi

# List installed files for debugging
echo "   📋 Installed files:"
ls -la "$ORACLE_DIR/" | head -10

echo ""
echo "🎉 Oracle Instant Client initialization complete!"
echo "   Location: $ORACLE_DIR"
echo "   Version: $ORACLE_VERSION"
echo "   Architecture: $ARCH_SUFFIX"
echo ""
echo "   Main application container can now use Oracle client libraries"
echo "   Environment variables:"
echo "   - ORACLE_HOME=$ORACLE_DIR"
echo "   - LD_LIBRARY_PATH includes $ORACLE_DIR"
echo ""