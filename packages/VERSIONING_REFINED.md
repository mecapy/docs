# 🔖 Versioning Raffiné : Package + Fonction

## 🎯 Problème Identifié

**Scénario** :
```yaml
# v1.0.0 du package
functions:
  calcul-contrainte: "vis:calc_contrainte"  # Fonction A
  calcul-cisaillement: "vis:calc_cisaillement"  # Fonction B

# v1.1.0 du package
functions:
  calcul-contrainte: "vis:calc_contrainte"  # Fonction A (INCHANGÉE)
  calcul-cisaillement: "vis:calc_cisaillement"  # Fonction B (modifiée)
  calcul-precharge: "vis:calc_precharge"  # Fonction C (nouvelle)
```

**Problème** : Un utilisateur de `calcul-contrainte` voit passer la version de 1.0.0 à 1.1.0 alors que **sa fonction n'a pas changé**.

## 💡 Solution : Versioning à Deux Niveaux

### Principe : **Package Version + Function Checksum**

```yaml
# mecapy.package.yaml
package:
  name: "mecapy-boulonnerie"
  version: "1.1.0"  # Version du package (métadonnées)

functions:
  calcul-contrainte:
    handler: "boulonnerie.vis:calculer_contrainte"
    version: "1.0.0"  # Version de la fonction (automatique ou manuelle)
    checksum: "sha256:4f3b2a..."  # Hash du code de la fonction

  calcul-cisaillement:
    handler: "boulonnerie.vis:calculer_cisaillement"
    version: "1.1.0"  # A changé dans cette release
    checksum: "sha256:8d7c1e..."

  calcul-precharge:
    handler: "boulonnerie.vis:calculer_precharge"
    version: "1.1.0"  # Nouvelle fonction
    checksum: "sha256:2a9f5b..."
```

## 🔧 Système de Versioning Automatique

### Option 1 : Versioning Automatique par Checksum (Recommandé)

**Le système MecaPy calcule automatiquement la version de chaque fonction.**

```python
import hashlib
import inspect

def calculate_function_checksum(module_path: str, function_name: str) -> str:
    """Calcule le checksum d'une fonction."""
    # Importer la fonction
    module = importlib.import_module(module_path)
    func = getattr(module, function_name)

    # Obtenir le code source
    source = inspect.getsource(func)

    # Calculer SHA256
    return hashlib.sha256(source.encode()).hexdigest()


def auto_version_function(
    previous_version: str,
    previous_checksum: str,
    current_checksum: str
) -> str:
    """Détermine automatiquement la nouvelle version."""
    if current_checksum == previous_checksum:
        # Code inchangé → version inchangée
        return previous_version
    else:
        # Code changé → bump PATCH
        major, minor, patch = previous_version.split('.')
        return f"{major}.{minor}.{int(patch) + 1}"
```

**Workflow** :

```bash
# Déploiement v1.1.0 du package
POST /packages/from-git
{
  "git_url": "...",
  "ref": "v1.1.0"
}

# MecaPy analyse automatiquement :
# - calcul-contrainte: checksum identique → v1.0.0 (inchangé)
# - calcul-cisaillement: checksum différent → v1.0.1 (auto-bump)
# - calcul-precharge: nouvelle fonction → v1.1.0 (nouvelle)
```

**Réponse API** :
```json
{
  "package_version": "1.1.0",
  "functions": [
    {
      "name": "calcul-contrainte",
      "version": "1.0.0",  // INCHANGÉ
      "checksum": "4f3b2a...",
      "status": "unchanged"
    },
    {
      "name": "calcul-cisaillement",
      "version": "1.0.1",  // AUTO-BUMPED
      "checksum": "8d7c1e...",
      "status": "updated",
      "changelog": "Code source modifié"
    },
    {
      "name": "calcul-precharge",
      "version": "1.1.0",  // NOUVELLE
      "checksum": "2a9f5b...",
      "status": "new"
    }
  ]
}
```

---

### Option 2 : Versioning Manuel avec Vérification

**L'utilisateur spécifie les versions, MecaPy vérifie la cohérence.**

```yaml
# mecapy.package.yaml
package:
  version: "1.1.0"

functions:
  calcul-contrainte:
    handler: "boulonnerie.vis:calculer_contrainte"
    version: "1.0.0"  # Manuel : l'utilisateur dit "pas changé"

  calcul-cisaillement:
    handler: "boulonnerie.vis:calculer_cisaillement"
    version: "1.1.0"  # Manuel : l'utilisateur dit "changé"

  calcul-precharge:
    handler: "boulonnerie.vis:calculer_precharge"
    version: "1.1.0"  # Manuel : nouvelle fonction
```

