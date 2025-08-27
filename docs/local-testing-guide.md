# Local CI/CD Testing Guide

This guide shows you how to test the CI/CD pipeline locally before pushing to GitHub, saving time and catching issues early.

## 🎯 Quick Start (Recommended)

```bash
# Full CI environment simulation (fastest way to validate everything)
./scripts/simulate-ci-env.sh
```

This script simulates the exact GitHub Actions environment and runs all pipeline steps locally.

## 🔧 Available Testing Methods

### Method 1: Complete CI Simulation ⭐ (Recommended)
Simulates the exact GitHub Actions environment with all steps.

```bash
./scripts/simulate-ci-env.sh
```

**What it does:**
- ✅ Sets up CI environment variables
- ✅ Runs unit tests with coverage
- ✅ Runs SQLite integration tests  
- ✅ Performs code quality checks
- ✅ Tests container builds
- ✅ Generates coverage reports
- ✅ Tests data generation

**Time:** ~2-3 minutes

### Method 2: GitHub Actions Local Runner
Uses `act` to run actual GitHub Actions workflows locally.

```bash
# Install act (if not already installed)
brew install act

# Run the interactive testing script
./scripts/test-ci-locally.sh
```

**Options:**
- Test individual workflows (test, lint, security)
- Dry run mode for build pipeline
- Full workflow testing

**Time:** ~5-10 minutes

### Method 3: Individual Component Testing
Test specific components during development.

```bash
./scripts/test-components-locally.sh
```

**Components:**
1. Python Dependencies
2. Unit Tests
3. SQLite Integration Tests
4. Code Quality (linting)
5. Security Scanning
6. Container Builds
7. Data Generation
8. End-to-End Workflow

**Time:** ~1-5 minutes per component

## 🚀 Common Testing Scenarios

### Scenario 1: Pre-Commit Testing
Before committing changes, run quick validation:

```bash
# Quick component test
./scripts/test-components-locally.sh
# Choose option 8 (End-to-End Workflow)
```

### Scenario 2: Pre-Push Testing  
Before pushing to GitHub, validate the full pipeline:

```bash
# Full CI simulation
./scripts/simulate-ci-env.sh
```

### Scenario 3: Debugging Workflow Issues
When GitHub Actions are failing:

```bash
# Test specific workflow
./scripts/test-ci-locally.sh
# Choose the failing workflow to debug
```

### Scenario 4: Container Development
When working on Containerfiles:

```bash
# Test container builds only
./scripts/test-components-locally.sh
# Choose option 6 (Container Builds)
```

## 📊 Output Examples

### Successful Test Run
```
🧪 Local CI/CD Pipeline Testing Script
======================================
✅ [SUCCESS] Unit and Integration Tests - Actual run passed
✅ [SUCCESS] Code Quality Checks - Actual run passed  
✅ [SUCCESS] Security Scanning - Actual run passed

📝 Next steps:
- Review any errors above
- When ready, push to GitHub to trigger actual CI/CD
```

### Failed Test Run
```
❌ [ERROR] Code Quality Checks - Actual run failed
💡 Fix required: Run 'black src/ tests/' to fix formatting

📝 Next steps:
- Fix issues in code/workflows
- Test again before pushing
```

## 🐳 Container Testing

### Local Container Builds
```bash
# Build main application container
podman build -f Containerfile -t tpcds-util:local .

# Build Oracle init container  
podman build -f Containerfile.oracle-init -t tpcds-util-oracle-init:local .

# Test container functionality
podman run --rm tpcds-util:local --help
podman run --rm tpcds-util:local --version
```

### Multi-Architecture Testing
```bash
# Test multi-arch build (requires buildx)
docker buildx build --platform linux/amd64,linux/arm64 -f Containerfile .
```

## 🔍 Debugging Tips

### Common Issues and Solutions

1. **Test Timeouts**
   ```bash
   # Issue: Integration tests taking too long
   # Solution: Ensure using scale=0 mode
   grep -r "scale=1" tests/integration/
   # Should show minimal results
   ```

