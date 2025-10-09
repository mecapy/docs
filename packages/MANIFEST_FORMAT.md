# 📋 MecaPy Manifest Format Specification

## Vue d'ensemble

Le manifest MecaPy définit la configuration d'un package multi-fonctions.

**Format unique** : `mecapy.yml`

Ce format hybride est **simple par défaut** avec introspection automatique, tout en permettant des **overrides explicites** quand nécessaire.

---

## 🚀 Format mecapy.yml

### Structure de base

```yaml
name: package-name
description: Package description
author: Author Name
license: MIT
tags:
  - tag1
  - tag2

functions:
  function-name:
    handler: module.Class:method
    description: Function description
    init: [param1, param2]
```

### Exemple complet (simple - 90% des cas)

```yaml
# mecapy.yml - Simple avec auto-introspection
name: mecapy-example
description: Suite complète de calculs mécaniques
author: MecaPy Team
license: MIT
tags:
  - mécanique
  - assemblage
  - eurocode

# Fonctions exposées
functions:
  calcul-contrainte-traction:
    handler: example.vis.Vis:calculer_contrainte_traction
    description: Calcul de contrainte de traction dans une vis selon RDM
    init: [diametre, materiau]
    # Schemas auto-générés ✅

  calcul-cisaillement:
    handler: example.vis.Vis:calculer_cisaillement
    description: Calcul de contrainte de cisaillement
    init: [diametre, materiau]
    # Schemas auto-générés ✅

  creation-vis-designation:
    handler: example.vis.Vis:depuis_designation
    description: Crée une vis depuis désignation (M12, M16, etc.)
    # Schemas auto-générés ✅

# Configuration optionnelle (valeurs par défaut intelligentes sinon)
runtime:
  python: "3.12"
  timeout: 300
  memory: 2048

# Tests auto-détectés dans tests/
tests:
  framework: pytest
  min_coverage: 80
```

### Exemple avec overrides (10% des cas)

```yaml
# mecapy.yml - Avec overrides explicites quand nécessaire
name: mecapy-advanced
description: Package avec schemas personnalisés

functions:
  # Fonction simple (auto-introspection)
  simple-function:
    handler: module:function
    # Schemas auto-générés ✅

  # Fonction avec schema custom (override)
  complex-function:
    handler: module:advanced
    description: Fonction avec validation complexe
    # Override explicite du schema d'entrée
    inputs_schema:
      type: object
      properties:
        pattern_field:
          type: string
          pattern: "^[A-Z]{3}-[0-9]{4}$"
        custom_validation:
          type: array
          items:
            type: object
            properties:
              key: {type: string}
              value: {type: number}
      required: [pattern_field]
    # Output schema auto-généré ✅
```

---

## 📖 Spécification des champs

### Champs obligatoires

| Champ | Type | Description |
|-------|------|-------------|
| `name` | string | Nom unique du package (kebab-case) |
| `functions` | object | Dictionnaire des fonctions exposées |

### Champs optionnels (package)

| Champ | Type | Défaut | Description |
|-------|------|--------|-------------|
| `description` | string | - | Description du package |
| `author` | string | - | Auteur du package |
| `license` | string | MIT | Licence (MIT, Apache-2.0, etc.) |
| `tags` | array | [] | Tags pour catégorisation |
| `runtime` | object | (voir ci-dessous) | Configuration runtime par défaut |
| `tests` | object | auto | Configuration des tests |

### Champs fonction

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `handler` | string | ✅ | Import path (module:function ou Class:method) |
| `description` | string | ❌ | Description de la fonction |
| `init` | list\|object | ❌ | Paramètres constructeur (pour méthodes de classe) |
| `runtime` | object | ❌ | Override runtime pour cette fonction |
| `examples` | array | ❌ | Exemples d'utilisation (optionnel) |

---

## 🎯 Handler Formats

Le champ `handler` supporte plusieurs formats :

### 1. Fonction simple

```yaml
handler: module.submodule:function_name
```

Exemple :
```python
# example/utils.py
def calculate(x: float, y: float) -> float:
    return x + y
```

```yaml
handler: example.utils:calculate
```

### 2. Méthode d'instance

