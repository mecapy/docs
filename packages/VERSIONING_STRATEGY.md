# 🔖 Stratégie de Versioning MecaPy

## 🎯 Principe : Versioning au Niveau Package

### Recommandation : **Versioning Sémantique du Package**

Le package entier a une version, toutes les fonctions héritent de cette version.

## 📋 Format de Version

### Semantic Versioning (SemVer 2.0)

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

Exemples :
  1.0.0           Version stable
  1.2.3           Bug fix
  2.0.0           Breaking change
  1.0.0-alpha.1   Pre-release
  1.0.0+20250104  Build metadata
```

### Règles SemVer

- **MAJOR** : Changements incompatibles (breaking changes)
- **MINOR** : Nouvelles fonctionnalités (backward compatible)
- **PATCH** : Corrections de bugs (backward compatible)

## 🏗️ Architecture de Versioning

### Option A : Versioning Unique du Package (Recommandé)

**Tout le package partage la même version.**

```yaml
# mecapy.package.yaml
version: "1.0"
kind: "package"

package:
  name: "mecapy-boulonnerie"
  version: "2.1.0"  # Version du package entier

functions:
  calcul-contrainte:
    handler: "boulonnerie.calculs:contrainte_traction"
    # Hérite de la version 2.1.0

  calcul-cisaillement:
    handler: "boulonnerie.calculs:cisaillement"
    # Hérite de la version 2.1.0

  optimisation-diametre:
    handler: "boulonnerie.optimisation:optimiser"
    # Hérite de la version 2.1.0
```

**Avantages** :
- ✅ Simple à gérer
- ✅ Cohérence garantie entre fonctions
- ✅ Un seul tag Git = tout le package
- ✅ Pas de conflits de dépendances

**Inconvénients** :
- ❌ Toutes les fonctions changent de version même si une seule change

---

### Option B : Versioning Hybride (Flexible)

**Package a une version, fonctions peuvent override.**

```yaml
package:
  name: "mecapy-boulonnerie"
  version: "2.1.0"  # Version globale du package

functions:
  # Fonction stable - suit la version du package
  calcul-contrainte:
    handler: "boulonnerie.calculs:contrainte_traction"
    # version: 2.1.0 (hérité)

  # Fonction en développement - override
  calcul-cisaillement:
    handler: "boulonnerie.calculs:cisaillement"
    version: "2.2.0-beta.1"  # Override pour testing
    deprecated: false

  # Fonction obsolète
  ancien-calcul:
    handler: "boulonnerie.legacy:old_calc"
    version: "1.5.0"
    deprecated: true
    deprecated_message: "Utilisez 'calcul-contrainte' à la place"
    removal_version: "3.0.0"
```

**Avantages** :
- ✅ Flexibilité pour fonctions expérimentales
- ✅ Dépréciation progressive
- ✅ Beta testing de nouvelles fonctions

**Inconvénients** :
- ❌ Plus complexe à gérer
- ❌ Risque de dépendances conflictuelles

---

### Option C : Versioning par Fonction (Déconseillé)

**Chaque fonction a sa propre version indépendante.**

```yaml
package:
  name: "mecapy-boulonnerie"
  # Pas de version au niveau package

functions:
  calcul-contrainte:
    handler: "boulonnerie.calculs:contrainte_traction"
    version: "3.2.1"

  calcul-cisaillement:
    handler: "boulonnerie.calculs:cisaillement"
    version: "1.0.5"

  optimisation:
    handler: "boulonnerie.optimisation:optimiser"
    version: "2.4.0"
```

**Avantages** :
- ✅ Granularité maximale

**Inconvénients** :
- ❌ Complexité de gestion
- ❌ Risque d'incompatibilités entre fonctions du même package
- ❌ Git tags ambigus (v3.2.1 de quelle fonction ?)

---

## 🔄 Workflow de Versioning Recommandé

### 1. Développement Initial

```bash
# mecapy.package.yaml
package:
  version: "0.1.0"  # Version initiale en développement

