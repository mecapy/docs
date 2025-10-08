# Déploiement MecaPy

## Vue d'ensemble

MecaPy utilise une stratégie de déploiement multi-environnements avec des services découplés pour maximiser la flexibilité et la scalabilité.

## Architecture de déploiement

```mermaid
graph TB
    subgraph "Production"
        LB[Load Balancer]
        API1[API Instance 1]
        API2[API Instance N]
        FE[Frontend Static]
        DB[(PostgreSQL)]
        S3[Object Storage]
        KC[Keycloak]
    end
    
    subgraph "Staging"
        STAG_API[Staging API]
        STAG_FE[Staging Frontend]
        STAG_DB[(Staging DB)]
    end
    
    subgraph "Development"
        DEV[Local Docker]
    end
    
    Internet --> LB
    LB --> API1
    LB --> API2
    API1 --> DB
    API2 --> DB
    API1 --> S3
    API2 --> S3
```

## Environnements

### 1. Développement local

**Configuration** : Docker Compose

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  api:
    build: 
      context: ./repos/api
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./dev.db
      - KEYCLOAK_URL=http://keycloak:8080
      - TOKEN_VERIFICATION_ENABLED=false
    volumes:
      - ./repos/api:/app
    depends_on:
      - keycloak
      - postgres
    
  frontend:
    build:
      context: ./repos/frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NODE_ENV=development
    volumes:
      - ./repos/frontend:/app
      - /app/node_modules
    
  keycloak:
    image: quay.io/keycloak/keycloak:latest
    command: start-dev --import-realm
    ports:
      - "8080:8080"
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: keycloak
    volumes:
      - ./keycloak/realm-export.json:/opt/keycloak/data/import/realm.json
    depends_on:
      - postgres
    
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: mecapy
      POSTGRES_USER: mecapy
      POSTGRES_PASSWORD: mecapy_dev
      POSTGRES_MULTIPLE_DATABASES: keycloak
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/create-multiple-dbs.sh:/docker-entrypoint-initdb.d/create-multiple-dbs.sh

volumes:
  postgres_data:
```

**Commandes** :
```bash
# Démarrage environnement complet
docker-compose -f docker-compose.dev.yml up -d

# Logs en temps réel
docker-compose -f docker-compose.dev.yml logs -f

# Redémarrage service
docker-compose -f docker-compose.dev.yml restart api

# Nettoyage
docker-compose -f docker-compose.dev.yml down -v
```

### 2. Staging/Préprod

**Infrastructure** : Services cloud managés

- **API** : Clever Cloud app de staging
- **Frontend** : Vercel preview deployment
- **Database** : PostgreSQL managé (petite instance)
- **Keycloak** : Instance dédiée ou partagée

**Configuration** :
```bash
# Variables d'environnement staging
ENVIRONMENT=staging
DATABASE_URL=postgresql://staging_user:pass@staging-db.clever-cloud.com/mecapy_staging
KEYCLOAK_URL=https://auth-staging.mecapy.com
CORS_ALLOW_ORIGINS=https://staging.mecapy.com
LOG_LEVEL=DEBUG
```

### 3. Production

**Infrastructure** : Multi-cloud avec redondance

- **API** : Clever Cloud avec scaling automatique
- **Frontend** : Vercel avec CDN global
- **Database** : PostgreSQL managé avec réplication
- **Storage** : Scaleway Object Storage
- **Monitoring** : Sentry + DataDog (futur)

## Déploiement API (Clever Cloud)

### 1. Configuration

**Procfile** :
```
web: gunicorn mecapy_api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**Variables d'environnement** :
```bash
# Clever Cloud variables
CC_PYTHON_VERSION=3.13
CC_PIP_REQUIREMENTS_FILE=requirements.txt

# Application
DATABASE_URL=postgresql://...  # Auto-provisioned
KEYCLOAK_URL=https://auth.mecapy.com
KEYCLOAK_REALM=mecapy
KEYCLOAK_CLIENT_ID=mecapy-api
KEYCLOAK_CLIENT_SECRET=xxx

# Scaleway Object Storage
SCW_ACCESS_KEY=xxx
SCW_SECRET_KEY=xxx
CLOUD_BUCKET_UPLOADS=mecapy-uploads
CLOUD_REGION=fr-par

# Security
TOKEN_VERIFICATION_ENABLED=true
CORS_ALLOW_ORIGINS=https://mecapy.com
```

**Déploiement** :
```bash
# Clone dépôt sur Clever Cloud
git remote add clever-cloud git+ssh://git@push-par-clevercloud-customers.services.clever-cloud.com/app_xxx.git

# Push vers production
git push clever-cloud main

# Logs de déploiement
clever logs --alias mecapy-api
```

