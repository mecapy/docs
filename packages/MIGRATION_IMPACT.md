# 🔄 Impact de la migration vers mecapy.yml

## Résumé

Migration du format `mecapy.package.yaml` (verbeux) vers `mecapy.yml` (minimal).

**Réduction** : 304 lignes → 40 lignes (**-87%**)

---

## 📦 Dépôts impactés

### 1. Backend API (`repos/api/`)

#### Fichiers à modifier

| Fichier | Type | Modification requise |
|---------|------|---------------------|
| `mecapy_api/services/package_git_service.py:106` | Code | Chercher `mecapy.yml` OU `mecapy.package.yaml` |
| `mecapy_api/services/package_parser.py` | Code | **Nouveau parser pour format minimal** |
| `mecapy_api/routes/packages.py` | Doc | Mettre à jour docstring avec `mecapy.yml` |
| `mecapy_api/services/versioning_service.py` | Message | Mettre à jour messages d'erreur |
| `tests/test_packages_routes.py` | Tests | Mettre à jour chemins vers `mecapy.yml` |
| `tests/test_git_tag_validator.py` | Tests | Mettre à jour messages |

#### Nouveaux composants nécessaires

1. **Introspection Engine** (`mecapy_api/services/introspection_service.py`)
   - Parse type hints Python (typing, Annotated, Pydantic Field)
   - Extrait docstrings NumPy
   - Génère JSON schemas automatiquement
   - Détecte TypedDict pour output schemas

2. **Minimal Manifest Parser** (`mecapy_api/services/minimal_manifest_parser.py`)
   - Parse le nouveau format `mecapy.yml`
   - Délègue à l'introspection pour les schemas
   - Compatible avec ancien format (rétrocompatibilité)

3. **Schema Generator** (`mecapy_api/services/schema_generator.py`)
   - Génère input schemas depuis type hints
   - Génère output schemas depuis TypedDict
   - Utilise Pydantic pour validation

---

### 2. Functions Example (`repos/functions/example/`)

#### Modifications effectuées ✅

- [x] Création de `mecapy.yml` (nouveau format)
- [x] Conservation de `mecapy.package.yaml` (rétrocompatibilité temporaire)
- [x] Documentation : `docs/MANIFEST_INTROSPECTION.md`
- [x] Documentation : `docs/MIGRATION_IMPACT.md` (ce fichier)

#### À faire

- [ ] Améliorer les type hints dans `example/vis.py` pour introspection optimale
- [ ] Ajouter TypedDict pour les retours structurés
- [ ] Migrer les exemples vers les tests pytest

---

### 3. Python SDK (`repos/python-sdk/`)

#### Impact minimal

Le SDK consomme l'API, pas le manifest directement.

**Aucune modification requise** tant que l'API reste compatible.

---

### 4. Documentation globale (`docs/`)

#### Fichiers à créer/mettre à jour

- [ ] `docs/MANIFEST_FORMAT.md` - Spécification complète du format `mecapy.yml`
- [ ] `docs/INTROSPECTION_RULES.md` - Règles d'introspection détaillées
- [ ] `docs/MIGRATION_GUIDE.md` - Guide de migration depuis ancien format

---

## 🔧 Plan de migration

### Phase 1 : Backend API (priorité haute)

```bash
cd repos/api

# 1. Créer le service d'introspection
touch mecapy_api/services/introspection_service.py

# 2. Créer le parser minimal
touch mecapy_api/services/minimal_manifest_parser.py

# 3. Mettre à jour package_git_service.py
# Supporter mecapy.yml ET mecapy.package.yaml (rétrocompatibilité)

# 4. Mettre à jour les tests
# Créer test_introspection_service.py
# Créer test_minimal_manifest_parser.py
```

### Phase 2 : Tests et validation

```bash
# 1. Tester avec repos/functions/example
# Déployer avec mecapy.yml
# Vérifier introspection des schemas

# 2. Tester rétrocompatibilité
# Déployer avec mecapy.package.yaml
# Vérifier que tout fonctionne
```

### Phase 3 : Documentation

```bash
# Créer guides utilisateurs
docs/MANIFEST_FORMAT.md
docs/INTROSPECTION_RULES.md
docs/MIGRATION_GUIDE.md
```

### Phase 4 : Migration complète

```bash
# Déprécier mecapy.package.yaml (6 mois)
# Garder rétrocompatibilité pendant transition
# Supprimer support ancien format après migration utilisateurs
```

