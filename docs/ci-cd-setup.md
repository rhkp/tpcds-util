# CI/CD Setup Guide

This document describes the continuous integration and deployment pipeline for the TPC-DS Utility project.

## 🔄 CI/CD Pipeline Overview

### Workflows

1. **`test.yml`** - Continuous Testing
2. **`build-push.yml`** - Container Build & Push  
3. **`release.yml`** - Automated Releases

## 🧪 Testing Pipeline (`test.yml`)

Runs on every push and pull request to `main` and `develop` branches.

### Jobs:
- **test**: Unit tests + SQLite integration tests across Python 3.8-3.12
- **lint**: Code quality checks (black, flake8, isort)
- **security**: Trivy filesystem vulnerability scanning

### Key Features:
- ✅ **Fast execution**: Scale=0 mode for integration tests (~1 minute total)
- ✅ **43% test coverage** with comprehensive unit and integration tests
- ✅ **Multi-Python support**: Tests against 5 Python versions
- ✅ **No Oracle dependency**: SQLite-based integration tests
- ✅ **Security scanning**: Automated vulnerability detection

## 📦 Container Pipeline (`build-push.yml`)

Builds and pushes container images to Quay.io registry.

### Triggers:
- Push to `main`/`develop` branches
- Git tags (`v*`)
- Pull requests (build only, no push)

### Features:
- 🐳 **Multi-architecture builds**: linux/amd64, linux/arm64
- 🔒 **Container security scanning**: Trivy image scanning
- 📋 **SBOM generation**: Software Bill of Materials for supply chain security
- 🏷️ **Smart tagging**: Branch-based, semantic versioning, SHA-based tags
- 🧪 **Container testing**: Functional validation before push

### Built Images:
```bash
# Main application container
quay.io/your-org/tpcds-util:latest-main
quay.io/your-org/tpcds-util:v1.0.0-main

# Oracle initialization container  
quay.io/your-org/tpcds-util:latest-oracle-init
quay.io/your-org/tpcds-util:v1.0.0-oracle-init
```

## 🚀 Release Pipeline (`release.yml`)

Automated releases triggered by git tags.

### Features:
- 📝 **Automated changelog**: Generated from git commits
- 📦 **Python packages**: Wheel and source distribution
- 🐳 **Tagged container images**: Semantic versioning
- 🔒 **Security attestations**: SBOM and scan results
- 📊 **Release notes**: Comprehensive release documentation

## ⚙️ Setup Requirements

### 1. Quay.io Registry Setup

Create repository secrets in GitHub:
```bash
QUAY_USERNAME=your-quay-username
QUAY_PASSWORD=your-quay-password-or-token
```

### 2. Quay.io Repository Configuration

1. Create repository: `quay.io/your-org/tpcds-util`
2. Set to **public** for open source projects
3. Enable **security scanning** in repository settings
4. Configure **robot accounts** for CI/CD access

### 3. GitHub Repository Settings

Enable the following in your repository settings:
- ✅ **Actions permissions**: Allow GitHub Actions
- ✅ **Security tab**: Enable for vulnerability reports
- ✅ **Packages**: Enable for container registry
- ✅ **Issues**: For release feedback

## 🔒 Security Features

### Vulnerability Scanning
- **Filesystem scanning**: Trivy scans source code
- **Container scanning**: Trivy scans built images
- **SARIF upload**: Results in GitHub Security tab
- **Dependency scanning**: Safety checks Python packages

### Supply Chain Security
- **SBOM generation**: Software Bill of Materials
- **Image signing**: Ready for cosign integration
- **Reproducible builds**: Consistent container builds
- **Multi-stage builds**: Minimal attack surface

## 📊 Monitoring & Observability

### Build Monitoring
- **GitHub Actions**: Build status and logs
- **Codecov**: Test coverage reporting
- **GitHub Security**: Vulnerability dashboard
- **Quay.io**: Container image metrics

### Performance Metrics
- **Test execution time**: ~1 minute for full test suite
- **Build time**: ~5-10 minutes for multi-arch containers
- **Image size**: Optimized with UBI9 base image

## 🚀 Usage Examples

### Manual Container Build
```bash
# Build main application
podman build -f Containerfile -t tpcds-util:local .

# Build Oracle init container
podman build -f Containerfile.oracle-init -t tpcds-util-oracle-init:local .
```

### Running Tests Locally
```bash
# Unit tests with coverage
pytest tests/unit/ --cov=src/tpcds_util --cov-report=term-missing

# Fast integration tests
pytest tests/integration/test_simple_sqlite.py -v

# Full test suite (slower)
pytest tests/ --cov=src/tpcds_util
```

### Creating a Release
```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0

# This automatically triggers:
# 1. Container builds with version tags
# 2. Python package creation
# 3. GitHub release with artifacts
# 4. Security scanning and SBOM generation
```

## 🔧 Customization

### Environment Variables
```yaml
# In build-push.yml
env:
  REGISTRY: quay.io                    # Change registry
  IMAGE_NAME: ${{ github.repository }} # Change image name
```

### Adding New Test Types
```yaml
# In test.yml - add new job
integration-oracle:
  runs-on: ubuntu-latest
  # Add Oracle database service
  services:
    oracle:
      image: gvenzl/oracle-xe:latest
```

### Custom Container Platforms
```yaml
# In build-push.yml
platforms: linux/amd64,linux/arm64,linux/s390x
```

## 🆘 Troubleshooting

### Common Issues

1. **Quay.io push failures**
   - Check `QUAY_USERNAME` and `QUAY_PASSWORD` secrets
   - Verify repository exists and is accessible
   - Check robot account permissions

2. **Test timeouts**
   - Integration tests use scale=0 mode for speed
   - Check if any tests are using scale=1 by mistake
   - Monitor test execution time

3. **Container build failures**
   - Check Containerfile syntax
   - Verify base image availability
   - Check resource requirements

### Performance Optimization

- **Parallel builds**: Matrix strategy for different images
- **Build caching**: GitHub Actions cache for Docker layers
- **Test parallelization**: Multi-version test matrix
- **Fast feedback**: Early failure detection with `-x` flag

## 📈 Metrics & KPIs

- **Pipeline Success Rate**: Target 95%+
- **Test Coverage**: Current 43%, target 60%+
- **Build Time**: <10 minutes for multi-arch
- **Security Score**: Zero high/critical vulnerabilities
- **Release Frequency**: Automated on semantic versioning