**MecaPy vérifie** :
```python
# Au déploiement
if function_version == previous_version:
    # Vérifier que le checksum n'a pas changé
    if current_checksum != previous_checksum:
        raise ValueError(
            f"Version inchangée ({function_version}) mais code modifié. "
            f"Veuillez bumper la version."
        )
```

---

### Option 3 : Versioning Mixte (Flexible)

**Combinaison auto + manuel.**

```yaml
package:
  version: "1.1.0"
  versioning_strategy: "auto"  # ou "manual"

functions:
  # Auto : MecaPy calcule automatiquement
  calcul-contrainte:
    handler: "boulonnerie.vis:calculer_contrainte"
    versioning: "auto"
    # version sera calculée automatiquement

  # Manuel : l'utilisateur contrôle
  calcul-cisaillement:
    handler: "boulonnerie.vis:calculer_cisaillement"
    versioning: "manual"
    version: "2.0.0"  # Breaking change manuel
    changelog: "Signature changée : ajout paramètre 'nb_plans'"
```

---

## 🏗️ Architecture Base de Données

```python
class Function(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    package_id: str = Field(foreign_key="package.id")

    # Version actuelle (immutable)
    current_version: str

    # Relations vers toutes les versions
    versions: List["FunctionVersion"] = Relationship(back_populates="function")


class FunctionVersion(SQLModel, table=True):
    """Chaque version de fonction est immutable."""
    id: str = Field(primary_key=True)  # func_abc123_v1.0.0
    function_id: str = Field(foreign_key="function.id")
    package_version_id: str = Field(foreign_key="packageversion.id")

    # Version de cette fonction spécifique
    version: str  # "1.0.0", "1.0.1", "2.0.0"

    # Code et métadonnées (immutable)
    handler: str  # Import path
    code_checksum: str  # SHA256 du code
    inputs_schema: dict
    outputs_schema: dict

    # Métadonnées de changement
    changelog: Optional[str] = None
    is_breaking_change: bool = False
    deprecated: bool = False

    # Timestamps
    created_at: datetime
    deployed_at: datetime


class PackageVersion(SQLModel, table=True):
    id: str = Field(primary_key=True)
    package_id: str = Field(foreign_key="package.id")
    version: str  # Version du package
    git_ref: str
    git_commit: str

    # Relations vers fonctions de cette version du package
    function_versions: List["FunctionVersion"] = Relationship()
```

## 📋 API : Vues Utilisateur

### Vue 1 : Par Fonction (Recommandé pour l'Utilisateur)

**L'utilisateur voit uniquement les versions de SA fonction.**

```bash
# Lister les versions d'une fonction
GET /functions/calcul-contrainte/versions

Response:
{
  "function": "calcul-contrainte",
  "current_version": "1.0.0",
  "versions": [
    {
      "version": "1.0.0",
      "deployed_at": "2025-01-01T10:00:00Z",
      "package_version": "1.0.0",
      "changelog": "Version initiale",
      "deprecated": false
    },
    {
      "version": "1.0.0",  // Même version !
      "deployed_at": "2025-01-15T14:00:00Z",
      "package_version": "1.1.0",  // Package a bougé
      "changelog": "Aucun changement (autres fonctions modifiées)",
      "deprecated": false
    }
  ]
}
```

**Point clé** : L'utilisateur voit que sa fonction est toujours en v1.0.0, même si le package est passé à v1.1.0.

### Vue 2 : Par Package (Pour l'Administrateur)

```bash
GET /packages/mecapy-boulonnerie/versions

Response:
{
  "package": "mecapy-boulonnerie",
  "current_version": "1.1.0",
  "versions": [
    {
      "version": "1.0.0",
      "deployed_at": "2025-01-01T10:00:00Z",
      "functions": [
        {"name": "calcul-contrainte", "version": "1.0.0"},
        {"name": "calcul-cisaillement", "version": "1.0.0"}
      ]
    },
    {
      "version": "1.1.0",
      "deployed_at": "2025-01-15T14:00:00Z",
      "functions": [
        {"name": "calcul-contrainte", "version": "1.0.0"},  // Inchangé
        {"name": "calcul-cisaillement", "version": "1.0.1"},  // Bumped
        {"name": "calcul-precharge", "version": "1.1.0"}  // Nouveau
      ],
      "changelog": "Ajout calcul-precharge, fix calcul-cisaillement"
    }
  ]
}
```

## 🎯 Appels de Fonction : Immutabilité Garantie

### Principe : Function Version ID (Immutable)

```bash
# Lors du premier déploiement
POST /packages/from-git {"ref": "v1.0.0"}

Response:
{
  "functions": [
    {
      "id": "func_abc123",  // Immutable ID
      "name": "calcul-contrainte",
      "version": "1.0.0",
      "version_id": "funcver_xyz789",  // ID de cette version spécifique
      "endpoint": "/functions/func_abc123/execute"
    }
  ]
}
```

