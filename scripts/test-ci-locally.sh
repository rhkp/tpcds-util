#!/bin/bash
set -e

echo "🧪 Local CI/CD Pipeline Testing Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if act is installed
if ! command -v act &> /dev/null; then
    print_error "act is not installed. Install with: brew install act"
    exit 1
fi

# Check if Docker/Podman is running
if ! command -v docker &> /dev/null && ! command -v podman &> /dev/null; then
    print_error "Docker or Podman is required for container testing"
    exit 1
fi

# Create artifacts directory
mkdir -p artifacts

print_success "Prerequisites check passed"

# Function to test individual workflows
test_workflow() {
    local workflow=$1
    local job=$2
    local description=$3
    
    print_status "Testing $description..."
    
    if act -W .github/workflows/$workflow --job $job --dryrun; then
        print_success "$description - Dry run passed"
        
        # Ask user if they want to run the actual workflow
        read -p "Run actual workflow for $description? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if act -W .github/workflows/$workflow --job $job; then
                print_success "$description - Actual run passed"
            else
                print_error "$description - Actual run failed"
                return 1
            fi
        fi
    else
        print_error "$description - Dry run failed"
        return 1
    fi
}

# Menu for testing different components
echo ""
echo "Select what to test:"
echo "1. Test pipeline (unit tests + integration tests)"
echo "2. Lint pipeline (code quality checks)"
echo "3. Security pipeline (vulnerability scanning)"
echo "4. Build pipeline (container builds - dry run only)"
echo "5. All test workflows"
echo "6. Individual component testing (recommended for development)"
echo "7. Exit"

read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        print_status "Testing test pipeline..."
        test_workflow "test.yml" "test" "Unit and Integration Tests"
        ;;
    2)
        print_status "Testing lint pipeline..."
        test_workflow "test.yml" "lint" "Code Quality Checks"
        ;;
    3)
        print_status "Testing security pipeline..."
        test_workflow "test.yml" "security" "Security Scanning"
        ;;
    4)
        print_status "Testing build pipeline (dry run)..."
        print_warning "Build pipeline requires Quay.io secrets, running dry run only"
        act -W .github/workflows/build-push.yml --dryrun
        ;;
    5)
        print_status "Testing all workflows..."
        test_workflow "test.yml" "test" "Unit and Integration Tests"
        test_workflow "test.yml" "lint" "Code Quality Checks"
        test_workflow "test.yml" "security" "Security Scanning"
        ;;
    6)
        print_status "Starting individual component testing..."
        exec ./scripts/test-components-locally.sh
        ;;
    7)
        print_status "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

print_success "Local CI/CD testing completed!"
echo ""
echo "📝 Next steps:"
echo "- Review any errors above"
echo "- Fix issues in code/workflows"
echo "- Test individual components with: ./scripts/test-components-locally.sh"
echo "- When ready, push to GitHub to trigger actual CI/CD"