### 2. Scaling automatique

**Configuration Clever Cloud** :
```json
{
  "deploy": {
    "runtimeVersion": "3.13"
  },
  "hooks": {
    "postDeploy": "alembic upgrade head"
  },
  "scaling": {
    "minInstances": 1,
    "maxInstances": 10,
    "targetCPU": 70,
    "targetMemory": 80
  }
}
```

## Déploiement Frontend (Vercel)

### 1. Configuration

**vercel.json** :
```json
{
  "framework": "nextjs",
  "buildCommand": "pnpm build",
  "devCommand": "pnpm dev",
  "installCommand": "pnpm install",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.mecapy.com"
  },
  "regions": ["cdg1", "iad1", "syd1"],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.mecapy.com/:path*"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ]
}
```

**Variables d'environnement** :
```bash
# Production
NEXT_PUBLIC_API_URL=https://api.mecapy.com
NEXT_PUBLIC_KEYCLOAK_URL=https://auth.mecapy.com
NEXT_PUBLIC_ENVIRONMENT=production

# Preview/Staging
NEXT_PUBLIC_API_URL=https://api-staging.mecapy.com
NEXT_PUBLIC_ENVIRONMENT=staging
```

**Déploiement** :
```bash
# Installation Vercel CLI
npm i -g vercel

# Configuration projet
vercel init

# Déploiement production
vercel --prod

# Déploiement preview
vercel
```

### 2. Optimisations

**next.config.mjs** :
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Performance
  experimental: {
    optimizeCss: true,
    optimizeServerReact: true,
  },
  
  // Images
  images: {
    domains: ['mecapy-uploads.s3.fr-par.scw.cloud'],
    formats: ['image/avif', 'image/webp'],
  },
  
  // Compression
  compress: true,
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
        ],
      },
    ];
  },
};

export default nextConfig;
```

## Base de données

### 1. PostgreSQL managé

**Providers recommandés** :
- **Clever Cloud** : PostgreSQL intégré
- **Neon** : Serverless PostgreSQL
- **Railway** : PostgreSQL avec backup automatique
- **AWS RDS** : Enterprise grade

**Configuration** :
```bash
# Connection string
DATABASE_URL=postgresql://user:password@host:5432/mecapy

# Pool configuration
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### 2. Migrations

**Déploiement automatique** :
```bash
# Dans le hook post-deploy
alembic upgrade head

# Ou via script de déploiement
#!/bin/bash
set -e

echo "Running database migrations..."
python -m alembic upgrade head

echo "Starting application..."
exec "$@"
```

**Rollback procedure** :
```bash
# Identifier version cible
alembic history

# Rollback vers version spécifique
alembic downgrade <revision>

# Rollback une version
alembic downgrade -1
```

### 3. Backup et restauration

**Backup automatique** :
```bash
#!/bin/bash
# backup-db.sh

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mecapy_backup_${TIMESTAMP}.sql"

# Créer backup
pg_dump $DATABASE_URL > ${BACKUP_DIR}/${BACKUP_FILE}

# Compresser
gzip ${BACKUP_DIR}/${BACKUP_FILE}

# Upload vers S3 (optionnel)
aws s3 cp ${BACKUP_DIR}/${BACKUP_FILE}.gz s3://mecapy-backups/postgres/

# Nettoyer anciens backups (> 30 jours)
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete
```

**Cron job** :
```bash
# Backup quotidien à 2h du matin
0 2 * * * /scripts/backup-db.sh >> /var/log/backup.log 2>&1
```

## Monitoring et Logs

### 1. Logs centralisés

**Structure logs** :
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "mecapy-api",
  "environment": "production",
  "version": "1.0.0",
  "request_id": "req_123456",
  "user_id": "user_789",
  "endpoint": "/upload",
  "method": "POST",
  "status_code": 200,
  "duration_ms": 150,
  "message": "File uploaded successfully",
  "metadata": {
    "file_size": 1024,
    "file_type": "application/pdf"
  }
}
```

**Clever Cloud logs** :
```bash
# Logs en direct
clever logs --alias mecapy-api

# Logs avec filtre
clever logs --alias mecapy-api --filter "ERROR"

