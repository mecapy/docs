# Container Registry Strategy for MecaPy

**Date:** 2025-10-04
**Version:** 1.0
**Status:** Architecture Design
**Author:** System Architecture Designer

---

## Executive Summary

This document outlines the container registry strategy for MecaPy, a scientific computing platform requiring secure, performant, and cost-effective Docker image distribution. The recommendation is to use **Scaleway Container Registry** as the primary registry with **GitHub Container Registry** as a backup/disaster recovery solution.

**Key Metrics:**
- **Estimated Image Storage:** 50-100GB (first 6 months)
- **Monthly Image Pulls:** ~15,000 (5,000 function executions/day × 3 days cache rotation)
- **Build Frequency:** ~50-100 images/week (user-generated functions)
- **Maximum Image Size:** 2GB per function image
- **Total Monthly Cost:** €0-1 (Scaleway free tier)

---

## 1. Container Registry Requirements Analysis

### 1.1 Functional Requirements

| Requirement | Priority | Justification |
|-------------|----------|---------------|
| **S3-Compatible Storage Integration** | Critical | Already using Scaleway S3 for inputs/outputs |
| **Private Registry** | Critical | User function code must remain confidential |
| **Image Vulnerability Scanning** | High | Security requirement for user-generated code |
| **High Availability** | High | 99.9% uptime SLA needed for production |
| **Fast Pull Speed** | High | Minimize cold start latency (target: less than 3s) |
| **CI/CD Integration** | Medium | Automated builds from API |
| **Multi-Region Support** | Low | MVP targets single region (EU-West) |
| **Image Immutability** | Medium | Prevent accidental overwrites |

### 1.2 Non-Functional Requirements

**Performance:**
- Image pull latency: less than 500ms (cached), less than 2s (cold)
- Build and push time: less than 60s for typical function (100MB)
- Concurrent pulls: Support 50+ simultaneous worker pulls

**Security:**
- End-to-end encryption (TLS 1.3)
- IAM-based access control
- Automated vulnerability scanning
- Image signing (future: Notary v2/Cosign)
- Compliance: GDPR (EU data residency)

**Scalability:**
- Storage: 100GB → 1TB over 12 months
- Bandwidth: 10GB/month → 100GB/month
- Image count: 100 → 10,000 images

**Cost:**
- Target: less than 50 EUR/month at scale (Phase 2)
- MVP: Leverage free tiers where possible

---

## 2. Registry Provider Comparison

### 2.1 Option Analysis Matrix

| Provider | Storage Cost | Bandwidth Cost | Free Tier | EU Region | S3 Integration | Score |
|----------|--------------|----------------|-----------|-----------|----------------|-------|
| **Scaleway Container Registry** | €0.01/GB | Included | 100GB free | ✅ FR-PAR | ✅ Native | **9/10** |
| **GitHub Container Registry** | Free (public) | Unlimited | Unlimited (public) | ❌ US | ⚠️ Via Actions | **7/10** |
| **Docker Hub** | $5/user | 5GB/6h limit | 1 private repo | ❌ US | ❌ None | **4/10** |
| **GitLab Container Registry** | Included in plan | 10GB/month free | 5GB storage | ✅ EU option | ⚠️ Basic | **6/10** |
| **AWS ECR** | $0.10/GB | $0.09/GB | 500MB/month free | ✅ eu-west-1 | ✅ Native | **7/10** |

### 2.2 Detailed Provider Analysis

#### 2.2.1 Scaleway Container Registry (RECOMMENDED)

**Pros:**
- ✅ **Free Tier:** 100GB storage (covers MVP + Phase 2)
- ✅ **EU Data Residency:** Paris (FR-PAR) region - GDPR compliant
- ✅ **Native S3 Integration:** Same infrastructure as Object Storage
- ✅ **Scaleway Ecosystem:** Already using PostgreSQL, Redis, Instances
- ✅ **Network Performance:** Low latency to Hetzner bare metal (same EU region)
- ✅ **Security:** Built-in vulnerability scanning (Clair integration)
- ✅ **IAM Integration:** Scaleway IAM policies for access control
- ✅ **No Bandwidth Charges:** Unlimited pulls within Scaleway ecosystem

**Cons:**
- ⚠️ **Vendor Lock-in:** Tied to Scaleway ecosystem
- ⚠️ **Limited Geographic Distribution:** Single region (no global CDN)
- ⚠️ **Smaller Ecosystem:** Less community tooling vs Docker Hub/GHCR

