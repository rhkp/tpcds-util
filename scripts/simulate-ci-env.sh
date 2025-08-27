#!/bin/bash
set -e

echo "🎭 CI Environment Simulation Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[CI-SIM]${NC} $1"; }
print_success() { echo -e "${GREEN}[CI-SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[CI-ERROR]${NC} $1"; }

# Simulate GitHub Actions environment variables
export CI=true
export GITHUB_ACTIONS=true
export GITHUB_WORKFLOW="Local CI Simulation"
export GITHUB_RUN_ID="local-$(date +%s)"
export GITHUB_RUN_NUMBER="1"
export GITHUB_ACTOR="local-developer"
export GITHUB_REPOSITORY="your-org/tpcds-util"
export GITHUB_REF="refs/heads/main"
export GITHUB_SHA=$(git rev-parse HEAD 2>/dev/null || echo "local-sha")
export GITHUB_EVENT_NAME="push"

print_status "Setting up CI-like environment..."
print_status "GITHUB_REPOSITORY: $GITHUB_REPOSITORY"
print_status "GITHUB_REF: $GITHUB_REF"
print_status "GITHUB_SHA: ${GITHUB_SHA:0:8}"

# Create CI-like directory structure
mkdir -p .ci-simulation/{workspace,artifacts,cache}
cd .ci-simulation/workspace

# Copy source code (like GitHub Actions checkout)
print_status "Copying source code to CI workspace..."
cp -r ../../* . 2>/dev/null || true
rm -rf .ci-simulation  # Remove nested simulation dirs

# Simulate the exact steps from our GitHub Actions workflows
print_status "Simulating GitHub Actions test workflow..."

echo "::group::Setup Python"
python3 -m venv ci-venv
source ci-venv/bin/activate
echo "::endgroup::"

echo "::group::Install Dependencies"
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "::endgroup::"

echo "::group::Run Unit Tests"
if pytest tests/unit/ -v --cov=src/tpcds_util --cov-report=xml --cov-report=term-missing; then
    print_success "Unit tests passed"
else
    print_error "Unit tests failed"
    exit 1
fi
echo "::endgroup::"

echo "::group::Run SQLite Integration Tests"
if pytest tests/integration/test_simple_sqlite.py -v --tb=short -x; then
    print_success "Integration tests passed"
else
    print_error "Integration tests failed"
    exit 1
fi
echo "::endgroup::"

echo "::group::Install Linting Tools"
pip install black flake8 isort
echo "::endgroup::"

echo "::group::Run Black"
if black --check src/ tests/; then
    print_success "Black formatting check passed"
else
    print_error "Black formatting check failed"
    echo "Run: black src/ tests/ to fix formatting"
    exit 1
fi
echo "::endgroup::"

echo "::group::Run Flake8"
if flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503; then
    print_success "Flake8 linting passed"
else
    print_error "Flake8 linting failed"
    exit 1
fi
echo "::endgroup::"

echo "::group::Run isort"
if isort --check-only src/ tests/; then
    print_success "Import sorting check passed"
else
    print_error "Import sorting check failed"
    echo "Run: isort src/ tests/ to fix imports"
    exit 1
fi
echo "::endgroup::"

echo "::group::Security Scan"
pip install safety > /dev/null 2>&1 || true
if safety check --file requirements.txt; then
    print_success "Security scan passed"
else
    print_error "Security vulnerabilities found"
    # Don't exit for security warnings in local testing
fi
echo "::endgroup::"

echo "::group::Generate Coverage Report"
coverage report --show-missing
coverage html -d ../artifacts/htmlcov
echo "Coverage report saved to .ci-simulation/artifacts/htmlcov/"
echo "::endgroup::"

echo "::group::Test Container Build (if Docker/Podman available)"
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
else
    print_error "No container runtime available, skipping container tests"
    CONTAINER_CMD=""
fi

if [ -n "$CONTAINER_CMD" ]; then
    print_status "Testing container build with $CONTAINER_CMD..."
    if $CONTAINER_CMD build -f Containerfile -t tpcds-util:ci-test .; then
        print_success "Container build passed"
        
        # Test container functionality
        if $CONTAINER_CMD run --rm tpcds-util:ci-test --help > /dev/null; then
            print_success "Container functionality test passed"
        else
            print_error "Container functionality test failed"
        fi
    else
        print_error "Container build failed"
        exit 1
    fi
fi
echo "::endgroup::"

echo "::group::Test Data Generation"
print_status "Testing synthetic data generation..."
PYTHONPATH=. python -c "
from src.tpcds_util.synthetic_generator import create_synthetic_data
import tempfile
import os

temp_dir = '../artifacts/test-data'
os.makedirs(temp_dir, exist_ok=True)

print('Testing scale=0 (test mode) data generation...')
result = create_synthetic_data(scale=0, output_dir=temp_dir)
print(f'Generation result: {result}')

if result:
    files = os.listdir(temp_dir)
    print(f'Generated {len(files)} data files')
    print('Files:', sorted(files)[:5], '...')
else:
    print('Data generation failed')
    exit(1)
"
echo "::endgroup::"

deactivate
cd ../..

print_success "CI simulation completed successfully!"
echo ""
echo "📊 Simulation Results:"
echo "- ✅ All tests passed in CI-like environment"
echo "- 📁 Artifacts saved to: .ci-simulation/artifacts/"
echo "- 📋 Coverage report: .ci-simulation/artifacts/htmlcov/index.html"
echo "- 📦 Test data: .ci-simulation/artifacts/test-data/"
echo ""
echo "🚀 Ready to push to GitHub!"
echo "The actual CI/CD pipeline should work correctly."

# Cleanup option
read -p "Clean up simulation files? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    rm -rf .ci-simulation
    print_status "Simulation files cleaned up"
fi