---

## 🎯 Stratégie de rétrocompatibilité

### Détection automatique du format

```python
def find_package_manifest(repo_path: Path) -> tuple[Path, str]:
    """
    Find package manifest (mecapy.yml or mecapy.package.yaml).

    Returns
    -------
    tuple[Path, str]
        (manifest_path, format_type)
        format_type: "minimal" or "verbose"
    """
    # Priorité au nouveau format
    minimal_path = repo_path / "mecapy.yml"
    if minimal_path.exists():
        return minimal_path, "minimal"

    # Fallback vers ancien format
    verbose_path = repo_path / "mecapy.package.yaml"
    if verbose_path.exists():
        return verbose_path, "verbose"

    raise PackageNotFoundError(
        "No manifest found. Expected mecapy.yml or mecapy.package.yaml"
    )
```

### Parser unifié

```python
class UnifiedManifestParser:
    """Parser unifié supportant les deux formats."""

    def __init__(self):
        self.minimal_parser = MinimalManifestParser()
        self.verbose_parser = PackageManifestParser()
        self.introspection = IntrospectionService()

    def parse(self, manifest_path: Path) -> PackageManifest:
        """Parse manifest (auto-détecte le format)."""
        format_type = self._detect_format(manifest_path)

        if format_type == "minimal":
            # Parse minimal + introspection
            manifest = self.minimal_parser.parse(manifest_path)
            return self._enrich_with_introspection(manifest)
        else:
            # Parse verbose (ancien format)
            return self.verbose_parser.parse_manifest(manifest_path.read_text())
```

---

## 📊 Checklist de migration

### Backend API

- [ ] Créer `IntrospectionService` pour analyser type hints
- [ ] Créer `MinimalManifestParser` pour nouveau format
- [ ] Créer `SchemaGenerator` pour générer JSON schemas
- [ ] Mettre à jour `PackageGitService.find_package_manifest()`
- [ ] Ajouter tests pour introspection
- [ ] Ajouter tests pour parser minimal
- [ ] Mettre à jour documentation API

### Functions Example

- [x] Créer `mecapy.yml`
- [ ] Améliorer type hints dans le code Python
- [ ] Ajouter TypedDict pour retours
- [ ] Migrer exemples vers tests

### Documentation

- [ ] Créer `MANIFEST_FORMAT.md`
- [ ] Créer `INTROSPECTION_RULES.md`
- [ ] Créer `MIGRATION_GUIDE.md`
- [x] Créer `MANIFEST_INTROSPECTION.md`

### Déploiement

- [ ] Tester déploiement avec nouveau format
- [ ] Tester rétrocompatibilité ancien format
- [ ] Valider génération automatique des schemas
- [ ] Valider versioning automatique

---

## 🚨 Risques et mitigation

| Risque | Impact | Mitigation |
|--------|--------|------------|
| **Breaking change** pour utilisateurs existants | Élevé | Rétrocompatibilité avec ancien format pendant 6 mois |
| **Introspection échoue** si type hints manquants | Moyen | Validation au déploiement + messages d'erreur clairs |
| **Schemas incorrects** générés | Élevé | Tests automatiques + validation avec testcases |
| **Performance** de l'introspection | Faible | Cache des schemas générés |

---

## 📝 Notes de développement

### Type hints requis pour introspection optimale

```python
from typing import Annotated, Literal, TypedDict
from pydantic import Field

# ✅ BON - introspection complète
def calcul(
    force: Annotated[float, Field(
        description="Force en N",
        ge=0,
        le=500000
    )]
) -> ResultatDict:
    ...

# ⚠️ MOYEN - introspection partielle
def calcul(force: float) -> dict:
    ...

# ❌ MAUVAIS - pas d'introspection
def calcul(force):
    ...
```

### Docstrings NumPy pour descriptions

```python
def calcul(force: float) -> dict:
    """
    Calcule la contrainte.

    Parameters
    ----------
    force : float
        Force de traction appliquée en Newton.
        Doit être positive.

    Returns
    -------
    dict
        Résultats avec les clés:
        - contrainte : float
            Contrainte calculée en MPa
        - statut : str
            État ('OK', 'LIMITE', 'RUPTURE')
    """
```

---

**Prochaine étape** : Implémenter l'introspection service dans le backend API.