**Cost Projection:**
```
MVP (0-100GB):          €0/month (free tier)
Phase 2 (100-500GB):    €5/month (€0.01/GB × 500GB)
Phase 3 (500GB-2TB):    €20/month (€0.01/GB × 2TB)
```

**Technical Implementation:**
```bash
# Authentication
export SCW_ACCESS_KEY="<access_key>"
export SCW_SECRET_KEY="<secret_key>"

# Login
docker login rg.fr-par.scw.cloud/mecapy -u nologin -p ${SCW_SECRET_KEY}

# Image naming convention
rg.fr-par.scw.cloud/mecapy/<namespace>/<image>:<tag>

# Example: User function image
rg.fr-par.scw.cloud/mecapy/functions/user-123-func-456:v1.2.3
```

---

#### 2.2.2 GitHub Container Registry (BACKUP/DR)

**Pros:**
- ✅ **Free for Public Images:** Unlimited storage and bandwidth
- ✅ **CI/CD Integration:** Native GitHub Actions support
- ✅ **High Availability:** GitHub's global infrastructure
- ✅ **Developer Familiarity:** Most developers already use GitHub
- ✅ **No Rate Limits:** For authenticated users
- ✅ **Package Retention Policies:** Automated cleanup of old images

**Cons:**
- ❌ **No EU Region:** US-based infrastructure (GDPR considerations)
- ❌ **Private Image Costs:** $0.25/GB storage for private repos
- ⚠️ **No Native S3 Integration:** Requires separate workflows
- ⚠️ **Higher Latency:** From EU to US for image pulls

**Use Cases for MecaPy:**
- **CI/CD Pipeline Images:** Base images for builds (Python, Node.js)
- **Disaster Recovery:** Mirror critical images for redundancy
- **Public SDK Examples:** Share community function templates

**Cost Projection:**
```
Public images:           €0/month
Private (50GB):          €11/month ($0.25/GB × 50GB)
```

---

#### 2.2.3 Docker Hub (NOT RECOMMENDED)

**Analysis:**
- ❌ **Rate Limits:** 100 pulls/6h for free tier (insufficient for production)
- ❌ **Limited Free Tier:** Only 1 private repository
- ❌ **Cost:** $5/user/month for team plan (expensive at scale)
- ❌ **No EU Region:** US-based infrastructure
- ✅ **Wide Ecosystem:** Largest public image repository

**Verdict:** Not suitable for MecaPy due to rate limits and cost structure.

---

#### 2.2.4 AWS ECR

**Analysis:**
- ✅ **EU Region:** eu-west-1 (Ireland) available
- ✅ **Mature Service:** Enterprise-grade reliability
- ✅ **IAM Integration:** Granular access control
- ✅ **Vulnerability Scanning:** Built-in
- ⚠️ **Cost:** $0.10/GB storage + $0.09/GB bandwidth (expensive at scale)
- ⚠️ **Complexity:** Requires AWS account and IAM setup

**Cost Projection:**
```
100GB storage + 300GB bandwidth/month = €17/month
(€9 storage + €8 bandwidth)
```

**Verdict:** Good option if already using AWS, but more expensive than Scaleway for MecaPy's use case.

---

## 3. Recommended Architecture

### 3.1 Dual-Registry Strategy

**Primary Registry:** Scaleway Container Registry (FR-PAR)
**Backup Registry:** GitHub Container Registry (Public base images + DR)

```
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD PIPELINE                            │
│                                                               │
│  API FastAPI (Clever Cloud)                                  │
│  └─ User creates function                                    │
│     ├─ Generate Dockerfile                                   │
│     ├─ Build image: docker build                             │
│     ├─ Tag: rg.fr-par.scw.cloud/mecapy/functions/...        │
│     ├─ Push → Scaleway Registry (PRIMARY)                    │
│     └─ (Optional) Mirror → GHCR (DR - critical images only)  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Image Pull
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            BARE METAL WORKER (Hetzner AX52)                  │
│                                                               │
│  Worker Daemon                                               │
│  ├─ Poll Redis queue                                         │
│  ├─ Check LRU cache (200 containers warm)                   │
│  ├─ Cache MISS:                                              │
│  │  ├─ Pull from Scaleway Registry (PRIMARY)                │
│  │  └─ Fallback to GHCR if Scaleway down (DR)              │
│  └─ Execute in Docker container                              │
│                                                               │
│  Docker Daemon                                               │
│  └─ Image cache: 200 images × 200MB = 40GB                  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Image Naming Convention

**Structure:**
```
<registry>/<namespace>/<image-type>/<identifier>:<tag>
```

**Examples:**
```bash
# User function images
rg.fr-par.scw.cloud/mecapy/functions/user-a1b2c3-func-123:v1.0.0
rg.fr-par.scw.cloud/mecapy/functions/user-a1b2c3-func-123:latest
rg.fr-par.scw.cloud/mecapy/functions/user-a1b2c3-func-123:sha-abc123

