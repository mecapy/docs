# GitHub Secrets Configuration Guide

## Overview

This document provides a comprehensive guide for configuring GitHub repository secrets required for CI/CD workflows.

## Required Secrets

### Container Registry

| Secret Name | Description | How to Obtain | Required |
|-------------|-------------|---------------|----------|
| `GITHUB_TOKEN` | GitHub Actions token | Auto-provided by GitHub | ✅ Yes |

**Note**: `GITHUB_TOKEN` is automatically created by GitHub Actions. No manual configuration needed.

### Clever Cloud Deployment

| Secret Name | Description | Example | Required |
|-------------|-------------|---------|----------|
| `CLEVER_TOKEN` | Clever Cloud API token | `tok_xxxxxxxxxxxx` | ✅ Yes |
| `CLEVER_SECRET` | Clever Cloud API secret | `sec_xxxxxxxxxxxx` | ✅ Yes |
| `CLEVER_APP_ID` | Application ID on Clever Cloud | `app_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | ✅ Yes |
| `CLEVER_APP_URL` | Deployed application URL | `https://mecapy-api.cleverapps.io` | ✅ Yes |

**How to obtain Clever Cloud credentials**:

```bash
# Install Clever Cloud CLI
curl -fsSL https://clever-tools.clever-cloud.com/releases/latest/clever-tools-latest_linux.tar.gz | tar xz
sudo mv clever-tools-*/clever /usr/local/bin/

# Login to Clever Cloud
clever login

# Get your API credentials
clever profile
# Shows your token and secret

# List applications to get APP_ID
clever applications
```

### Keycloak Authentication

| Secret Name | Description | Example | Required |
|-------------|-------------|---------|----------|
| `CC_KEYCLOAK_URL` | Keycloak server URL | `https://keycloak.mecapy.com` | ✅ Yes |
| `KEYCLOAK_CLIENT_SECRET` | Keycloak client secret | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | ✅ Yes |

**How to obtain from Keycloak**:

1. Login to Keycloak Admin Console
2. Navigate to: Clients → mecapy-api
3. Go to Credentials tab
4. Copy the Client Secret

### Scaleway Object Storage

| Secret Name | Description | Example | Required |
|-------------|-------------|---------|----------|
| `SCW_ACCESS_KEY` | Scaleway access key | `SCWXXXXXXXXXXXXXXXXX` | ✅ Yes |
| `SCW_SECRET_KEY` | Scaleway secret key | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | ✅ Yes |
| `CLOUD_BUCKET_UPLOADS` | S3 bucket name | `mecapy-uploads` | ✅ Yes |

**How to obtain from Scaleway**:

1. Login to Scaleway Console
2. Navigate to: Identity and Access Management → API Keys
3. Create new API key
4. Save Access Key and Secret Key
5. Create Object Storage bucket:
   - Navigate to: Object Storage → Buckets
   - Create bucket named `mecapy-uploads`

### Application Configuration

| Secret Name | Description | Example | Required |
|-------------|-------------|---------|----------|
| `CORS_ALLOW_ORIGINS` | Allowed CORS origins | `https://mecapy.com,https://app.mecapy.com` | ✅ Yes |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` | ✅ Yes |
| `REDIS_HOST` | Redis server host | `redis.mecapy.com` | ✅ Yes |
| `REDIS_PORT` | Redis server port | `6379` | ⚠️ Optional (default: 6379) |

### Code Quality & Security

| Secret Name | Description | Example | Required |
|-------------|-------------|---------|----------|
| `CODECOV_TOKEN` | Codecov upload token | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | ⚠️ Optional |
| `SONAR_TOKEN` | SonarCloud authentication token | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | ⚠️ Optional |

**How to obtain**:

**Codecov**:
1. Login to https://codecov.io
2. Add repository
3. Copy upload token from Settings

**SonarCloud**:
1. Login to https://sonarcloud.io
2. Analyze new project
3. Generate token in My Account → Security

## Configuration Steps

### Step 1: Access Repository Secrets

1. Navigate to your GitHub repository
2. Click `Settings` tab
3. In the left sidebar, click `Secrets and variables` → `Actions`
4. Click `New repository secret`

### Step 2: Add Each Secret

For each secret listed above:

1. Click `New repository secret`
2. Enter the secret name (exactly as shown, case-sensitive)
3. Enter the secret value
4. Click `Add secret`

### Step 3: Verify Configuration

Run this checklist:

```bash
# ✅ Clever Cloud secrets
- [ ] CLEVER_TOKEN
- [ ] CLEVER_SECRET
- [ ] CLEVER_APP_ID
- [ ] CLEVER_APP_URL

# ✅ Keycloak secrets
- [ ] CC_KEYCLOAK_URL
- [ ] KEYCLOAK_CLIENT_SECRET

# ✅ Scaleway secrets
- [ ] SCW_ACCESS_KEY
- [ ] SCW_SECRET_KEY
- [ ] CLOUD_BUCKET_UPLOADS