```yaml
handler: module.Class:method_name
init: [param1, param2]
```

Exemple :
```python
# example/vis.py
class Vis:
    def __init__(self, diametre: float, materiau: str):
        self.diametre = diametre
        self.materiau = materiau

    def calculer_contrainte(self, force: float) -> dict:
        ...
```

```yaml
handler: example.vis.Vis:calculer_contrainte
init: [diametre, materiau]  # Passés au constructeur
```

### 3. Méthode de classe (@classmethod)

```yaml
handler: module.Class:class_method_name
```

Exemple :
```python
# example/vis.py
class Vis:
    @classmethod
    def depuis_designation(cls, designation: str) -> "Vis":
        ...
```

```yaml
handler: example.vis.Vis:depuis_designation
# Pas de init requis (class method)
```

### 4. Classe callable

```yaml
handler: module.Class
```

Exemple :
```python
# example/calculator.py
class Calculator:
    def __call__(self, x: float, y: float) -> float:
        return x + y
```

```yaml
handler: example.calculator.Calculator
```

---

## 🔧 Configuration Runtime

### Defaults globaux

```yaml
runtime:
  python: "3.12"       # Version Python (3.11, 3.12)
  timeout: 300         # Timeout en secondes
  memory: 2048         # Mémoire en MB
```

### Override par fonction

```yaml
functions:
  heavy-computation:
    handler: example:compute
    runtime:
      timeout: 600     # Override: 10 minutes
      memory: 4096     # Override: 4 GB
```

---

## 🧪 Configuration Tests

### Auto-détection

```yaml
tests:
  framework: pytest           # pytest (défaut)
  min_coverage: 80           # Couverture minimale (%)
```

MecaPy détecte automatiquement :
- Tests dans `tests/` directory
- Requirements dans `requirements.txt` ou `pyproject.toml`

### Configuration avancée

```yaml
tests:
  framework: pytest
  min_coverage: 90
  command: "pytest tests/ -v --cov=example"
  include:
    - "tests/test_*.py"
  exclude:
    - "tests/test_integration.py"
```

---

## 📊 Introspection Automatique

Le format minimal génère automatiquement :

### 1. Input Schemas

Depuis les **type hints** et **Pydantic Field** :

```python
from typing import Annotated
from pydantic import Field

def calcul(
    force: Annotated[float, Field(
        description="Force en N",
        ge=0,
        le=500000
    )],
    diametre: Annotated[float, Field(
        description="Diamètre en mm",
        ge=3,
        le=100,
        examples=[6, 8, 10, 12]
    )]
) -> dict:
    ...
```

→ Génère automatiquement :

```json
{
  "type": "object",
  "properties": {
    "force": {
      "type": "number",
      "description": "Force en N",
      "minimum": 0,
      "maximum": 500000
    },
    "diametre": {
      "type": "number",
      "description": "Diamètre en mm",
      "minimum": 3,
      "maximum": 100,
      "examples": [6, 8, 10, 12]
    }
  },
  "required": ["force", "diametre"]
}
```

### 2. Output Schemas

Depuis les **TypedDict** :

```python
from typing import TypedDict, Literal

class ResultatCalcul(TypedDict):
    contrainte: float           # Contrainte (MPa)
    statut: Literal["OK", "LIMITE", "RUPTURE"]
    coefficient_securite: float

def calcul(force: float) -> ResultatCalcul:
    ...
```

→ Génère automatiquement le schema de sortie

### 3. Descriptions

Depuis les **docstrings NumPy** :

```python
def calcul(force: float, diametre: float) -> dict:
    """
    Calcule la contrainte de traction.

    Parameters
    ----------
    force : float
        Force de traction appliquée en Newton
    diametre : float
        Diamètre nominal de la vis en millimètres

    Returns
    -------
    dict
        Résultats avec contrainte et statut
    """
    ...
```

→ Descriptions extraites automatiquement

---

## 📐 Standard Parameter Types

### Principle

**MecaPy uses a restricted set of well-defined types** to ensure:
- Clear and consistent documentation
- Robust API-side validation
- Predictable user interface
- Full JSON Schema compatibility

### Supported Types

