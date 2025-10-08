# Workflow Git MecaPy

## Vue d'ensemble

Ce document décrit le workflow Git recommandé pour le développement de MecaPy, incluant les conventions de commit, branching strategy, et processus de collaboration.

## Architecture des dépôts

### Dépôt principal (mecapy)
```
mecapy/
├── repos/           # Sous-modules ou références aux repos
│   ├── api/        # Lien vers repo API
│   └── frontend/   # Lien vers repo Frontend  
├── docs/           # Documentation globale
├── .claude/        # Configuration Claude
└── scripts/        # Scripts de développement
```

### Dépôts séparés
- **mecapy-api** : Backend FastAPI
- **mecapy-frontend** : Frontend Next.js

## Branching Strategy

### Structure des branches

```
main (production)
├── develop (intégration)
│   ├── feat/oauth2-integration
│   ├── feat/file-upload
│   └── fix/memory-leak
├── release/v1.0.0
└── hotfix/critical-security-fix
```

### Types de branches

#### `main`
- **Production ready** code uniquement
- Toujours déployable
- Protégée : require PR + reviews
- Tagged pour releases (v1.0.0, v1.1.0, etc.)

#### `develop` (optionnel)
- Branche d'intégration
- Merge des features avant main
- Testing et validation

#### `feat/feature-name`
- Nouvelles fonctionnalités
- Nommage : `feat/description-courte`
- Basée sur `main` ou `develop`
- Supprimée après merge

#### `fix/bug-description`
- Corrections de bugs
- Nommage : `fix/description-courte`
- Basée sur `main` ou `develop`

#### `hotfix/critical-issue`
- Corrections urgentes en production
- Basée sur `main`
- Merge vers `main` ET `develop`

#### `release/v1.0.0`
- Préparation release
- Freeze features, bug fixes uniquement
- Merge vers `main` et tag

## Conventions de commit

### Structure Conventional Commits

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- **feat** : Nouvelle fonctionnalité
- **fix** : Correction de bug
- **docs** : Documentation
- **style** : Formatage (sans impact logique)
- **refactor** : Refactorisation
- **test** : Tests
- **chore** : Maintenance (deps, config)
- **perf** : Performance
- **ci** : CI/CD
- **build** : Build system

### Scopes MecaPy

- **api** : Backend FastAPI
- **frontend** : Application Next.js  
- **auth** : Authentification
- **db** : Base de données
- **docker** : Containers
- **docs** : Documentation
- **scripts** : Scripts développement

### Règles détaillées des commit messages

**Bonnes pratiques :**
- Utilisez l'impératif présent : "add" et non "added"
- Première ligne < 60 caractères
- Pas de point final dans le titre
- **Description détaillée :** optionnelle, uniquement si le titre ne suffit pas
  - Séparez du titre par une ligne vide
  - Limitez à 150 caractères
  - Expliquez le "pourquoi" plus que le "quoi"
- Ajoutez `!` après le type pour les breaking changes : `feat!:`

### Exemples de commits

```bash
# Feature
feat(auth): implement OAuth2 PKCE flow

Add OAuth2 authentication with PKCE for enhanced security.
Integrates with Keycloak for user management.

Closes #123

# Bug fix
fix(api): resolve memory leak in file upload

The file upload endpoint was not properly releasing memory
after processing large files. Fixed by implementing proper
stream cleanup.

# Documentation
docs: update API deployment guide

# Breaking change
feat(api)!: change user model structure

BREAKING CHANGE: User.display_name is now required field

# Autres exemples spécifiques MecaPy
chore(docker): update PostgreSQL to v15
perf(frontend): optimize bundle size
ci: add automated deployment pipeline
```

## Workflow de développement

### 1. Démarrer une nouvelle feature

```bash
# Mettre à jour main
git checkout main
git pull origin main

# Créer branche feature
git checkout -b feat/oauth2-integration

# Développer et committer
git add .
git commit -m "feat(auth): add OAuth2 client configuration"

# Push première fois
git push -u origin feat/oauth2-integration
```

### 2. Développement continu

```bash
# Commits réguliers
git add src/auth/
git commit -m "feat(auth): implement PKCE challenge generation"

git add tests/
git commit -m "test(auth): add OAuth2 flow tests"

# Push des changements
git push origin feat/oauth2-integration
```

### 3. Mise à jour depuis main

```bash
# Récupérer les derniers changements
git checkout main
git pull origin main

# Rebaser la feature branch
git checkout feat/oauth2-integration
git rebase main

# Résoudre conflits si nécessaire
# git add <resolved-files>
# git rebase --continue

# Push force après rebase
git push --force-with-lease origin feat/oauth2-integration
```

### 4. Pull Request

#### Création PR
```bash
# Via GitHub CLI
gh pr create --title "feat(auth): implement OAuth2 PKCE flow" \
             --body "Implements OAuth2 with PKCE for secure authentication"

# Ou via interface web GitHub
```