**L'utilisateur peut appeler de 3 façons** :

```bash
# 1. Via function ID (immutable, toujours v1.0.0)
POST /functions/func_abc123/execute
{
  "inputs": {"force": 10000, "diametre": 12}
}

# 2. Via nom + version explicite
POST /packages/mecapy-boulonnerie/functions/calcul-contrainte@1.0.0/execute
{
  "inputs": {"force": 10000, "diametre": 12}
}

# 3. Via nom (latest version de cette fonction)
POST /packages/mecapy-boulonnerie/functions/calcul-contrainte/execute
{
  "inputs": {"force": 10000, "diametre": 12}
}
# Retourne v1.0.0 même si package est en v1.1.0
```

## 📊 Changelog Automatique

**MecaPy génère automatiquement le changelog de chaque fonction.**

```python
def generate_function_changelog(
    function_name: str,
    old_version: FunctionVersion,
    new_version: FunctionVersion
) -> str:
    """Génère le changelog d'une fonction."""

    # Comparer les checksums
    if old_version.code_checksum == new_version.code_checksum:
        return "Aucun changement de code"

    # Analyser les différences de signature
    old_sig = inspect.signature(old_version.handler)
    new_sig = inspect.signature(new_version.handler)

    changes = []

    # Paramètres ajoutés
    new_params = set(new_sig.parameters) - set(old_sig.parameters)
    if new_params:
        changes.append(f"Nouveaux paramètres: {', '.join(new_params)}")

    # Paramètres supprimés (BREAKING)
    removed_params = set(old_sig.parameters) - set(new_sig.parameters)
    if removed_params:
        changes.append(f"⚠️ BREAKING: Paramètres supprimés: {', '.join(removed_params)}")

    # Comparer les schémas I/O
    if old_version.inputs_schema != new_version.inputs_schema:
        changes.append("Schéma d'entrée modifié")

    if old_version.outputs_schema != new_version.outputs_schema:
        changes.append("Schéma de sortie modifié")

    return " | ".join(changes) if changes else "Code source modifié"
```

## 💡 Recommandation Finale : Option 1 (Auto) + Immutabilité

### Workflow Utilisateur

**Développeur du package** :
```bash
# 1. Développer
git checkout -b feature/fix-cisaillement
# Modifier boulonnerie/vis.py:calculer_cisaillement

# 2. Commit
git commit -m "fix: correction calcul cisaillement pour M6"

# 3. Release package (sans bumper les versions de fonctions manuellement)
git tag v1.1.0
git push origin v1.1.0

# 4. Déployer
POST /packages/from-git {"ref": "v1.1.0"}
# MecaPy détecte automatiquement :
# - calcul-contrainte: v1.0.0 (checksum identique, pas de bump)
# - calcul-cisaillement: v1.0.1 (checksum différent, auto-bump PATCH)
```

**Utilisateur de calcul-contrainte** :
```bash
# Appel avant v1.1.0 du package
POST /functions/func_abc123/execute
# Utilise calcul-contrainte v1.0.0

# Appel après v1.1.0 du package
POST /functions/func_abc123/execute
# Utilise TOUJOURS calcul-contrainte v1.0.0 (immutable)
# ✅ Aucun changement visible pour cet utilisateur

# Pour migrer vers une nouvelle version (si disponible)
POST /packages/mecapy-boulonnerie/functions/calcul-contrainte@latest/execute
# Utilise la dernière version de calcul-contrainte
```

**Utilisateur de calcul-cisaillement** :
```bash
# Appel avant v1.1.0
POST /functions/func_def456/execute
# Utilise calcul-cisaillement v1.0.0

# Appel après v1.1.0
POST /functions/func_def456/execute
# Utilise TOUJOURS v1.0.0 (immutable)

# Pour utiliser le fix
POST /packages/mecapy-boulonnerie/functions/calcul-cisaillement@1.0.1/execute
# Utilise calcul-cisaillement v1.0.1 (avec le fix)
```

## 🎯 Résumé

1. **Package a une version** : métadonnée organisationnelle
2. **Chaque fonction a SA propre version** : auto-calculée par checksum
3. **Function ID immutable** : garantit stabilité pour utilisateurs
4. **Changelog automatique** : MecaPy détecte les changements
5. **Migration opt-in** : l'utilisateur choisit quand upgrader

**Avantages** :
- ✅ L'utilisateur ne voit que les changements de SA fonction
- ✅ Immutabilité garantie via Function ID
- ✅ Pas de surprises lors des déploiements
- ✅ Migration contrôlée et progressive
- ✅ Versioning automatique (pas de maintenance manuelle)

**Ça résout ton problème ?** 🎯