# Git
git tag v0.1.0
git push origin v0.1.0
```

### 2. Ajout de Nouvelles Fonctions (MINOR)

```bash
# Ajout de calcul_cisaillement
# mecapy.package.yaml
package:
  version: "0.2.0"  # +1 MINOR (nouvelle feature)

git tag v0.2.0
git push origin v0.2.0
```

### 3. Bug Fix (PATCH)

```bash
# Correction d'un bug dans calcul_contrainte
# mecapy.package.yaml
package:
  version: "0.2.1"  # +1 PATCH (bug fix)

git tag v0.2.1
git push origin v0.2.1
```

### 4. Breaking Change (MAJOR)

```bash
# Changement de signature de calcul_contrainte
# mecapy.package.yaml
package:
  version: "1.0.0"  # +1 MAJOR (breaking change)

git tag v1.0.0
git push origin v1.0.0
```

### 5. Pre-release (Alpha/Beta)

```bash
# Nouvelle fonction expérimentale
# mecapy.package.yaml
package:
  version: "1.1.0-beta.1"

git tag v1.1.0-beta.1
git push origin v1.1.0-beta.1
```

## 📦 Déploiement par Version

### Déployer une Version Spécifique

```bash
# Via tag Git
POST /packages/from-git
{
  "git_url": "https://github.com/user/mecapy-boulonnerie.git",
  "ref": "v2.1.0"  # Tag Git
}

# Via branche
POST /packages/from-git
{
  "git_url": "https://github.com/user/mecapy-boulonnerie.git",
  "ref": "main"     # Dernière version sur main
}

# Via commit SHA
POST /packages/from-git
{
  "git_url": "https://github.com/user/mecapy-boulonnerie.git",
  "ref": "4063bfe..."  # Commit spécifique
}
```

### Gestion Multi-Versions

**MecaPy peut héberger plusieurs versions du même package simultanément :**

```python
# Base de données
class PackageVersion(SQLModel, table=True):
    id: str = Field(primary_key=True)
    package_id: str = Field(foreign_key="package.id")
    version: str  # "2.1.0"
    git_ref: str  # "v2.1.0"
    git_commit: str  # SHA complet
    is_latest: bool = False  # Marqueur version courante
    is_stable: bool = True   # vs pre-release
    created_at: datetime

    # Relations
    functions: List["FunctionVersion"] = Relationship()


class FunctionVersion(SQLModel, table=True):
    id: str = Field(primary_key=True)
    function_id: str = Field(foreign_key="function.id")
    package_version_id: str = Field(foreign_key="packageversion.id")
    version: str  # Hérite du package ou override
    handler: str  # Import path
    code_checksum: str  # Pour détection changements
```

**Appeler une version spécifique :**

```bash
# Version latest (par défaut)
POST /packages/mecapy-boulonnerie/functions/calcul-contrainte/execute
{
  "inputs": {...}
}

# Version spécifique
POST /packages/mecapy-boulonnerie@2.1.0/functions/calcul-contrainte/execute
{
  "inputs": {...}
}

# Via function ID (immutable)
POST /functions/func_abc123/execute
{
  "inputs": {...}
}
```

## 🔀 Gestion des Changements

### Changelog Automatique

**mecapy.package.yaml** :
```yaml
package:
  name: "mecapy-boulonnerie"
  version: "2.1.0"

  changelog:
    "2.1.0":
      date: "2025-01-15"
      changes:
        - type: "feature"
          description: "Ajout calcul de précharge pour boulons HR"
          functions: ["calcul-precharge"]
        - type: "fix"
          description: "Correction calcul section résistante M6"
          functions: ["calcul-contrainte"]
          issue: "https://github.com/user/repo/issues/42"

    "2.0.0":
      date: "2025-01-01"
      changes:
        - type: "breaking"
          description: "Signature de calcul_contrainte changée"
          functions: ["calcul-contrainte"]
          migration: |
            Ancien: calcul_contrainte(force, section)
            Nouveau: calcul_contrainte(force, diametre, materiau)