# Base images (Python runtimes)
rg.fr-par.scw.cloud/mecapy/base/python:3.11-slim
rg.fr-par.scw.cloud/mecapy/base/python:3.12-numpy
ghcr.io/mecapy/base/python:3.11-slim  # Public mirror

# Worker system images
rg.fr-par.scw.cloud/mecapy/system/worker:v2.1.0
rg.fr-par.scw.cloud/mecapy/system/worker:latest
```

### 3.3 Image Lifecycle Management

**Retention Policies:**
```yaml
# User function images
user_functions:
  retention: 90 days  # Keep for 3 months after last pull
  max_versions: 10     # Keep last 10 versions per function
  auto_cleanup: true

# Base images
base_images:
  retention: 365 days  # Keep for 1 year
  immutable: true      # Prevent overwrites

# Latest tags
latest_tags:
  retention: 30 days   # Auto-update, short retention
```

**Cleanup Strategy:**
```python
# Pseudo-code for automated cleanup
def cleanup_old_images():
    images = registry.list_images(namespace="mecapy/functions")
    for image in images:
        last_pull = image.get_last_pull_time()
        age_days = (now - last_pull).days

        if age_days > 90:
            # Check if function still exists
            function = db.get_function(image.function_id)
            if not function or function.deleted:
                registry.delete_image(image)
                logger.info(f"Deleted old image: {image.name}")
```

---

## 4. CI/CD Pipeline Design

### 4.1 Automated Image Build Workflow

**Trigger:** User creates/updates function via API `POST /functions`

**Pipeline Steps:**

```mermaid
graph TD
    A[User POST /functions] --> B[Validate Code]
    B --> C[Generate Dockerfile]
    C --> D[Build Docker Image]
    D --> E[Run Security Scan]
    E --> F{Vulnerabilities?}
    F -->|Critical| G[Reject & Notify User]
    F -->|None/Low| H[Tag Image]
    H --> I[Push to Scaleway Registry]
    I --> J[Update Function Metadata in DB]
    J --> K[Return Success]

    E --> L[Upload Build Logs to S3]
```

### 4.2 Implementation Details

#### 4.2.1 Dockerfile Generation

**Template Engine:**
```python
# mecapy_api/services/docker_builder.py

from jinja2 import Template
import hashlib

DOCKERFILE_TEMPLATE = """
# Base image with Python + NumPy
FROM rg.fr-par.scw.cloud/mecapy/base/python:{{ python_version }}-slim

# Security: Run as non-root user
RUN useradd -m -u 1000 mecapy
USER mecapy
WORKDIR /app

# Install user dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy user function code
COPY user_function.py .

# Metadata labels
LABEL org.mecapy.function.id="{{ function_id }}"
LABEL org.mecapy.function.user="{{ user_id }}"
LABEL org.mecapy.function.version="{{ version }}"
LABEL org.mecapy.function.created="{{ created_at }}"

# Default command
CMD ["python", "user_function.py"]
"""

def generate_dockerfile(function: Function) -> str:
    """Generate Dockerfile from template."""
    template = Template(DOCKERFILE_TEMPLATE)
    return template.render(
        python_version=function.python_version or "3.11",
        function_id=function.id,
        user_id=function.user_id,
        version=function.version,
        created_at=function.created_at.isoformat()
    )

def build_and_push_image(function: Function) -> str:
    """Build Docker image and push to registry."""
    import docker

    client = docker.from_env()

    # Generate unique tag
    code_hash = hashlib.sha256(function.code.encode()).hexdigest()[:8]
    image_tag = f"rg.fr-par.scw.cloud/mecapy/functions/user-{function.user_id}-func-{function.id}:v{function.version}-{code_hash}"

    # Build context
    build_context = {
        'Dockerfile': generate_dockerfile(function),
        'user_function.py': function.code,
        'requirements.txt': function.requirements
    }

    # Build image
    image, build_logs = client.images.build(
        fileobj=io.BytesIO(create_tar_archive(build_context)),
        tag=image_tag,
        rm=True,  # Remove intermediate containers
        pull=False,  # Don't pull base image every time (cached)
        nocache=False
    )

    # Push to registry
    auth_config = {
        'username': 'nologin',
        'password': os.getenv('SCW_SECRET_KEY')
    }

    push_logs = client.images.push(
        repository=image_tag,
        auth_config=auth_config,
        stream=True
    )

    # Upload build logs to S3 for debugging
    upload_build_logs_to_s3(function.id, build_logs, push_logs)

    return image_tag
