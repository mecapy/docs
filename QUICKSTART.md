# 🚀 MecaPy Manifest - Guide de démarrage rapide

## Format minimal (90% des cas)

Créez un fichier `mecapy.yml` à la racine de votre projet :

```yaml
name: mon-package
description: Description de mon package

functions:
  ma-fonction:
    handler: module:function
```

**C'est tout !** Les schemas sont auto-générés depuis vos type hints Python.

---

## Exemples pratiques

### Fonction simple

```yaml
# mecapy.yml
name: calculateur-simple

functions:
  addition:
    handler: calc:add
```

```python
# calc.py
def add(x: float, y: float) -> float:
    """Additionne deux nombres."""
    return x + y
```

### Méthode de classe

```yaml
functions:
  calcul-contrainte:
    handler: vis.Vis:calculer_contrainte
    init: [diametre, materiau]  # Paramètres du constructeur
```

```python
# vis.py
class Vis:
    def __init__(self, diametre: float, materiau: str):
        self.diametre = diametre
        self.materiau = materiau

    def calculer_contrainte(self, force: float) -> dict:
        """Calcule la contrainte."""
        return {"contrainte": force / self.diametre}
```

### Classmethod

```yaml
functions:
  creation-vis:
    handler: vis.Vis:depuis_designation  # Pas de init requis
```

```python
class Vis:
    @classmethod
    def depuis_designation(cls, designation: str) -> "Vis":
        """Crée une vis depuis sa désignation (M8, M12, etc.)."""
        ...
```

---

## Type hints pour l'auto-introspection

### Types de base

```python
from typing import Annotated
from pydantic import Field

def calcul(
    force: Annotated[float, Field(
        description="Force en Newton",
        ge=0,
        le=500000
    )],
    diametre: Annotated[float, Field(
        description="Diamètre en mm",
        ge=3,
        le=100
    )]
) -> float:
    """Calcule quelque chose."""
    return force / diametre
```

→ Génère automatiquement un schema JSON avec validation !

### Types de retour structurés

```python
from typing import TypedDict, Literal

class Resultat(TypedDict):
    contrainte: float
    statut: Literal["OK", "LIMITE", "RUPTURE"]

def calculer(force: float) -> Resultat:
    """Calcule et retourne un résultat structuré."""
    return {"contrainte": 150.5, "statut": "OK"}
```

→ Schema de sortie auto-généré !

---

## Overrides explicites (10% des cas)

Si vous avez besoin de validation custom :

```yaml
functions:
  fonction-complexe:
    handler: module:advanced
    # Override du schema d'entrée
    inputs_schema:
      type: object
      properties:
        code:
          type: string
          pattern: "^[A-Z]{3}-[0-9]{4}$"
      required: [code]
    # Output schema reste auto-généré
```

---

## Configuration optionnelle

```yaml
name: mon-package
description: Description

# Runtime (optionnel, defaults intelligents)
runtime:
  python: "3.12"
  timeout: 300

# Tests (auto-détectés dans tests/)
tests:
  framework: pytest
  min_coverage: 80

functions:
  ma-fonction:
    handler: module:function
```

---

## Checklist rapide

✅ Fichier `mecapy.yml` à la racine du projet
✅ Type hints sur toutes les fonctions
✅ Docstrings avec description
✅ Tests dans le dossier `tests/`
✅ `requirements.txt` ou `pyproject.toml`

**C'est parti !** 🚀

---

## Documentation complète

Pour plus de détails : [MANIFEST_FORMAT.md](./packages/MANIFEST_FORMAT.md)