| Python Type | JSON Schema | Description | Pydantic Validation |
|------------|-------------|-------------|---------------------|
| `int` | `integer` | Integer number | `int` |
| `int` (≥0) | `integer` | Non-negative integer | `Annotated[int, Field(ge=0)]` |
| `float` | `number` | Decimal number | `float` |
| `float` (≥0) | `number` | Non-negative float | `Annotated[float, Field(ge=0)]` |
| `str` | `string` | Text string | `str` |
| `Literal[...]` | `string` (enum) | Fixed choice list | `Literal["choice1", "choice2"]` |
| `list[T]` | `array` | Array of values | `list[int]`, `list[float]`, etc. |

### Examples by Type

#### 1. Integer

```python
from typing import Annotated
from pydantic import Field

def calculate(
    nb_iterations: Annotated[int, Field(
        description="Number of iterations",
        ge=1,           # Minimum: 1
        le=1000,        # Maximum: 1000
        examples=[10, 50, 100]
    )]
) -> dict:
    ...
```

→ Generated JSON Schema:
```json
{
  "nb_iterations": {
    "type": "integer",
    "description": "Number of iterations",
    "minimum": 1,
    "maximum": 1000,
    "examples": [10, 50, 100]
  }
}
```

#### 2. Non-negative Integer (≥ 0)

```python
def calculate(
    quantity: Annotated[int, Field(
        description="Number of parts",
        ge=0,
        examples=[0, 5, 10]
    )]
) -> dict:
    ...
```

→ JSON Schema:
```json
{
  "quantity": {
    "type": "integer",
    "description": "Number of parts",
    "minimum": 0,
    "examples": [0, 5, 10]
  }
}
```

#### 3. Float (number)

```python
def calculate(
    force: Annotated[float, Field(
        description="Applied force in Newton",
        ge=0,
        le=500000,
        examples=[1000, 5000, 10000]
    )]
) -> dict:
    ...
```

→ JSON Schema:
```json
{
  "force": {
    "type": "number",
    "description": "Applied force in Newton",
    "minimum": 0,
    "maximum": 500000,
    "examples": [1000, 5000, 10000]
  }
}
```

#### 4. Non-negative Float (≥ 0)

```python
def calculate(
    diameter: Annotated[float, Field(
        description="Diameter in mm",
        ge=0,
        le=1000,
        examples=[6, 8, 10, 12]
    )]
) -> dict:
    ...
```

→ JSON Schema:
```json
{
  "diameter": {
    "type": "number",
    "description": "Diameter in mm",
    "minimum": 0,
    "maximum": 1000,
    "examples": [6, 8, 10, 12]
  }
}
```

#### 5. String

```python
def calculate(
    designation: Annotated[str, Field(
        description="Part designation",
        min_length=1,
        max_length=100,
        examples=["M12", "M16", "HEA200"]
    )]
) -> dict:
    ...
```

→ JSON Schema:
```json
{
  "designation": {
    "type": "string",
    "description": "Part designation",
    "minLength": 1,
    "maxLength": 100,
    "examples": ["M12", "M16", "HEA200"]
  }
}
```

#### 6. Enum (Fixed Choices)

```python
from typing import Literal

def calculate(
    material: Annotated[Literal["S235", "S355", "S460"], Field(
        description="Steel grade according to EN 10025"
    )],
    assembly_type: Literal["preloaded", "non-preloaded"] = "preloaded"
) -> dict:
    ...
```

→ JSON Schema:
```json
{
  "material": {
    "type": "string",
    "description": "Steel grade according to EN 10025",
    "enum": ["S235", "S355", "S460"]
  },
  "assembly_type": {
    "type": "string",
    "enum": ["preloaded", "non-preloaded"],
    "default": "preloaded"
  }
}
```

#### 7. Array

```python
def calculate(
    forces: Annotated[list[float], Field(
        description="List of forces in Newton",
        min_length=1,
        max_length=10
    )],
    coefficients: list[float] = [1.0, 1.5, 2.0]
) -> dict:
    ...
```