```

#### 4.2.2 Security Scanning Integration

**Tool:** Trivy (open-source vulnerability scanner)

```python
# mecapy_api/services/security_scanner.py

import subprocess
import json

def scan_image(image_tag: str) -> dict:
    """Scan Docker image for vulnerabilities using Trivy."""

    result = subprocess.run([
        'trivy', 'image',
        '--format', 'json',
        '--severity', 'HIGH,CRITICAL',
        '--exit-code', '1',  # Fail if vulnerabilities found
        image_tag
    ], capture_output=True, text=True)

    scan_results = json.loads(result.stdout)

    vulnerabilities = []
    for target in scan_results.get('Results', []):
        for vuln in target.get('Vulnerabilities', []):
            vulnerabilities.append({
                'id': vuln['VulnerabilityID'],
                'severity': vuln['Severity'],
                'package': vuln['PkgName'],
                'installed_version': vuln['InstalledVersion'],
                'fixed_version': vuln.get('FixedVersion', 'N/A'),
                'title': vuln.get('Title', ''),
            })

    return {
        'passed': result.returncode == 0,
        'vulnerabilities': vulnerabilities,
        'critical_count': len([v for v in vulnerabilities if v['severity'] == 'CRITICAL']),
        'high_count': len([v for v in vulnerabilities if v['severity'] == 'HIGH'])
    }
```

### 4.3 GitHub Actions Workflow (Optional - For Base Images)

**File:** `.github/workflows/build-base-images.yml`

```yaml
name: Build Base Images

on:
  push:
    paths:
      - 'docker/base/**'
      - '.github/workflows/build-base-images.yml'
  schedule:
    # Rebuild weekly for security updates
    - cron: '0 2 * * 0'
  workflow_dispatch:

jobs:
  build-python-images:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python_version: ['3.11', '3.12']
        variant: ['slim', 'numpy', 'scipy']

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Scaleway Registry
        uses: docker/login-action@v3
        with:
          registry: rg.fr-par.scw.cloud
          username: nologin
          password: ${{ secrets.SCW_SECRET_KEY }}

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./docker/base/python-${{ matrix.variant }}
          build-args: |
            PYTHON_VERSION=${{ matrix.python_version }}
          push: true
          tags: |
            rg.fr-par.scw.cloud/mecapy/base/python:${{ matrix.python_version }}-${{ matrix.variant }}
            ghcr.io/mecapy/base/python:${{ matrix.python_version }}-${{ matrix.variant }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Scan image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: rg.fr-par.scw.cloud/mecapy/base/python:${{ matrix.python_version }}-${{ matrix.variant }}
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## 5. Security Best Practices

### 5.1 Access Control

**IAM Policy Example (Scaleway):**

```json
{
  "version": "2023-06-01",
  "id": "mecapy-worker-registry-access",
  "statement": [
    {
      "sid": "AllowWorkerPull",
      "effect": "allow",
      "actions": [
        "registry:PullImage",
        "registry:GetImageManifest"
      ],
      "resources": [
        "rg.fr-par.scw.cloud/mecapy/functions/*",
        "rg.fr-par.scw.cloud/mecapy/base/*"
      ]
    },
    {
      "sid": "DenyWorkerPush",
      "effect": "deny",
      "actions": [
        "registry:PushImage",
        "registry:DeleteImage"
      ],
      "resources": ["*"]
    }
  ]
}
```

**Service Accounts:**

| Service | Permission Level | Use Case |
|---------|------------------|----------|
| **API Builder** | Push + Pull (functions/*, system/*) | Build and push user function images |
| **Worker** | Pull only (functions/*, base/*) | Pull images for execution |
| **CI/CD** | Push + Pull (base/*, system/*) | Build base images and system components |
| **Admin** | Full access | Manual operations and troubleshooting |

### 5.2 Image Signing (Future Enhancement)

**Tool:** Cosign (Sigstore)

```bash
# Sign image after build
cosign sign --key cosign.key \
  rg.fr-par.scw.cloud/mecapy/functions/user-123-func-456:v1.0.0

# Verify signature before pull (worker)
cosign verify --key cosign.pub \
  rg.fr-par.scw.cloud/mecapy/functions/user-123-func-456:v1.0.0
```

**Benefits:**
- Prevent supply chain attacks
- Ensure image integrity
- Compliance requirements (future enterprise customers)

### 5.3 Network Security

**Registry Access:**
```yaml
# Only allow access from known IPs
firewall_rules:
  - name: api-builder-access
    source: <Clever Cloud IP range>
    destination: rg.fr-par.scw.cloud
    action: allow

  - name: worker-access
    source: <Hetzner bare metal IP>
    destination: rg.fr-par.scw.cloud
    action: allow

  - name: deny-all
    source: 0.0.0.0/0
    action: deny
```

### 5.4 Secrets Management

**Never store in images:**
- API keys
- Database credentials
- OAuth tokens

**Proper approach:**
```dockerfile
# ❌ WRONG
ENV DATABASE_URL="postgresql://user:pass@host/db"

# ✅ CORRECT
# Secrets injected at runtime via environment variables
CMD ["sh", "-c", "python /app/user_function.py"]
```

**Runtime injection (worker):**
```python
# Worker injects secrets at container runtime
container = client.containers.run(
    image=function.image_tag,
    environment={
        'MECAPY_FUNCTION_ID': function.id,
        'MECAPY_USER_ID': function.user_id,
        # Secrets from HashiCorp Vault / AWS Secrets Manager
        'DATABASE_URL': get_secret('database_url'),
        'API_KEY': get_secret(f'user_{user_id}_api_key')
    },
    detach=True
)
```

---

## 6. Cost Analysis

### 6.1 Scaleway Registry Costs

**Pricing Model:**
- Storage: €0.01/GB/month
- Bandwidth: Free (within Scaleway ecosystem)
- Free Tier: 100GB storage

**Projections:**

| Period | Active Functions | Avg Image Size | Total Storage | Monthly Cost |
|--------|------------------|----------------|---------------|--------------|
| **MVP (Month 1-3)** | 100 | 200MB | 20GB | €0 (free tier) |
| **Growth (Month 4-6)** | 500 | 200MB | 100GB | €0 (free tier) |
| **Scale (Month 7-12)** | 2,000 | 250MB | 500GB | €5/month |
| **Year 2** | 10,000 | 300MB | 3TB | €30/month |

**Bandwidth Analysis:**
```
Daily image pulls: 5,000 executions
Cache hit rate: 80% (LRU cache on worker)
Cold starts: 1,000/day

Average image size: 200MB
Daily bandwidth: 1,000 × 200MB = 200GB/day
Monthly bandwidth: 200GB × 30 = 6TB/month

Cost within Scaleway: €0 (free within ecosystem)
Cost if external: 6TB × €0.01/GB = €60/month (AVOIDED)
```

### 6.2 GitHub Container Registry Costs

**Use Case:** Public base images + DR mirror

```
Public images (base/python:*): €0 (unlimited)
Private mirror (critical functions): 10GB × €0.25/GB = €2.50/month
Total: €2.50/month
```

### 6.3 Total Infrastructure Cost Impact

| Component | Current Plan | With Registry | Difference |
|-----------|--------------|---------------|------------|
| API (Clever Cloud) | €7 | €7 | €0 |
| Keycloak | €10 | €10 | €0 |
| PostgreSQL (×2) | €30 | €30 | €0 |
| Redis | €15 | €15 | €0 |
| Object Storage | €1 | €1 | €0 |
| **Container Registry** | **€0** | **€0** | **€0** |
| Bare Metal Worker | €54 | €54 | €0 |
| **TOTAL** | **€117** | **€117** | **€0** |

**Conclusion:** Scaleway Container Registry has **ZERO cost impact** on MVP budget due to 100GB free tier.

---

## 7. Disaster Recovery & High Availability

### 7.1 Registry Failover Strategy

**Scenario:** Scaleway Registry outage

```python
# Worker image pull with failover
def pull_image_with_fallback(image_tag: str) -> docker.Image:
    """Pull image with automatic failover to backup registry."""

    registries = [
        {
            'url': 'rg.fr-par.scw.cloud',
            'auth': {'username': 'nologin', 'password': os.getenv('SCW_SECRET_KEY')},
            'priority': 1
        },
        {
            'url': 'ghcr.io',
            'auth': {'username': 'mecapy', 'password': os.getenv('GITHUB_TOKEN')},
            'priority': 2
        }
    ]

    for registry in sorted(registries, key=lambda x: x['priority']):
        try:
            # Transform image tag for registry
            backup_tag = image_tag.replace('rg.fr-par.scw.cloud', registry['url'])

            client = docker.from_env()
            client.login(**registry['auth'])

            logger.info(f"Pulling from {registry['url']}: {backup_tag}")
            image = client.images.pull(backup_tag)

            return image

        except docker.errors.ImageNotFound:
            logger.warning(f"Image not found in {registry['url']}")
            continue
        except Exception as e:
            logger.error(f"Failed to pull from {registry['url']}: {e}")
            continue

    raise Exception(f"Failed to pull image from all registries: {image_tag}")
```

### 7.2 Automated Mirroring

**Cron Job (Worker Server):**

```bash
#!/bin/bash
# /usr/local/bin/mirror-critical-images.sh

# Mirror top 100 most-used function images to GHCR for DR
psql "$DATABASE_URL" -t -c "
  SELECT docker_image
  FROM functions
  WHERE deleted_at IS NULL
  ORDER BY last_executed_at DESC
  LIMIT 100
" | while read -r image; do
  if [ -n "$image" ]; then
    # Pull from Scaleway
    docker pull "$image"

    # Tag for GHCR
    ghcr_image="${image/rg.fr-par.scw.cloud/ghcr.io}"
    docker tag "$image" "$ghcr_image"

    # Push to GHCR
    docker push "$ghcr_image"

    echo "Mirrored: $image -> $ghcr_image"
  fi
done
```

**Cron Schedule:**
```cron
# Run daily at 2 AM
0 2 * * * /usr/local/bin/mirror-critical-images.sh >> /var/log/registry-mirror.log 2>&1
```

### 7.3 Backup & Recovery

**Registry Metadata Backup:**

```python
# Daily backup of registry metadata to S3
import boto3
from datetime import datetime

def backup_registry_metadata():
    """Backup registry image metadata to S3."""

    # Get all images from Scaleway Registry API
    images = scaleway_api.list_images(namespace='mecapy')

    backup_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'registry': 'rg.fr-par.scw.cloud/mecapy',
        'images': []
    }

    for image in images:
        backup_data['images'].append({
            'name': image.name,
            'tags': image.tags,
            'size': image.size,
            'created_at': image.created_at,
            'last_pulled': image.last_pulled,
            'function_id': image.labels.get('org.mecapy.function.id'),
            'user_id': image.labels.get('org.mecapy.function.user')
        })

    # Upload to S3
    s3 = boto3.client('s3')
    backup_key = f"registry-backups/{datetime.utcnow().strftime('%Y-%m-%d')}.json"

    s3.put_object(
        Bucket='mecapy-backups',
        Key=backup_key,
        Body=json.dumps(backup_data, indent=2),
        ContentType='application/json'
    )

    logger.info(f"Registry metadata backed up to s3://mecapy-backups/{backup_key}")
```

**Recovery Procedure:**

1. **Minor Outage (less than 1 hour):** Worker retries + fallback to GHCR
2. **Major Outage (>1 hour):**
   - Switch all workers to GHCR as primary
   - Continue operations with mirrored images
   - New builds pushed to GHCR only
3. **Complete Loss:**
   - Restore metadata from S3 backup
   - Trigger rebuild of all active function images (from source code in DB)
   - Workers use GHCR during rebuild (4-6 hours for 1000 images)

---

## 8. Monitoring & Observability

### 8.1 Key Metrics

**Registry Health:**
- Image pull latency (p50, p95, p99)
- Image push success rate
- Storage usage trend
- Bandwidth consumption
- Failed pull attempts

**CI/CD Pipeline:**
- Build duration (median, max)
- Build success rate
- Security scan failures
- Time to first pull (after build)

**Worker Operations:**
- Cache hit rate (LRU container cache)
- Image pull errors
- Registry failover events

### 8.2 Monitoring Implementation

**Prometheus Metrics (Custom Exporter):**

```python
# mecapy_worker/monitoring/registry_exporter.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
registry_pull_duration = Histogram(
    'mecapy_registry_pull_duration_seconds',
    'Time spent pulling images from registry',
    ['registry', 'image_type']
)

registry_pull_errors = Counter(
    'mecapy_registry_pull_errors_total',
    'Total number of failed image pulls',
    ['registry', 'error_type']
)

registry_cache_hits = Counter(
    'mecapy_registry_cache_hits_total',
    'Total number of cache hits (image already local)',
    ['image_type']
)

registry_storage_bytes = Gauge(
    'mecapy_registry_storage_bytes',
    'Total storage used in registry',
    ['namespace']
)

# Usage
@registry_pull_duration.labels(registry='scaleway', image_type='function').time()
def pull_function_image(image_tag: str):
    # Pull logic
    pass
```

**Grafana Dashboard:**

```yaml
# Example dashboard panels
dashboard:
  title: "MecaPy Container Registry"
  panels:
    - title: "Image Pull Latency"
      type: graph
      targets:
        - expr: histogram_quantile(0.95, rate(mecapy_registry_pull_duration_seconds_bucket[5m]))

    - title: "Cache Hit Rate"
      type: stat
      targets:
        - expr: |
            sum(rate(mecapy_registry_cache_hits_total[5m])) /
            (sum(rate(mecapy_registry_cache_hits_total[5m])) +
             sum(rate(mecapy_registry_pull_duration_seconds_count[5m])))

    - title: "Registry Storage Usage"
      type: gauge
      targets:
        - expr: mecapy_registry_storage_bytes / (100 * 1024^3)  # Show as % of 100GB
```

### 8.3 Alerting Rules

**PrometheusRule:**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: mecapy-registry-alerts
spec:
  groups:
    - name: registry
      interval: 30s
      rules:
        - alert: RegistryPullLatencyHigh
          expr: |
            histogram_quantile(0.95,
              rate(mecapy_registry_pull_duration_seconds_bucket[5m])
            ) > 5
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High registry pull latency (>5s p95)"
            description: "Image pulls are taking longer than expected"

        - alert: RegistryPullFailureRate
          expr: |
            sum(rate(mecapy_registry_pull_errors_total[5m])) /
            sum(rate(mecapy_registry_pull_duration_seconds_count[5m])) > 0.05
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High registry pull failure rate (>5%)"
            description: "More than 5% of image pulls are failing"

        - alert: RegistryStorageNearLimit
          expr: mecapy_registry_storage_bytes > (90 * 1024^3)  # 90GB
          for: 1h
          labels:
            severity: warning
          annotations:
            summary: "Registry storage nearing free tier limit (90GB)"
            description: "Consider cleanup or upgrade plan"
```

---

## 9. Performance Optimization

### 9.1 Image Size Reduction

**Best Practices:**

```dockerfile
# ❌ BAD: Large image (1.2GB)
FROM python:3.11
RUN pip install numpy scipy pandas matplotlib scikit-learn

# ✅ GOOD: Optimized image (350MB)
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir numpy scipy
```

**Multi-stage Builds:**

```dockerfile
# Builder stage
FROM python:3.11 as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY user_function.py /app/
ENV PATH=/root/.local/bin:$PATH
WORKDIR /app
CMD ["python", "user_function.py"]
```

**Size Targets:**
- Base images: less than 100MB
- Function images: less than 300MB
- Maximum allowed: 2GB (enforce in API validation)

### 9.2 Layer Caching Strategy

**Dockerfile Ordering:**

```dockerfile
# 1. Base image (rarely changes)
FROM rg.fr-par.scw.cloud/mecapy/base/python:3.11-slim

# 2. System dependencies (rarely changes)
RUN apt-get update && apt-get install -y libfoo

# 3. Python dependencies (changes occasionally)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. User code (changes frequently)
COPY user_function.py .

# Ensures layers 1-3 are cached across builds
```

### 9.3 Parallel Image Pulls

**Worker Configuration:**

```python
# mecapy_worker/config.py

DOCKER_CONFIG = {
    'max_concurrent_downloads': 10,  # Parallel layer downloads
    'max_concurrent_uploads': 5,
    'default_platform': 'linux/amd64',
}

# Pre-warm cache on worker startup
def prewarm_image_cache():
    """Pull most-used images on worker startup."""

    top_images = db.execute("""
        SELECT docker_image, COUNT(*) as usage_count
        FROM tasks
        WHERE created_at > NOW() - INTERVAL '7 days'
        GROUP BY docker_image
        ORDER BY usage_count DESC
        LIMIT 50
    """)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(docker_client.images.pull, img.docker_image)
            for img in top_images
        ]

        for future in as_completed(futures):
            try:
                image = future.result()
                logger.info(f"Pre-warmed image: {image.tags[0]}")
            except Exception as e:
                logger.error(f"Failed to pre-warm image: {e}")
```

---

## 10. Implementation Roadmap

### 10.1 Phase 1: MVP Setup (Week 3-4)

**Tasks:**

- [x] ~~Research registry options~~ (This document)
- [ ] Create Scaleway Container Registry namespace `mecapy`
- [ ] Configure IAM policies (API builder, worker, CI/CD)
- [ ] Implement Dockerfile generation in API
- [ ] Implement build & push logic in API
- [ ] Configure worker to authenticate with Scaleway Registry
- [ ] Test end-to-end: Create function → Build image → Execute
- [ ] Document registry access for team

**Deliverables:**
- Functional image build pipeline
- Worker can pull and execute user function images
- Documentation in `/docs/registry-setup.md`

**Success Criteria:**
- Build time: less than 60s for 100MB image
- Pull time: less than 2s from worker (warm cache)
- Zero cost (within free tier)

---

### 10.2 Phase 2: Security & Monitoring (Week 7-8)

**Tasks:**

- [ ] Integrate Trivy security scanner
- [ ] Implement vulnerability checking in build pipeline
- [ ] Set up Prometheus registry metrics exporter
- [ ] Create Grafana dashboard
- [ ] Configure alerting rules
- [ ] Implement automated cleanup of old images
- [ ] Set up GitHub Container Registry mirror (base images)
- [ ] Test disaster recovery failover

**Deliverables:**
- Security scanning prevents vulnerable images
- Monitoring dashboard operational
- DR plan tested and documented

---

### 10.3 Phase 3: Optimization (Month 3-6)

**Tasks:**

- [ ] Implement image signing with Cosign
- [ ] Optimize base image sizes (less than 100MB target)
- [ ] Pre-warm cache on worker startup
- [ ] Implement parallel image pulls
- [ ] Set up automated mirroring to GHCR (top 100 images)
- [ ] Performance testing (100 concurrent builds)
- [ ] Implement retention policies automation

**Deliverables:**
- Cold start latency: less than 3s (target: 2.5s)
- Cache hit rate: >80%
- Build throughput: 50 images/hour

---

## 11. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Scaleway Registry outage** | Low | High | Automated failover to GHCR, critical images mirrored |
| **Exceeding free tier (100GB)** | Medium | Low | Automated cleanup, monitoring alerts at 90GB |
| **Slow image pulls (>5s)** | Low | Medium | Pre-warming, layer caching, Scaleway-Hetzner proximity |
| **Security vulnerabilities in user images** | High | High | Trivy scanning, reject on CRITICAL findings |
| **Registry bandwidth costs** | Low | Low | Use Scaleway ecosystem (free bandwidth) |
| **Build pipeline bottleneck** | Medium | Medium | Queue-based builds, timeout limits, horizontal scaling |
| **Image size bloat** | Medium | Medium | Size limits (2GB), lint checks, multi-stage builds |

---

## 12. Conclusion & Recommendations

### 12.1 Final Recommendation

**Primary Registry:** Scaleway Container Registry (FR-PAR)
**Backup Registry:** GitHub Container Registry (for base images + DR)

**Justification:**
1. **Cost:** €0/month for MVP (100GB free tier covers 6-12 months)
2. **Performance:** Low latency to Hetzner worker (both in EU)
3. **Integration:** Native S3 integration with existing Scaleway infrastructure
4. **Compliance:** EU data residency (GDPR)
5. **Scalability:** Grows with usage at €0.01/GB (predictable costs)

### 12.2 Key Success Factors

1. **Automated Builds:** API builds images on function creation (no manual steps)
2. **Security First:** Trivy scanning prevents vulnerable images
3. **Monitoring:** Prometheus + Grafana for visibility
4. **DR Plan:** GHCR failover + automated mirroring
5. **Cost Control:** Automated cleanup keeps usage within free tier

### 12.3 Next Steps

1. **Immediate (This Week):**
   - Create Scaleway Container Registry namespace
   - Generate IAM credentials for API and worker
   - Update deployment documentation

2. **Week 3-4 (API Backend Sprint):**
   - Implement Dockerfile generation
   - Implement build & push in API
   - Configure worker authentication
   - End-to-end testing

3. **Week 7-8 (Testing Sprint):**
   - Security scanning integration
   - Monitoring setup
   - DR testing

### 12.4 Documentation Artifacts

This strategy will be supported by:
- `/docs/registry-setup.md` - Operational guide
- `/docs/registry-dr.md` - Disaster recovery procedures
- `/docs/registry-monitoring.md` - Monitoring and alerting
- API code: `/repos/api/mecapy_api/services/docker_builder.py`
- Worker code: `/repos/worker/mecapy_worker/container_manager.py`

---

**Strategy approved for implementation: 2025-10-04**
**Next review date: 2025-12-01 (after MVP launch)**