#### Template PR
```markdown
## Description
Brief description of changes

## Type of change
- [ ] Bug fix
- [x] New feature  
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [x] Code follows style guidelines
- [x] Self-review completed
- [x] Documentation updated
- [x] Tests added/updated
```

### 5. Review et merge

#### Review checklist
- Code quality et style
- Tests coverage
- Documentation à jour
- Pas de breaking changes non documentés
- Performance impact évalué

#### Merge strategies
```bash
# Squash merge (recommandé pour features)
git checkout main
git merge --squash feat/oauth2-integration
git commit -m "feat(auth): implement OAuth2 PKCE flow"

# Merge commit (pour releases)
git merge --no-ff release/v1.0.0

# Rebase merge (pour hotfixes)
git rebase feat/small-fix
```

## Gestion des releases

### Semantic Versioning

- **MAJOR** : Breaking changes (v1.0.0 → v2.0.0)
- **MINOR** : New features (v1.0.0 → v1.1.0)  
- **PATCH** : Bug fixes (v1.0.0 → v1.0.1)

### Processus de release

```bash
# 1. Créer branche release
git checkout -b release/v1.1.0 develop

# 2. Bump version
echo "1.1.0" > VERSION
git commit -m "chore: bump version to 1.1.0"

# 3. Tests finaux et bug fixes
git commit -m "fix: resolve last-minute bug"

# 4. Merge vers main
git checkout main
git merge --no-ff release/v1.1.0

# 5. Tag release
git tag -a v1.1.0 -m "Release version 1.1.0"

# 6. Merge vers develop
git checkout develop  
git merge main

# 7. Push tout
git push origin main develop --tags

# 8. Supprimer branche release
git branch -d release/v1.1.0
git push origin --delete release/v1.1.0
```

### Changelog automatique

```bash
# Installation
npm install -g conventional-changelog-cli

# Génération changelog
conventional-changelog -p angular -i CHANGELOG.md -s

# Commit changelog
git add CHANGELOG.md
git commit -m "docs: update changelog for v1.1.0"
```

## Collaboration multi-dépôts

### Synchronisation repos

```bash
# Dans le repo principal mecapy
cd repos/api
git pull origin main

cd ../frontend  
git pull origin main

# Commit références mises à jour
cd ../..
git add repos/
git commit -m "chore: update submodule references"
```

### Développement coordonné

1. **API First** : Développer API endpoints
2. **Frontend Integration** : Intégrer avec API
3. **Documentation** : Mettre à jour docs globales
4. **Testing** : Tests end-to-end

### Scripts utilitaires

```bash
#!/bin/bash
# scripts/sync-repos.sh

echo "Synchronizing all repositories..."

# API
cd repos/api
git checkout main
git pull origin main
echo "✅ API synchronized"

# Frontend  
cd ../frontend
git checkout main
git pull origin main
echo "✅ Frontend synchronized"

# Main repo
cd ../..
git add repos/
if ! git diff --cached --quiet; then
    git commit -m "chore: sync repository references"
    echo "✅ Main repo updated"
fi

echo "🎉 All repositories synchronized!"
```

## Bonnes pratiques

### Commits

- **Atomiques** : Un commit = une modification logique
- **Fréquents** : Committer souvent, pusher régulièrement
- **Descriptifs** : Messages clairs et complets
- **Testés** : Chaque commit doit passer les tests

### Branches

- **Courtes** : Lifecycle court pour éviter conflicts
- **Focalisées** : Une branche = une fonctionnalité
- **À jour** : Rebase régulier depuis main
- **Nettoyées** : Supprimer après merge

### Reviews

- **Constructives** : Feedback pour améliorer
- **Rapides** : Reviews dans les 24h
- **Complètes** : Code, tests, docs
- **Bienveillantes** : Respecter l'auteur

### Release

- **Planifiées** : Roadmap et calendrier
- **Testées** : QA approfondie
- **Documentées** : Changelog et migration guide
- **Sécurisées** : Backup et rollback plan

## Outils et intégrations

### Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
# Linting et tests avant commit

# API
cd repos/api
uv run ruff check || exit 1
uv run pytest || exit 1

# Frontend
cd ../frontend  
pnpm lint || exit 1
pnpm test || exit 1

echo "✅ Pre-commit checks passed"
```

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          cd repos/api && uv run pytest
          cd ../frontend && pnpm test
  
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: echo "Deploying..."
```

### Outils CLI

```bash
# Installation des outils
npm install -g commitizen
npm install -g conventional-changelog-cli
pip install pre-commit

# Configuration commitizen
echo '{"path": "cz-conventional-changelog"}' > .czrc

# Utilisation
git cz  # Aide pour commits conventional
```

---

**Version** : 1.0.0  
**Dernière mise à jour** : 2024-01-15