# ✅ Application secrets
- [ ] CORS_ALLOW_ORIGINS
- [ ] DATABASE_URL
- [ ] REDIS_HOST

# ⚠️ Optional secrets
- [ ] CODECOV_TOKEN (recommended)
- [ ] SONAR_TOKEN (recommended)
- [ ] REDIS_PORT (if not using default)
```

## Environment-Specific Secrets

For multiple environments (staging, production), use GitHub Environments:

### Create Environment

1. Navigate to `Settings` → `Environments`
2. Click `New environment`
3. Enter name (e.g., `production`, `staging`)
4. Click `Configure environment`

### Add Environment Secrets

1. In environment settings, scroll to `Environment secrets`
2. Click `Add secret`
3. Add environment-specific values

**Example**:

**Production Environment**:
- `CLEVER_APP_URL`: `https://api.mecapy.com`
- `DATABASE_URL`: `postgresql://prod-host:5432/mecapy_prod`

**Staging Environment**:
- `CLEVER_APP_URL`: `https://api-staging.mecapy.com`
- `DATABASE_URL`: `postgresql://staging-host:5432/mecapy_staging`

## Security Best Practices

### 1. Secret Rotation

Rotate secrets regularly:

```bash
# Quarterly rotation schedule
- Q1: Rotate Keycloak client secret
- Q2: Rotate Scaleway access keys
- Q3: Rotate Clever Cloud tokens
- Q4: Rotate database credentials
```

### 2. Least Privilege Access

Ensure secrets have minimum required permissions:

- Scaleway: Create service account with Object Storage only
- Keycloak: Use confidential client with specific roles
- Database: Use account with limited permissions (no DROP/CREATE DATABASE)

### 3. Secret Auditing

Monitor secret usage:

1. GitHub Actions logs (check for unauthorized access)
2. Clever Cloud activity logs
3. Scaleway audit logs

### 4. Never Hardcode Secrets

**❌ Wrong**:
```python
# Don't do this!
KEYCLOAK_SECRET = "my-secret-key"
```

**✅ Correct**:
```python
import os
KEYCLOAK_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
```

### 5. Use Secret Scanning

Enable GitHub secret scanning:

1. Navigate to `Settings` → `Code security and analysis`
2. Enable `Secret scanning`
3. Enable `Push protection`

## Testing Secrets

### Local Testing

**Never** use production secrets locally. Use `.env` file:

```bash
# repos/api/.env.example
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=mecapy
KEYCLOAK_CLIENT_ID=mecapy-api
KEYCLOAK_CLIENT_SECRET=local-dev-secret
TOKEN_VERIFICATION_ENABLED=false

# Copy and modify for local dev
cp .env.example .env
# Edit .env with local values
```

### Workflow Testing

Test workflow with secrets:

```bash
# Use act for local workflow testing
# https://github.com/nektos/act

# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Create .secrets file (DO NOT COMMIT)
echo "CLEVER_TOKEN=test_token" >> .secrets
echo "CLEVER_SECRET=test_secret" >> .secrets

# Run workflow locally
act -s CLEVER_TOKEN -s CLEVER_SECRET
```

## Troubleshooting

### Secret Not Found Error

```
Error: Secret CLEVER_TOKEN not found
```

**Solution**:
1. Verify secret name matches exactly (case-sensitive)
2. Check if secret is set at repository or environment level
3. Ensure workflow has permission to access environment secrets

### Invalid Secret Value

```
Error: Authentication failed with Clever Cloud
```

**Solution**:
1. Verify secret value has no extra whitespace
2. Regenerate token/secret
3. Update GitHub secret with new value

### Secret Not Updating

**Issue**: Workflow still uses old secret value

**Solution**:
1. Secrets are cached. Wait 1-2 minutes after update
2. Re-run workflow
3. If persists, delete and recreate secret

### Environment Secret Override

**Issue**: Repository secret not being used

**Solution**:
- Environment secrets take precedence
- Check environment configuration
- Either update environment secret or remove it to use repository secret

## Validation Checklist

Before first deployment, verify:

```bash
# ✅ All required secrets are set
gh secret list

# ✅ Clever Cloud connection works
clever login --token "$CLEVER_TOKEN" --secret "$CLEVER_SECRET"
clever applications

# ✅ Scaleway credentials valid
export AWS_ACCESS_KEY_ID="$SCW_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="$SCW_SECRET_KEY"
aws s3 ls s3://$CLOUD_BUCKET_UPLOADS --endpoint-url https://s3.fr-par.scw.cloud

# ✅ Database connection works
psql "$DATABASE_URL" -c "SELECT version();"

# ✅ Redis connection works
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping
```

## Additional Resources

- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Clever Cloud CLI Documentation](https://www.clever-cloud.com/doc/cli/)
- [Scaleway API Keys](https://console.scaleway.com/project/credentials)
- [Keycloak Admin Console](https://www.keycloak.org/docs/latest/server_admin/)

## Support

For issues with secret configuration:
- GitHub: https://github.com/mecapy/api/issues
- Internal docs: `/docs/ci-cd/`
