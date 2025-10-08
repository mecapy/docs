# GitHub Actions CI/CD Setup Guide

## Overview

This guide provides comprehensive instructions for setting up and configuring GitHub Actions CI/CD pipelines for the MecaPy API.

## Architecture

### Workflows

1. **`api-ci.yml`** - Continuous Integration
   - Runs on: push to main/develop, pull requests
   - Jobs: lint, test, security, sonarcloud, build-check

2. **`api-deploy.yml`** - Continuous Deployment
   - Runs on: push to main, manual workflow dispatch
   - Jobs: pre-deploy-checks, build-docker, security-scan, deploy-clever-cloud, smoke-tests

3. **`api-pr-checks.yml`** - Pull Request Validation
   - Runs on: pull requests
   - Jobs: pr-validation, code-quality, test-coverage, dependency-review

## Prerequisites

### Required Secrets

Configure the following secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

#### Container Registry
- `GITHUB_TOKEN` - Auto-provided by GitHub Actions

#### Clever Cloud Deployment
- `CLEVER_TOKEN` - Clever Cloud API token
- `CLEVER_SECRET` - Clever Cloud API secret
- `CLEVER_APP_ID` - Clever Cloud application ID
- `CLEVER_APP_URL` - Deployed application URL (e.g., https://mecapy-api.cleverapps.io)

#### Application Configuration
- `CC_KEYCLOAK_URL` - Keycloak server URL
- `KEYCLOAK_CLIENT_SECRET` - Keycloak client secret
- `SCW_ACCESS_KEY` - Scaleway access key
- `SCW_SECRET_KEY` - Scaleway secret key
- `CLOUD_BUCKET_UPLOADS` - S3 bucket name for uploads
- `CORS_ALLOW_ORIGINS` - Allowed CORS origins
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_HOST` - Redis host address
- `REDIS_PORT` - Redis port (default: 6379)

#### Code Quality & Security
- `CODECOV_TOKEN` - Codecov upload token (optional)
- `SONAR_TOKEN` - SonarCloud authentication token

### Repository Setup

1. **Enable GitHub Packages**
   ```bash
   # Ensure your repository has GitHub Packages enabled
   # Settings > General > Features > Packages
   ```

2. **Configure Branch Protection**
   ```bash
   # Settings > Branches > Add branch protection rule
   # Branch name pattern: main
   # ✓ Require pull request reviews before merging
   # ✓ Require status checks to pass before merging
   #   - Required checks: lint, test, security
   # ✓ Require branches to be up to date before merging
   ```

3. **Set up Environments**
   ```bash
   # Settings > Environments > New environment
   # Name: production
   # Add environment secrets (same as above)
   # Optional: Add required reviewers
   ```

## Clever Cloud Setup

### Install Clever Cloud CLI

```bash
# Linux/macOS
curl -fsSL https://clever-tools.clever-cloud.com/releases/latest/clever-tools-latest_linux.tar.gz | tar xz
sudo mv clever-tools-*/clever /usr/local/bin/

# Verify installation
clever version
```

### Create Application

```bash
# Login to Clever Cloud
clever login

# Create Python application
clever create --type python mecapy-api --region par --org <your-org>

# Get application ID
clever applications

# Set environment variables
clever env set PYTHON_VERSION 3.13
clever env set CC_KEYCLOAK_URL <keycloak-url>
clever env set KEYCLOAK_REALM mecapy
clever env set KEYCLOAK_CLIENT_ID mecapy-api
clever env set KEYCLOAK_CLIENT_SECRET <secret>
# ... (add all required env vars)
```

### Get API Credentials

```bash
# Create API token
clever profile

# Note the token and secret for GitHub secrets:
# - CLEVER_TOKEN
# - CLEVER_SECRET
```

## Container Registry Setup

### GitHub Container Registry (GHCR)

The workflow uses GitHub Container Registry (ghcr.io) by default.

**Image naming**: `ghcr.io/<owner>/<repo>/mecapy-api`

**Authentication**: Automatic via `GITHUB_TOKEN`

### Alternative: Docker Hub

To use Docker Hub instead:

1. **Update workflow file** (`.github/workflows/api-deploy.yml`):
   ```yaml
   env:
     REGISTRY: docker.io
     IMAGE_NAME: <dockerhub-username>/mecapy-api
   ```

2. **Add secrets**:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`

3. **Update login step**:
   ```yaml
   - name: Log in to Docker Hub
     uses: docker/login-action@v3
     with:
       username: ${{ secrets.DOCKERHUB_USERNAME }}
       password: ${{ secrets.DOCKERHUB_TOKEN }}
   ```

## Workflow Configuration

### CI Workflow (`api-ci.yml`)

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs**:

1. **Lint & Type Check**
   - Runs ruff linting and formatting
   - Runs mypy type checking
   - Fast feedback on code quality

2. **Test**
   - Matrix strategy for Python 3.13
   - Unit tests (excluding integration)
   - Integration tests (with Redis)
   - Coverage reporting to Codecov

3. **Security**
   - Bandit security scan
   - Safety dependency scan
   - Artifact uploads for reports

4. **SonarCloud**
   - Code quality analysis
   - Coverage integration
   - Quality gate enforcement

5. **Build Check**
   - Package build verification
   - Ensures distributable artifact

### Deploy Workflow (`api-deploy.yml`)

**Triggers**:
- Push to `main` branch
- Manual workflow dispatch

**Jobs**:

1. **Pre-deployment Checks**
   - Quick linting
   - Smoke tests
   - Fail-fast validation

2. **Build & Push Docker**
   - Multi-platform build (linux/amd64)
   - Metadata extraction
   - Image tagging strategy
   - SBOM generation
   - Cache optimization

3. **Security Scan**
   - Trivy vulnerability scan
   - SARIF report upload
   - GitHub Security integration

4. **Deploy to Clever Cloud**
   - Environment configuration
   - Variable injection
   - Deployment execution
   - Health check validation

5. **Smoke Tests**
   - Post-deployment validation
   - Endpoint health checks
   - API availability

6. **Rollback** (conditional)
   - Automatic on failure
   - Previous version restoration

### PR Checks Workflow (`api-pr-checks.yml`)

**Triggers**:
- Pull requests to `main` or `develop`

**Jobs**:

1. **PR Validation**
   - Semantic PR title check
   - Merge conflict detection

2. **Code Quality**
   - Ruff checks with annotations
   - Code complexity analysis

3. **Test Coverage**
   - Coverage report generation
   - PR comment with metrics

4. **Dependency Review**
   - Security vulnerability check
   - License compliance

5. **Performance Check**
   - Basic load testing
   - Baseline validation

## Usage Examples

### Triggering Workflows

**Automatic (CI)**:
```bash
# Make changes to API
cd repos/api
# ... edit files ...

# Commit and push
git add .
git commit -m "feat(api): add new endpoint"
git push origin feature/new-endpoint

# CI workflow triggers automatically
```

**Manual Deployment**:
```bash
# Via GitHub UI:
# Actions > API Deploy > Run workflow > Select environment

# Or via gh CLI:
gh workflow run api-deploy.yml -f environment=production
```

### Monitoring Workflows

```bash
# List workflow runs
gh run list --workflow=api-ci.yml

# View specific run
gh run view <run-id>

# Watch live logs
gh run watch
```

### Troubleshooting

**Workflow fails on lint**:
```bash
# Run locally first
cd repos/api
uv run ruff check .
uv run ruff format .
uv run mypy mecapy_api
```

**Workflow fails on tests**:
```bash
# Run tests locally with same env
export TOKEN_VERIFICATION_ENABLED=false
uv run pytest -v
```

**Deployment fails**:
```bash
# Check Clever Cloud logs
clever logs --follow

# Verify environment variables
clever env
```

**Docker build fails**:
```bash
# Build locally
docker build -t mecapy-api:test -f repos/api/Dockerfile repos/api

# Test container
docker run -p 8000:8000 mecapy-api:test
```

## Performance Optimization

### Caching Strategy

1. **Python Dependencies**:
   ```yaml
   - uses: actions/setup-python@v5
     with:
       cache: 'pip'
   ```

2. **Docker Layers**:
   ```yaml
   - uses: docker/build-push-action@v5
     with:
       cache-from: type=gha
       cache-to: type=gha,mode=max
   ```

3. **uv Cache**:
   ```yaml
   - uses: astral-sh/setup-uv@v5
     with:
       enable-cache: true
   ```

### Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Prevents duplicate runs for the same branch.

## Security Best Practices

1. **Secret Management**
   - Never commit secrets to repository
   - Use GitHub encrypted secrets
   - Rotate secrets regularly
   - Use least-privilege access

2. **Container Security**
   - Multi-stage builds
   - Non-root user
   - Minimal base images
   - Regular security scans

3. **Dependency Security**
   - Automated dependency review
   - Safety and Bandit scans
   - License compliance checks

4. **Access Control**
   - Branch protection rules
   - Required reviewers
   - Status check enforcement
   - CODEOWNERS file

## Monitoring and Alerts

### GitHub Actions Notifications

Configure in `Settings > Notifications`:
- Email notifications for failed workflows
- Slack/Discord webhooks (optional)

### SonarCloud Integration

Quality gate status visible in:
- Pull request checks
- README badges
- SonarCloud dashboard

### Deployment Monitoring

- Health check endpoint: `/health`
- Clever Cloud metrics dashboard
- Application logs via `clever logs`

## Cost Optimization

1. **Use GitHub-hosted runners** (included in free tier)
2. **Cache dependencies** to reduce build time
3. **Fail fast** with pre-deployment checks
4. **Limit concurrent workflows** to prevent resource waste
5. **Use matrix strategy** only when necessary

## Rollout Strategy

### Staging Environment (Optional)

1. Create staging environment in Clever Cloud
2. Add staging workflow trigger:
   ```yaml
   on:
     push:
       branches: [develop]
   ```
3. Deploy to staging before production

### Blue-Green Deployment (Advanced)

For zero-downtime deployments, maintain two Clever Cloud apps:
- Blue: Current production
- Green: New version

Switch traffic after validation.

## Maintenance

### Updating Workflows

```bash
# Test workflow changes in a branch
git checkout -b ci/update-workflow
# Edit .github/workflows/api-ci.yml
git commit -m "ci: update workflow configuration"
git push origin ci/update-workflow
# Create PR and verify checks
```

### Dependency Updates

```bash
# Update GitHub Actions
# Use Dependabot: .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Clever Cloud Deployment Guide](https://www.clever-cloud.com/doc/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [SonarCloud Integration](https://sonarcloud.io/documentation)

## Support

For issues or questions:
- GitHub Issues: https://github.com/mecapy/api/issues
- Clever Cloud Support: https://www.clever-cloud.com/support
- Internal Documentation: `/docs/ci-cd/`