```

### Migration Guide

**Pour Breaking Changes (MAJOR version)** :

```yaml
package:
  version: "2.0.0"

  migration_guide:
    from: "1.x"
    to: "2.0.0"

    breaking_changes:
      - function: "calcul-contrainte"
        change: "Paramètre 'section' remplacé par 'diametre'"
        before: |
          {
            "force": 10000,
            "section": 84.1
          }
        after: |
          {
            "force": 10000,
            "diametre": 12
          }

      - function: "calcul-cisaillement"
        change: "Ajout paramètre obligatoire 'nb_plans'"
        after: |
          {
            "force": 5000,
            "diametre": 12,
            "nb_plans": 2  # Nouveau paramètre obligatoire
          }
```

## 🏷️ Tags Git : Conventions

### Format Recommandé

```bash
# Releases stables
v1.0.0
v1.2.3
v2.0.0

# Pre-releases
v1.0.0-alpha.1
v1.0.0-beta.2
v1.0.0-rc.1

# Build metadata (optionnel)
v1.0.0+20250104
v1.0.0-beta.1+exp.sha.5114f85
```

### Script de Release

```bash
#!/bin/bash
# scripts/release.sh

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/release.sh <version>"
  exit 1
fi

# 1. Mettre à jour le manifeste
sed -i "s/version: \".*\"/version: \"$VERSION\"/" mecapy.package.yaml

# 2. Commit
git add mecapy.package.yaml
git commit -m "chore: bump version to $VERSION"

# 3. Tag
git tag -a "v$VERSION" -m "Release v$VERSION"

# 4. Push
git push origin main
git push origin "v$VERSION"

echo "✅ Released v$VERSION"
```

## 📊 Matrice de Compatibilité

### Entre Versions de Package

```yaml
package:
  name: "mecapy-boulonnerie"
  version: "2.1.0"

  compatibility:
    # Versions compatibles ascendantes
    compatible_with:
      - "2.0.0"
      - "2.0.1"
      - "2.1.0"

    # Versions incompatibles (breaking)
    breaking_changes_from:
      - "1.x"

    # Dépendances d'autres packages
    dependencies:
      mecapy-materiaux: ">=1.5.0,<2.0.0"  # Style npm/pip
      mecapy-eurocodes: "^3.2.0"          # Style npm caret
```

## 🔄 Rolling Updates et Canary Deployments

### Déploiement Progressif

```yaml
# Stratégie de déploiement pour nouvelle version
deployment:
  strategy: "rolling"  # ou "blue-green", "canary"

  # Canary: 10% du traffic sur v2.1.0, 90% sur v2.0.0
  canary:
    enabled: true
    traffic_split:
      "2.1.0": 10
      "2.0.0": 90
    duration: "24h"  # Après 24h, basculer à 100% si OK

    # Métriques de succès
    success_criteria:
      error_rate_max: 0.01  # 1% max
      latency_p95_max: 500  # ms
```

## 💡 Recommandation Finale

### Stratégie Recommandée : **Option A + Git Tags**

1. **Versioning unique du package** (simple, cohérent)
2. **SemVer strict** (MAJOR.MINOR.PATCH)
3. **Git tags** pour chaque release (v1.2.3)
4. **Changelog dans le manifeste** (traçabilité)
5. **Support multi-versions** en production (migration douce)

### Workflow Type

```bash
# Développement
git checkout -b feature/nouvelle-fonction
# ... développement ...
git commit -m "feat: add calcul_precharge"

# Merge
git checkout main
git merge feature/nouvelle-fonction

# Release
./scripts/release.sh 2.1.0  # Auto: manifeste + tag + push

# Déploiement
curl -X POST /packages/from-git \
  -d '{"git_url": "...", "ref": "v2.1.0"}'
```

---

**Cette approche offre le meilleur équilibre simplicité/flexibilité !** 🎯