→ JSON Schema:
```json
{
  "forces": {
    "type": "array",
    "description": "List of forces in Newton",
    "items": {"type": "number"},
    "minItems": 1,
    "maxItems": 10
  },
  "coefficients": {
    "type": "array",
    "items": {"type": "number"},
    "default": [1.0, 1.5, 2.0]
  }
}
```

### Validation Constraints

#### Numeric Constraints

```python
# Boundary constraints
ge=0     # Greater or Equal    → minimum: 0
le=100   # Less or Equal       → maximum: 100
gt=0     # Greater Than        → exclusiveMinimum: 0
lt=100   # Less Than           → exclusiveMaximum: 100
```

**Complete example**:
```python
def calculate(
    temperature: Annotated[float, Field(
        description="Temperature in °C",
        ge=-273.15,  # Absolute zero
        le=1000,     # Practical max
        examples=[20, 100, 500]
    )]
) -> dict:
    ...
```

#### String Constraints

```python
# Length
min_length=1      # Minimum 1 character
max_length=100    # Maximum 100 characters

# Regex pattern (avoid if possible, prefer Literal)
pattern="^[A-Z]{1,3}[0-9]{1,4}$"  # Ex: M12, HEA200
```

#### Array Constraints

```python
# Size
min_length=1      # Minimum 1 element    → minItems: 1
max_length=100    # Maximum 100 elements → maxItems: 100
```

### Best Practices

#### ✅ GOOD: Simple and explicit types

```python
from typing import Annotated, Literal
from pydantic import Field

def calculate_assembly(
    diameter: Annotated[float, Field(
        description="Nominal diameter in mm",
        ge=6,
        le=100,
        examples=[8, 10, 12, 16, 20]
    )],
    grade: Literal["4.6", "5.6", "8.8", "10.9"],
    nb_bolts: Annotated[int, Field(ge=1, le=100)],
    forces: list[float]
) -> dict:
    """Bolted assembly calculation."""
    ...
```

#### ❌ AVOID: Complex types

```python
# ❌ No complex nested types
def calculate(
    config: dict[str, list[tuple[int, float]]]  # Too complex
) -> dict:
    ...

# ✅ Prefer simple types
def calculate(
    forces: list[float],
    coefficients: list[float]
) -> dict:
    ...
```

#### ❌ AVOID: Regex validation if Literal is possible

```python
# ❌ Regex pattern for fixed choices
material: Annotated[str, Field(
    pattern="^(S235|S355|S460)$"
)]

# ✅ Literal for fixed choices
material: Literal["S235", "S355", "S460"]
```

### Validation Checklist

Before publishing a package, verify:

- [ ] All parameters use standard types (int, float, str, Literal, list)
- [ ] Numeric constraints are coherent (ge < le)
- [ ] Descriptions are clear
- [ ] Examples cover typical use cases
- [ ] Default values are sensible
- [ ] No complex types (nested dict, tuple, etc.)
- [ ] Literal is preferred over regex patterns

---

## 🔄 Versioning Automatique

### Principe

Chaque fonction est versionnée automatiquement via **checksum du code source** :

```
version = {MAJOR}.{MINOR}.{CHECKSUM}

Exemple : 1.0.0-a3f2b8c1d4e5
```

### Calcul du checksum

```python
checksum = sha256(
    function_source_code +
    dependencies_code +
    function_signature
).hexdigest()[:12]
```

### Comportement

- Modification du code → nouveau checksum → nouvelle version
- Function ID reste immutable → utilisateurs existants non impactés
- Migration opt-in vers nouvelle version

---

## 📝 Init Params (Paramètres Constructeur)

### Format simple (liste)

```yaml
init: [diametre, materiau]
```

→ Équivalent à :
```yaml
init:
  diametre: "{inputs.diametre}"
  materiau: "{inputs.materiau}"
```

### Format avancé (mapping)

```yaml
init:
  diametre: "{inputs.diametre}"
  materiau: "get_materiau({inputs.materiau})"
  longueur: 100  # Valeur fixe
```

Supporte :
- `{inputs.key}` : Valeur depuis les inputs
- `function({inputs.key})` : Appel de fonction
- Valeurs littérales (str, int, float)

---

## ✅ Bonnes pratiques

### 1. Nommage

