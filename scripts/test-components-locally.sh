#!/bin/bash
set -e

echo "🔧 Individual Component Testing Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to run tests with timing
run_timed_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Running $test_name..."
    start_time=$(date +%s)
    
    if eval "$test_command"; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        print_success "$test_name completed in ${duration}s"
        return 0
    else
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        print_error "$test_name failed after ${duration}s"
        return 1
    fi
}

# Test 1: Python Dependencies
test_dependencies() {
    print_status "Testing Python dependencies..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    run_timed_test "Dependency Installation" \
        "pip install --upgrade pip && pip install -r requirements.txt"
    
    run_timed_test "Development Dependencies" \
        "pip install black flake8 isort pytest-cov"
    
    deactivate
}

# Test 2: Unit Tests
test_unit_tests() {
    print_status "Testing unit tests..."
    source venv/bin/activate
    
    run_timed_test "Unit Tests with Coverage" \
        "PYTHONPATH=. pytest tests/unit/ -v --cov=src/tpcds_util --cov-report=term-missing --cov-report=html:htmlcov"
    
    print_status "Coverage report generated in htmlcov/"
    deactivate
}

# Test 3: SQLite Integration Tests  
test_integration_tests() {
    print_status "Testing SQLite integration tests..."
    source venv/bin/activate
    
    run_timed_test "Fast SQLite Integration Tests" \
        "PYTHONPATH=. pytest tests/integration/test_simple_sqlite.py -v --tb=short"
    
    deactivate
}

# Test 4: Code Quality
test_code_quality() {
    print_status "Testing code quality..."
    source venv/bin/activate
    
    run_timed_test "Black Code Formatting Check" \
        "black --check src/ tests/"
    
    run_timed_test "Flake8 Linting" \
        "flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503"
    
    run_timed_test "Import Sorting Check" \
        "isort --check-only src/ tests/"
    
    deactivate
}

# Test 5: Security Scanning
test_security() {
    print_status "Testing security scanning..."
    source venv/bin/activate
    
    # Install safety if not present
    pip install safety > /dev/null 2>&1 || true
    
    run_timed_test "Python Dependency Security Scan" \
        "safety check --file requirements.txt || true"
    
    # Test Trivy if available
    if command -v trivy &> /dev/null; then
        run_timed_test "Filesystem Security Scan" \
            "trivy fs . --severity HIGH,CRITICAL || true"
    else
        print_warning "Trivy not installed, skipping filesystem scan"
    fi
    
    deactivate
}

# Test 6: Container Build
test_container_build() {
    print_status "Testing container builds..."
    
    # Check if podman or docker is available
    if command -v podman &> /dev/null; then
        CONTAINER_CMD="podman"
    elif command -v docker &> /dev/null; then
        CONTAINER_CMD="docker"
    else
        print_error "Neither podman nor docker is available"
        return 1
    fi
    
    print_status "Using $CONTAINER_CMD for container builds"
    
    # Test main container build
    run_timed_test "Main Container Build" \
        "$CONTAINER_CMD build -f Containerfile -t tpcds-util:test-main ."
    
    # Test Oracle init container build
    if [ -f "Containerfile.oracle-init" ]; then
        run_timed_test "Oracle Init Container Build" \
            "$CONTAINER_CMD build -f Containerfile.oracle-init -t tpcds-util:test-oracle-init ."
    fi
    
    # Test container functionality
    print_status "Testing container functionality..."
    
    run_timed_test "Container Help Command" \
        "$CONTAINER_CMD run --rm tpcds-util:test-main --help"
    
    run_timed_test "Container Version Command" \
        "$CONTAINER_CMD run --rm tpcds-util:test-main --version || true"
}

# Test 7: Synthetic Data Generation
test_data_generation() {
    print_status "Testing synthetic data generation..."
    source venv/bin/activate
    
    # Create temp directory for test data
    TEST_DIR=$(mktemp -d)
    
    run_timed_test "Scale=0 (Test Mode) Data Generation" \
        "PYTHONPATH=. python -c \"
from src.tpcds_util.synthetic_generator import create_synthetic_data
import tempfile
result = create_synthetic_data(scale=0, output_dir='$TEST_DIR')
print(f'Generation result: {result}')
import os
files = os.listdir('$TEST_DIR')
print(f'Files created: {len(files)}')
print(f'Files: {sorted(files)[:5]}...')
\""
    
    # Check if files were created
    if [ "$(ls -A $TEST_DIR)" ]; then
        print_success "Data files generated successfully"
        ls -la $TEST_DIR | head -10
    else
        print_error "No data files generated"
    fi
    
    # Cleanup
    rm -rf $TEST_DIR
    deactivate
}

# Test 8: End-to-End Workflow
test_end_to_end() {
    print_status "Running end-to-end workflow test..."
    
    # Run all critical tests in sequence
    test_dependencies && \
    test_unit_tests && \
    test_integration_tests && \
    test_code_quality && \
    test_data_generation
    
    if [ $? -eq 0 ]; then
        print_success "End-to-end workflow test passed!"
        return 0
    else
        print_error "End-to-end workflow test failed!"
        return 1
    fi
}

# Main menu
echo ""
echo "Select component to test:"
echo "1. Python Dependencies"
echo "2. Unit Tests" 
echo "3. SQLite Integration Tests"
echo "4. Code Quality (linting)"
echo "5. Security Scanning"
echo "6. Container Builds"
echo "7. Data Generation"
echo "8. End-to-End Workflow"
echo "9. All Components"
echo "10. Exit"

read -p "Enter your choice (1-10): " choice

case $choice in
    1) test_dependencies ;;
    2) test_unit_tests ;;
    3) test_integration_tests ;;
    4) test_code_quality ;;
    5) test_security ;;
    6) test_container_build ;;
    7) test_data_generation ;;
    8) test_end_to_end ;;
    9) 
        print_status "Running all component tests..."
        test_dependencies && \
        test_unit_tests && \
        test_integration_tests && \
        test_code_quality && \
        test_security && \
        test_data_generation && \
        test_container_build
        ;;
    10) 
        print_status "Exiting..."
        exit 0 
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

print_success "Component testing completed!"
echo ""
echo "📊 Test Results Summary:"
echo "- Check above output for any failed tests"
echo "- Coverage report: htmlcov/index.html"
echo "- Fix any issues before pushing to GitHub"