2. **Container Build Failures**
   ```bash
   # Issue: Container build fails
   # Solution: Check Containerfile syntax and base image
   podman build --no-cache -f Containerfile .
   ```

3. **Import/Formatting Issues**
   ```bash
   # Issue: Linting failures
   # Solution: Auto-fix common issues
   black src/ tests/
   isort src/ tests/
   ```

4. **Coverage Issues**
   ```bash
   # Issue: Low coverage or missing files
   # Solution: Check coverage report
   pytest tests/unit/ --cov=src/tpcds_util --cov-report=html
   open htmlcov/index.html
   ```

### Verbose Testing
For detailed debugging, run tests with verbose output:

```bash
# Verbose unit tests
PYTHONPATH=. pytest tests/unit/ -v -s --tb=long

# Verbose integration tests  
PYTHONPATH=. pytest tests/integration/test_simple_sqlite.py -v -s --tb=long

# Verbose container build
podman build -f Containerfile -t test --progress=plain .
```

## 📁 Test Artifacts

After running tests, check these locations for results:

```
.ci-simulation/artifacts/
├── htmlcov/              # Coverage reports
├── test-data/            # Generated test data
└── logs/                 # Test execution logs

htmlcov/                  # Coverage from component tests
├── index.html            # Main coverage report
└── ...

artifacts/                # act artifacts (if using act)
└── ...
```

## ⚡ Performance Optimization

### Speeding Up Local Tests

1. **Use Component Testing for Development**
   ```bash
   # Only test what you're working on
   ./scripts/test-components-locally.sh
   # Choose specific component
   ```

2. **Cache Dependencies**
   ```bash
   # Create persistent venv for faster subsequent runs
   python3 -m venv ~/.venvs/tpcds-util
   source ~/.venvs/tpcds-util/bin/activate
   pip install -r requirements.txt
   ```

3. **Skip Slow Tests During Development**
   ```bash
   # Skip integration tests during rapid development
   PYTHONPATH=. pytest tests/unit/ -v
   ```

4. **Use Docker Layer Caching**
   ```bash
   # Enable BuildKit for faster builds
   export DOCKER_BUILDKIT=1
   docker build -f Containerfile .
   ```

## 🔒 Security Testing

### Local Security Scanning
```bash
# Python dependency scanning
pip install safety
safety check --file requirements.txt

# Container scanning (if Trivy installed)
brew install trivy
trivy image tpcds-util:local

# Filesystem scanning
trivy fs .
```

## 📋 Checklist Before Push

Before pushing to GitHub, ensure:

- [ ] ✅ `./scripts/simulate-ci-env.sh` passes completely
- [ ] ✅ No linting errors (black, flake8, isort)  
- [ ] ✅ Unit tests pass with good coverage
- [ ] ✅ Integration tests pass quickly (scale=0 mode)
- [ ] ✅ Container builds successfully
- [ ] ✅ No security vulnerabilities found
- [ ] ✅ Data generation works (scale=0 test mode)

## 🆘 Getting Help

If local testing reveals issues:

1. **Check the error messages** - they usually point to the specific problem
2. **Review recent changes** - what did you modify that might cause issues?
3. **Test individual components** - isolate the failing component
4. **Check prerequisites** - ensure Python, container runtime, etc. are working
5. **Review logs** - check artifacts directories for detailed logs

## 🎯 Next Steps

Once local testing passes:

1. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add CI/CD pipeline with local testing"
   ```

2. **Push to GitHub**
   ```bash
   git push origin main
   ```

3. **Monitor GitHub Actions**
   - Check the Actions tab in GitHub
   - Verify all workflows pass
   - Review any differences between local and remote results

4. **Set up Quay.io secrets** (for container pushes)
   - Add `QUAY_USERNAME` and `QUAY_PASSWORD` to repository secrets
   - Push a test tag to trigger the build pipeline

The local testing scripts ensure high confidence that the actual CI/CD pipeline will work correctly! 🚀