```yaml
# ✅ BON : kebab-case pour package et fonctions
name: mecapy-example
functions:
  calcul-contrainte-traction:
    ...

# ❌ ÉVITER : snake_case ou camelCase
name: mecapy_example
functions:
  calculateContrainte:
    ...
```

### 2. Type hints complets

```python
# ✅ BON : types explicites avec contraintes
def calcul(
    force: Annotated[float, Field(ge=0, le=500000)]
) -> ResultatDict:
    ...

# ❌ ÉVITER : pas de types
def calcul(force):
    ...
```

### 3. Docstrings NumPy

```python
# ✅ BON : NumPy docstring avec sections
def calcul(force: float) -> dict:
    """
    Calcule la contrainte.

    Parameters
    ----------
    force : float
        Force appliquée en N

    Returns
    -------
    dict
        Résultats du calcul
    """
    ...
```

### 4. TypedDict pour retours

```python
# ✅ BON : TypedDict structuré
class Resultat(TypedDict):
    contrainte: float
    statut: Literal["OK", "LIMITE", "RUPTURE"]

def calcul() -> Resultat:
    ...

# ⚠️ MOYEN : dict générique
def calcul() -> dict:
    ...
```

---

## 🔍 Validation du Manifest

### Commande CLI (future)

```bash
mecapy validate mecapy.yml
```

### Checklist manuelle

- [ ] `name` est unique et en kebab-case
- [ ] Tous les `handler` sont valides (module:function)
- [ ] Les `init` params correspondent aux constructeurs
- [ ] Type hints présents sur toutes les fonctions
- [ ] Docstrings NumPy sur toutes les fonctions
- [ ] Tests présents dans `tests/`
- [ ] `requirements.txt` ou `pyproject.toml` à jour

---

## 📚 Exemples complets

### Package simple (1 fonction)

```yaml
name: simple-calc
description: Calculateur simple

functions:
  add:
    handler: calculator:add
    description: Addition de deux nombres
```

### Package POO (4 fonctions)

```yaml
name: mecapy-vis
description: Calculs d'assemblages boulonnés

functions:
  contrainte-traction:
    handler: vis.Vis:calculer_contrainte_traction
    init: [diametre, materiau]

  cisaillement:
    handler: vis.Vis:calculer_cisaillement
    init: [diametre, materiau]

  creation-vis:
    handler: vis.Vis:depuis_designation

  precharge-hr:
    handler: vis.BoulonHR:calculer_precharge
    init: [diametre, materiau, classe]
```

### Package avec overrides

```yaml
name: advanced-package

functions:
  light-task:
    handler: tasks:light
    runtime:
      timeout: 60
      memory: 512

  heavy-task:
    handler: tasks:heavy
    runtime:
      timeout: 900
      memory: 8192

runtime:
  python: "3.12"
  timeout: 300
  memory: 2048
```

---

## 🚨 Limitations et Workarounds

### Limitation 1 : Introspection requiert type hints

**Problème** : Code sans type hints → schemas génériques

**Solution** :
```python
# ✅ Ajouter type hints
def calcul(force: float, diametre: float) -> dict:
    ...
```

### Limitation 2 : Imports dynamiques non supportés

**Problème** : `importlib.import_module()` → introspection échoue

**Solution** : Utiliser imports statiques

### Limitation 3 : Transformations complexes dans init

**Problème** : `init: [diametre]` ne peut pas transformer la valeur

**Solution** : Format avancé avec mapping
```yaml
init:
  diametre: "{inputs.diametre_mm}"
  materiau: "get_materiau({inputs.code_materiau})"
```

---

## 📖 Références

- [MANIFEST_INTROSPECTION.md](./MANIFEST_INTROSPECTION.md) - Règles d'introspection détaillées
- [MIGRATION_IMPACT.md](./MIGRATION_IMPACT.md) - Impact de la migration
- [Pydantic Field Documentation](https://docs.pydantic.dev/latest/concepts/fields/)
- [NumPy Docstring Standard](https://numpydoc.readthedocs.io/en/latest/format.html)

---

**Le format minimal `mecapy.yml` simplifie radicalement la configuration tout en conservant toute la puissance de MecaPy !** 🚀