# Export logs
clever logs --alias mecapy-api --since 1h > api-logs-1h.txt
```

### 2. Monitoring applicatif

**Health checks** :
```python
# health.py
@app.get("/health")
async def health_check():
    checks = {
        "api": "ok",
        "database": await check_database(),
        "keycloak": await check_keycloak(),
        "storage": await check_storage(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Détermine status global
    status = "ok" if all(v == "ok" for v in checks.values() if v != checks["timestamp"]) else "degraded"
    
    return {"status": status, "checks": checks}

async def check_database():
    try:
        # Test simple query
        await database.execute("SELECT 1")
        return "ok"
    except Exception:
        return "error"
```

**Uptime monitoring** :
- **Uptimerobot** : Monitoring externe gratuit
- **Pingdom** : Monitoring professionnel
- **DataDog** : Monitoring intégré (futur)

### 3. Error tracking

**Sentry integration** :
```python
# Sentry configuration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxx@xxx.ingest.sentry.io/xxx",
    environment="production",
    traces_sample_rate=0.1,
    integrations=[
        FastApiIntegration(auto_enabling_integrations=False),
    ],
)
```

**Frontend (Next.js)** :
```javascript
// sentry.client.config.js
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
  tracesSampleRate: 0.1,
});
```

## CI/CD Pipeline

### 1. GitHub Actions

**.github/workflows/deploy.yml** :
```yaml
name: Deploy MecaPy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-api:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./repos/api
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: uv install --dev
      
      - name: Run tests
        run: uv run pytest
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/mecapy_test
      
      - name: Run linting
        run: uv run ruff check
      
      - name: Run type checking
        run: uv run mypy .

  test-frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./repos/frontend
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'pnpm'
          cache-dependency-path: './repos/frontend/pnpm-lock.yaml'
      
      - name: Install pnpm
        run: npm install -g pnpm
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Run linting
        run: pnpm lint
      
      - name: Run type checking
        run: pnpm build
      
      - name: Run tests
        run: pnpm test # À implémenter

  deploy-api:
    needs: [test-api]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Deploy to Clever Cloud
        run: |
          git remote add clever-cloud ${{ secrets.CLEVER_CLOUD_GIT_URL }}
          git subtree push --prefix=repos/api clever-cloud main
        env:
          CLEVER_CLOUD_GIT_URL: ${{ secrets.CLEVER_CLOUD_GIT_URL }}

  deploy-frontend:
    needs: [test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./repos/frontend
          vercel-args: --prod
```

### 2. Secrets management

**GitHub Secrets** :
```bash
# Clever Cloud
CLEVER_CLOUD_GIT_URL=git+ssh://git@push-par-clevercloud-customers.services.clever-cloud.com/app_xxx.git

# Vercel
VERCEL_TOKEN=xxx
VERCEL_ORG_ID=xxx
VERCEL_PROJECT_ID=xxx

# Sentry
SENTRY_AUTH_TOKEN=xxx
SENTRY_DSN=xxx
```

### 3. Rollback strategy

**API Rollback** :
```bash
# Via Clever Cloud console ou CLI
clever restart --alias mecapy-api --commit <previous_commit>

# Ou rollback base de données si nécessaire
alembic downgrade <previous_revision>
```

**Frontend Rollback** :
```bash
# Via Vercel dashboard ou CLI
vercel rollback <deployment_url>
```

## Sécurité déploiement

### 1. Secrets et configuration

**Bonnes pratiques** :
- Jamais de secrets en dur dans le code
- Variables d'environnement différentes par environnement
- Rotation régulière des clés API
- Accès minimum requis (principle of least privilege)

### 2. Network security

**Production** :
- HTTPS obligatoire (Let's Encrypt)
- WAF (Web Application Firewall) si nécessaire
- Rate limiting par IP
- Monitoring des tentatives d'intrusion

### 3. Database security

**PostgreSQL** :
- Connexions SSL uniquement
- Users avec permissions minimales
- Backup encryption
- Regular security updates

## Disaster Recovery

### 1. Backup strategy

**Composants à sauvegarder** :
- Base de données (quotidien)
- Configuration Keycloak (hebdomadaire)
- Code source (Git + mirrors)
- Fichiers Object Storage (stratégie définie)

### 2. Recovery procedures

**Database Recovery** :
```bash
# Restauration depuis backup
psql $DATABASE_URL < backup.sql

# Ou point-in-time recovery si supporté
# Dépend du provider de DB
```

**Application Recovery** :
```bash
# Redéploiement depuis Git
git checkout <stable_commit>
git push clever-cloud main

# Rollback migrations si nécessaire
alembic downgrade <revision>
```

### 3. RTO/RPO Targets

- **RTO (Recovery Time Objective)** : < 4 heures
- **RPO (Recovery Point Objective)** : < 24 heures
- **Availability Target** : 99.5% (43.8 heures downtime/an)

---

**Version** : 1.0.0  
**Dernière mise à jour** : 2024-01-15