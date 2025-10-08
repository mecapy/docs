# Container Registry CI/CD Workflow Diagrams

**Date:** 2025-10-04
**Related:** container_registry_strategy.md

---

## 1. User Function Image Build Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER REQUEST                                │
│              POST /functions (code + requirements)               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   API FASTAPI (Clever Cloud)                     │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 1: Code Validation                                   │  │
│  │  ├─ Syntax check (ast.parse)                             │  │
│  │  ├─ Blacklist imports (os, subprocess, socket, eval)     │  │
│  │  ├─ Size limit (<1MB code, <50 dependencies)            │  │
│  │  └─ Result: ✅ Valid / ❌ Reject                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │ ✅                                   │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 2: Dockerfile Generation (Jinja2 template)          │  │
│  │  FROM rg.fr-par.scw.cloud/mecapy/base/python:3.11-slim  │  │
│  │  USER mecapy (UID 1000)                                  │  │
│  │  COPY requirements.txt + user_function.py                │  │
│  │  RUN pip install --user -r requirements.txt              │  │
│  │  LABEL org.mecapy.function.id="{function_id}"           │  │
│  │  CMD ["python", "user_function.py"]                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 3: Docker Build (docker-py)                         │  │
│  │  ├─ Build context: Dockerfile + code + requirements.txt │  │
│  │  ├─ Tag: rg.fr-par.scw.cloud/mecapy/functions/          │  │
│  │  │       user-a1b2c3-func-456:v1.0.0-sha8char           │  │
│  │  ├─ Cache: Use local Docker layer cache                 │  │
│  │  └─ Timeout: 300s (5 min max)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 4: Security Scan (Trivy)                            │  │
│  │  trivy image --severity HIGH,CRITICAL                    │  │
│  │                                                           │  │
│  │  ├─ Scan for known CVEs in dependencies                 │  │
│  │  ├─ Check Python package vulnerabilities                │  │
│  │  └─ Decision:                                            │  │
│  │     ├─ 0 CRITICAL → ✅ Continue                         │  │
│  │     ├─ 1+ CRITICAL → ❌ REJECT (notify user)            │  │
│  │     └─ HIGH → ⚠️ Log warning, allow build              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │ ✅                                   │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 5: Push to Scaleway Registry                        │  │
│  │  docker push rg.fr-par.scw.cloud/mecapy/functions/...   │  │
│  │                                                           │  │
│  │  Auth: username=nologin, password=$SCW_SECRET_KEY       │  │
│  │  Layers pushed in parallel (10 concurrent streams)       │  │
│  │  Progress: |████████████████████| 100%                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 6: Update Database                                  │  │
│  │  UPDATE functions SET                                     │  │
│  │    docker_image = 'rg.fr-par.scw.cloud/mecapy/...',     │  │
│  │    image_size = 245MB,                                   │  │
│  │    build_duration = 42s,                                 │  │
│  │    build_status = 'success',                             │  │
│  │    build_logs_s3_key = 's3://logs/build-456.log'        │  │
│  │  WHERE id = 456                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RESPONSE TO USER                             │
│                                                                   │
│  {                                                                │
│    "function_id": 456,                                           │
│    "status": "ready",                                            │
│    "docker_image": "rg.fr-par.scw.cloud/mecapy/functions/...",  │
│    "image_size": "245MB",                                        │
│    "build_time": "42s",                                          │
│    "vulnerabilities": {                                          │
│      "critical": 0,                                              │
│      "high": 2,                                                  │
│      "warnings": ["numpy 1.24.0 has HIGH CVE-2023-XXXX"]       │
│    }                                                             │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘

Total time: 45-90s (depending on image size and dependencies)
```

---

## 2. Worker Image Pull Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│              WORKER DAEMON (Bare Metal Hetzner)                  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ EVENT: Job received from Redis queue                      │  │
│  │  {                                                         │  │
│  │    "task_id": 789,                                        │  │
│  │    "function_id": 456,                                    │  │
│  │    "docker_image": "rg.fr-par.scw.cloud/mecapy/...",     │  │
│  │    "inputs_s3_key": "s3://inputs/task-789.json"          │  │
│  │  }                                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 1: Check LRU Container Cache                        │  │
│  │                                                           │  │
│  │  Cache state: 198/200 containers warm (~39GB RAM)        │  │
│  │  LRU order: [most recent] → [least recent]              │  │
│  │                                                           │  │
│  │  Query: Is image in cache?                               │  │
│  │  └─ Search: docker images --filter                       │
│  │            reference="rg.fr-par.scw.cloud/mecapy/..."   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                ┌──────────┴──────────┐                          │
│                ▼                     ▼                           │
│  ┌──────────────────────┐  ┌───────────────────────────────┐   │
│  │ CACHE HIT (80%)      │  │ CACHE MISS (20%)               │   │
│  │ Image already local  │  │ Image needs pulling            │   │
│  └──────┬───────────────┘  └───────┬───────────────────────┘   │
│         │                          │                             │
│         │                          ▼                             │
│         │          ┌──────────────────────────────────────────┐ │
│         │          │ STEP 2: Pull from Registry (COLD START) │ │
│         │          │                                          │ │
│         │          │ PRIMARY: Scaleway Container Registry     │ │
│         │          │ ┌────────────────────────────────────┐  │ │
│         │          │ │ docker pull rg.fr-par.scw.cloud/... │ │
│         │          │ │                                      │ │
│         │          │ │ Auth: $SCW_SECRET_KEY               │ │
│         │          │ │ Timeout: 30s                         │ │
│         │          │ │ Parallel layers: 10                  │ │
│         │          │ │                                      │ │
│         │          │ │ ┌────────────┐                      │ │
│         │          │ │ │ Success?   │                      │ │
│         │          │ │ └─────┬──────┘                      │ │
│         │          │ └───────┼─────────────────────────────┘ │
│         │          │         │ ✅                            │ │
│         │          │         │                               │ │
│         │          │   ❌ TIMEOUT / ERROR                   │ │
│         │          │         │                               │ │
│         │          │         ▼                               │ │
│         │          │ FALLBACK: GitHub Container Registry    │ │
│         │          │ ┌────────────────────────────────────┐ │ │
│         │          │ │ docker pull ghcr.io/mecapy/...    │ │ │
│         │          │ │                                    │ │ │
│         │          │ │ Auth: $GITHUB_TOKEN               │ │ │
│         │          │ │ Timeout: 30s                       │ │ │
│         │          │ │                                    │ │ │
│         │          │ │ Success: Image pulled from DR      │ │ │
│         │          │ │ Metric: registry_failover_total++  │ │ │
│         │          │ └────────────────────────────────────┘ │ │
│         │          └──────────────────┬───────────────────────┘ │
│         │                             │                          │
│         │                             ▼                          │
│         │          ┌──────────────────────────────────────────┐ │
│         │          │ STEP 3: Evict LRU Image if Cache Full   │ │
│         │          │                                          │ │
│         │          │ Current: 200/200 containers              │ │
│         │          │ Action: Remove least recently used       │ │
│         │          │  ├─ docker rmi <oldest_image>           │ │
│         │          │  └─ Free: ~200MB RAM                    │ │
│         │          └──────────────────┬───────────────────────┘ │
│         │                             │                          │
│         └─────────────────────────────┘                          │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 4: Start Container                                  │  │
│  │                                                           │  │
│  │  docker run --rm -d                                       │  │
│  │    --name mecapy-task-789                                │  │
│  │    --network none         # Isolated network             │  │
│  │    --read-only            # Immutable filesystem         │  │
│  │    --tmpfs /tmp:size=512m # Writable /tmp only          │  │
│  │    --memory 2g            # RAM limit                    │  │
│  │    --cpus 2               # CPU limit                    │  │
│  │    --cap-drop ALL         # No capabilities              │  │
│  │    rg.fr-par.scw.cloud/mecapy/functions/user-...:v1.0.0 │  │
│  │                                                           │  │
│  │  Container ID: abc123def456                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 5: Execute Function                                 │  │
│  │  ├─ Copy inputs via TAR: docker cp inputs.json abc123:/ │  │
│  │  ├─ Run: docker exec abc123 python user_function.py     │  │
│  │  ├─ Timeout: 300s (5 min max)                           │  │
│  │  └─ Extract output: docker cp abc123:/output.json .     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 6: Cleanup                                          │  │
│  │  ├─ Stop container: docker stop abc123 (if not --rm)    │  │
│  │  ├─ Upload results to S3                                 │  │
│  │  ├─ Update task status in PostgreSQL                    │  │
│  │  └─ Cache result in Redis (TTL 1h)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

Performance:
  ✅ CACHE HIT:  ~2.2s (overhead 10%)
  ⚠️  CACHE MISS: ~3.5-5s (pull 2s + boot 1.5s + overhead 0.5s)
  ❌ FAILOVER:   ~6-8s (retry + GHCR pull from US)
```

---

## 3. Base Image Build Workflow (GitHub Actions)

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRIGGER EVENTS                                │
│                                                                   │
│  ├─ Push to main (docker/base/** modified)                      │
│  ├─ Weekly cron schedule (security updates)                     │
│  └─ Manual workflow dispatch                                     │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              GITHUB ACTIONS WORKFLOW                             │
│              (.github/workflows/build-base-images.yml)           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ JOB: build-python-images                                  │  │
│  │ Matrix Strategy:                                          │  │
│  │   python_version: [3.11, 3.12]                           │  │
│  │   variant: [slim, numpy, scipy]                          │  │
│  │   Total jobs: 2 × 3 = 6 parallel builds                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 1: Checkout Repository                              │  │
│  │  actions/checkout@v4                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 2: Set up Docker Buildx                             │  │
│  │  docker/setup-buildx-action@v3                           │  │
│  │  └─ Enable multi-platform builds & layer caching         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 3: Login to Registries                              │  │
│  │                                                           │  │
│  │  Login 1: Scaleway                                        │  │
│  │    registry: rg.fr-par.scw.cloud                         │  │
│  │    username: nologin                                      │  │
│  │    password: ${{ secrets.SCW_SECRET_KEY }}               │  │
│  │                                                           │  │
│  │  Login 2: GitHub Container Registry                       │  │
│  │    registry: ghcr.io                                      │  │
│  │    username: ${{ github.actor }}                         │  │
│  │    password: ${{ secrets.GITHUB_TOKEN }}                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 4: Build and Push Multi-Registry                    │  │
│  │                                                           │  │
│  │  Context: ./docker/base/python-{{ variant }}             │  │
│  │  Build args:                                              │  │
│  │    PYTHON_VERSION=3.11                                    │  │
│  │    VARIANT=slim                                           │  │
│  │                                                           │  │
│  │  Tags (pushed to BOTH registries):                       │  │
│  │    rg.fr-par.scw.cloud/mecapy/base/python:3.11-slim     │  │
│  │    ghcr.io/mecapy/base/python:3.11-slim                 │  │
│  │                                                           │  │
│  │  Cache:                                                   │  │
│  │    cache-from: type=gha (GitHub Actions cache)           │  │
│  │    cache-to: type=gha,mode=max                           │  │
│  │                                                           │  │
│  │  Push: true (automatic after build)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 5: Security Scan (Trivy)                            │  │
│  │                                                           │  │
│  │  aquasecurity/trivy-action@master                        │  │
│  │  ├─ Scan: rg.fr-par.scw.cloud/mecapy/base/python:...    │  │
│  │  ├─ Format: SARIF (for GitHub Security)                 │  │
│  │  ├─ Severity: CRITICAL,HIGH                              │  │
│  │  └─ Output: trivy-results.sarif                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 6: Upload Security Results                          │  │
│  │                                                           │  │
│  │  github/codeql-action/upload-sarif@v3                    │  │
│  │  └─ Uploads to GitHub Security tab for review           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

Build time per variant: 3-5 minutes
Total workflow time: 5-7 minutes (parallel execution)
Frequency: Weekly + on-demand
```

---

## 4. Disaster Recovery Mirroring Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│              CRON JOB (Worker Server)                            │
│              /usr/local/bin/mirror-critical-images.sh            │
│              Schedule: Daily at 02:00 UTC                        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Query Top 100 Most-Used Function Images                │
│                                                                   │
│  psql -c "                                                        │
│    SELECT docker_image, COUNT(*) as usage_count                 │
│    FROM tasks                                                    │
│    WHERE created_at > NOW() - INTERVAL '7 days'                 │
│    GROUP BY docker_image                                         │
│    ORDER BY usage_count DESC                                     │
│    LIMIT 100                                                     │
│  "                                                                │
│                                                                   │
│  Result: 100 image tags                                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Mirror Loop (for each image)                           │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Image: rg.fr-par.scw.cloud/mecapy/functions/user-...:v1   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Sub-step 2.1: Pull from Scaleway                          │ │
│  │  docker pull rg.fr-par.scw.cloud/mecapy/functions/...     │ │
│  │  Status: ✅ Pulled (245MB, 3.2s)                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Sub-step 2.2: Tag for GHCR                                 │ │
│  │  docker tag rg.fr-par.scw.cloud/mecapy/functions/...      │ │
│  │             ghcr.io/mecapy/functions/...                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Sub-step 2.3: Push to GHCR                                 │ │
│  │  docker push ghcr.io/mecapy/functions/...                  │ │
│  │  Status: ✅ Pushed (245MB, 12.5s to US)                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Sub-step 2.4: Log Success                                  │ │
│  │  echo "Mirrored: rg.fr-par.scw.cloud/... → ghcr.io/..."  │ │
│  │  timestamp: 2025-10-04T02:15:42Z                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         └──┐                                     │
│                            │ LOOP (100 images)                   │
│                            └──────────────────┐                  │
└────────────────────────────────────────────────┼─────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Summary Report                                          │
│                                                                   │
│  Total images processed: 100                                     │
│  Successfully mirrored: 98                                       │
│  Failed: 2                                                       │
│    - user-123-func-999:v2.0.0 (not found in Scaleway)           │
│    - user-456-func-111:v1.5.0 (push timeout to GHCR)            │
│                                                                   │
│  Total data transferred: 24.5GB                                  │
│  Total duration: 18m 32s                                         │
│                                                                   │
│  Log: /var/log/registry-mirror/2025-10-04.log                   │
│  Prometheus metric: registry_mirror_images_total{status="success"} 98 │
└─────────────────────────────────────────────────────────────────┘

Execution frequency: Daily
Average duration: 15-20 minutes
Bandwidth usage: 20-30GB/day
```

---

## 5. Image Lifecycle and Cleanup Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│              AUTOMATED CLEANUP SERVICE                           │
│              Schedule: Daily at 03:00 UTC                        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Scan Registry for All Images                           │
│                                                                   │
│  Scaleway API: GET /registry/v1/namespaces/mecapy/images        │
│                                                                   │
│  Results: 1,247 images across all namespaces                     │
│    ├─ functions/*: 1,150 images                                 │
│    ├─ base/*: 12 images                                         │
│    └─ system/*: 85 images                                       │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Apply Retention Policies                               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ POLICY 1: User Function Images (functions/*)               │ │
│  │                                                             │ │
│  │ Rules:                                                      │ │
│  │  ├─ Retention: 90 days from last pull                      │ │
│  │  ├─ Max versions: Keep 10 most recent per function        │ │
│  │  ├─ Check: Is function deleted in database?                │ │
│  │  └─ Check: Has image been pulled in last 90 days?         │ │
│  │                                                             │ │
│  │ Actions:                                                    │ │
│  │  ├─ DELETE: 87 images (orphaned, >90 days, no pulls)      │ │
│  │  ├─ KEEP: 1,063 images (active or recent)                 │ │
│  │  └─ Freed space: 17.4GB                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ POLICY 2: Base Images (base/*)                             │ │
│  │                                                             │ │
│  │ Rules:                                                      │ │
│  │  ├─ Retention: 365 days (long-term)                        │ │
│  │  ├─ Immutable: Never auto-delete tagged versions          │ │
│  │  └─ Only delete: Untagged intermediate layers             │ │
│  │                                                             │ │
│  │ Actions:                                                    │ │
│  │  ├─ DELETE: 0 images (all recent)                         │ │
│  │  ├─ KEEP: 12 images                                        │ │
│  │  └─ Freed space: 0GB                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ POLICY 3: Latest Tags                                      │ │
│  │                                                             │ │
│  │ Rules:                                                      │ │
│  │  ├─ Retention: 30 days                                     │ │
│  │  ├─ Auto-update: Point to newest version                  │ │
│  │  └─ Clean old "latest" manifests (keep only current)      │ │
│  │                                                             │ │
│  │ Actions:                                                    │ │
│  │  ├─ DELETE: 23 old manifest references                    │ │
│  │  ├─ UPDATE: 145 "latest" tags to new versions             │ │
│  │  └─ Freed space: 0.1GB                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Update Metrics and Logs                                │
│                                                                   │
│  Prometheus metrics:                                             │
│    registry_cleanup_images_deleted_total 110                    │
│    registry_cleanup_space_freed_bytes 17.5GB                    │
│    registry_storage_used_bytes 82.5GB (of 100GB free tier)     │
│                                                                   │
│  Alert: registry_storage_used_bytes < 90GB ✅ OK               │
│                                                                   │
│  Log: /var/log/registry-cleanup/2025-10-04.log                  │
│  Summary:                                                        │
│    - Scanned: 1,247 images                                      │
│    - Deleted: 110 images                                        │
│    - Freed: 17.5GB                                              │
│    - Current usage: 82.5GB / 100GB (82.5%)                      │
│    - Estimated days until limit: 45 days                        │
└─────────────────────────────────────────────────────────────────┘

Execution frequency: Daily
Average duration: 5-10 minutes
Impact: Prevents exceeding free tier, reduces clutter
```

---

## Summary of Workflows

| Workflow | Trigger | Duration | Frequency | Purpose |
|----------|---------|----------|-----------|---------|
| **User Function Build** | API POST /functions | 45-90s | On-demand | Build and push user function images |
| **Worker Image Pull** | Job from Redis | 2.2s (warm) / 3.5-5s (cold) | Per task execution | Pull image for function execution |
| **Base Image Build** | Git push / Weekly cron | 5-7 min | Weekly | Update Python base images with security patches |
| **DR Mirroring** | Daily cron | 15-20 min | Daily 02:00 UTC | Mirror top 100 images to GHCR for disaster recovery |
| **Image Cleanup** | Daily cron | 5-10 min | Daily 03:00 UTC | Delete old/unused images, free storage |

---

**Next Steps:**
1. Implement build pipeline in API (`repos/api/mecapy_api/services/docker_builder.py`)
2. Configure worker pull logic with failover (`repos/worker/mecapy_worker/container_manager.py`)
3. Set up GitHub Actions for base images (`.github/workflows/build-base-images.yml`)
4. Deploy monitoring dashboards (Grafana + Prometheus)

