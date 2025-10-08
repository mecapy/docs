# 📦 Packages Multi-Fonctions MecaPy

## 🎯 Concept : Import Path Flexible

**Principe** : Le manifeste référence des fonctions par leur chemin d'import Python, permettant n'importe quelle structure de code.

### Format : `module.path:callable`

```yaml
functions:
  calcul_contrainte: "boulonnerie.vis:calcul_contrainte_traction"
  calcul_cisaillement: "boulonnerie.vis:calcul_cisaillement"
  check_assemblage: "boulonnerie.assemblage.Assemblage:verifier"
```

## 📋 Format Manifeste (mecapy.package.yaml)

```yaml
version: "1.0"
kind: "package"

package:
  name: "mecapy-boulonnerie"
  description: "Calculs pour assemblages boulonnés"
  author: "Votre Nom"
  version: "1.2.0"

# Configuration par défaut pour toutes les fonctions
defaults:
  runtime:
    python_version: "3.12"
    timeout: 300
    memory_limit: 2048

  dependencies:
    requirements: "requirements.txt"

# Liste des fonctions avec import paths
functions:
  # Fonction simple
  calcul-contrainte-traction:
    handler: "boulonnerie.calculs:contrainte_traction"
    description: "Calcul contrainte de traction dans une vis"
    io:
      inputs_schema:
        type: object
        properties:
          force: {type: number, minimum: 0}
          diametre: {type: number, minimum: 0}
      outputs_schema:
        type: object
        properties:
          contrainte: {type: number}
          statut: {type: string}

  # Méthode de classe
  calcul-cisaillement:
    handler: "boulonnerie.calculs.Vis:calculer_cisaillement"
    description: "Calcul contrainte de cisaillement"
    io:
      inputs_schema:
        type: object
        properties:
          force: {type: number}
          diametre: {type: number}

  # Méthode statique
  verification-assemblage:
    handler: "boulonnerie.assemblage.Assemblage:verifier_statique"
    description: "Vérification complète assemblage"
    runtime:
      timeout: 600  # Override du timeout pour cette fonction

  # Callable (classe avec __call__)
  optimisation-diametre:
    handler: "boulonnerie.optimisation.OptimiseurDiametre"
    description: "Optimisation du diamètre de vis"
```

## 💡 Exemples de Structures de Code

### Exemple 1 : Code Orienté Objet Existant

**Structure du projet** :
```
mecapy-boulonnerie/
├── mecapy.package.yaml
├── requirements.txt
├── boulonnerie/
│   ├── __init__.py
│   ├── vis.py              # Classes Vis, BoulonHR, etc.
│   ├── materiau.py         # Classes Materiau, Acier, Inox
│   ├── assemblage.py       # Classe Assemblage
│   └── calculs/
│       ├── __init__.py
│       ├── traction.py
│       └── cisaillement.py
└── tests/
```

**boulonnerie/vis.py** (code existant inchangé) :
```python
from dataclasses import dataclass
from typing import Dict, Any
from .materiau import Materiau, ACIER_S235

@dataclass
class Vis:
    """Classe représentant une vis."""
    diametre: float
    materiau: Materiau = ACIER_S235

    @property
    def section_resistante(self) -> float:
        """Calcul de la section résistante."""
        return 0.785 * (self.diametre ** 2) * 0.8

    def calculer_contrainte_traction(self, force: float) -> Dict[str, Any]:
        """
        Calcule la contrainte de traction.

        Cette méthode peut être directement exposée comme fonction MecaPy.
        """
        contrainte = force / self.section_resistante
        coef_securite = self.materiau.limite_elastique / contrainte

        if coef_securite >= 1.5:
            statut = "OK"
        elif coef_securite >= 1.0:
            statut = "LIMITE"
        else:
            statut = "RUPTURE"

        return {
            "contrainte": round(contrainte, 2),
            "coefficient_securite": round(coef_securite, 2),
            "statut": statut,
            "section_resistante": round(self.section_resistante, 2)
        }

    @classmethod
    def depuis_norme(cls, designation: str) -> "Vis":
        """Factory method depuis désignation normalisée."""
        # M12, M16, etc.
        diametre = float(designation[1:])
        return cls(diametre=diametre)


class BoulonHauteResistance(Vis):
    """Boulon haute résistance selon EN 14399."""

    def calculer_precharge(self) -> float:
        """Calcul de la précharge de serrage."""
        return 0.7 * self.materiau.limite_elastique * self.section_resistante
```

**mecapy.package.yaml** (manifeste flexible) :
```yaml
version: "1.0"
kind: "package"

package:
  name: "mecapy-boulonnerie"
  version: "1.0.0"

defaults:
  runtime:
    python_version: "3.12"

functions:
  # Méthode d'instance - MecaPy instancie automatiquement
  calcul-contrainte-vis:
    handler: "boulonnerie.vis.Vis:calculer_contrainte_traction"
    description: "Calcul contrainte traction dans une vis"
    # MecaPy détecte automatiquement les paramètres du constructeur
    constructor_params:
      diametre: "{inputs.diametre}"
      materiau: "{inputs.materiau}"  # Optionnel
    io:
      inputs_schema:
        type: object
        properties:
          force: {type: number}
          diametre: {type: number}
          materiau: {type: string, default: "S235"}

  # Méthode de classe
  vis-depuis-norme:
    handler: "boulonnerie.vis.Vis:depuis_norme"
    description: "Créer vis depuis désignation"

  # Sous-classe
  calcul-precharge-hr:
    handler: "boulonnerie.vis.BoulonHauteResistance:calculer_precharge"
    description: "Calcul précharge boulon HR"
```

### Exemple 2 : Code Fonctionnel (Actuel)

**Structure simple** :
```
mecapy-boulonnerie/
├── mecapy.package.yaml
├── requirements.txt
├── boulonnerie/
│   ├── __init__.py
│   └── calculs.py
└── tests/
```

**boulonnerie/calculs.py** :
```python
from typing import Dict, Any

def contrainte_traction(force: float, diametre: float,
                       materiau: str = "S235") -> Dict[str, Any]:
    """Fonction simple - style actuel."""
    section = 0.785 * (diametre ** 2) * 0.8
    contrainte = force / section
    # ... calculs ...
    return {"contrainte": contrainte, "statut": "OK"}


def cisaillement(force: float, diametre: float,
                nb_plans: int = 1) -> Dict[str, Any]:
    """Autre fonction simple."""
    section = 0.785 * (diametre ** 2)
    tau = force / (section * nb_plans)
    return {"cisaillement": tau}
```

**mecapy.package.yaml** :
```yaml
functions:
  contrainte-traction:
    handler: "boulonnerie.calculs:contrainte_traction"

  cisaillement:
    handler: "boulonnerie.calculs:cisaillement"
```

### Exemple 3 : Callable (Classe avec __call__)

**boulonnerie/optimisation.py** :
```python
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class OptimiseurDiametre:
    """Optimiseur comme callable - utile pour garder un état."""

    diametres_normalises: List[float] = None
    coefficient_securite_min: float = 1.5

    def __post_init__(self):
        if self.diametres_normalises is None:
            self.diametres_normalises = [6, 8, 10, 12, 14, 16, 20, 24, 30]

    def __call__(self, force: float, materiau: str = "S235") -> Dict[str, Any]:
        """
        Trouve le diamètre optimal pour une force donnée.

        La classe entière est callable - MecaPy l'instancie et l'appelle.
        """
        from .vis import Vis
        from .materiau import get_materiau

        mat = get_materiau(materiau)

        for d in self.diametres_normalises:
            vis = Vis(diametre=d, materiau=mat)
            result = vis.calculer_contrainte_traction(force)

            if result["coefficient_securite"] >= self.coefficient_securite_min:
                return {
                    "diametre_optimal": d,
                    "contrainte": result["contrainte"],
                    "coefficient_securite": result["coefficient_securite"]
                }

        return {"diametre_optimal": None, "erreur": "Aucun diamètre suffisant"}
```

**mecapy.package.yaml** :
```yaml
functions:
  optimisation-diametre:
    handler: "boulonnerie.optimisation.OptimiseurDiametre"
    description: "Trouve diamètre optimal"
    # Paramètres du constructeur (optionnels)
    constructor_params:
      coefficient_securite_min: 1.8  # Override de la valeur par défaut
```

### Exemple 4 : Workflow avec Dépendances

**boulonnerie/workflows.py** :
```python
from typing import Dict, Any
from .vis import Vis
from .assemblage import Assemblage

class WorkflowAssemblage:
    """Workflow complexe pour analyse complète assemblage."""

    def __init__(self):
        self.historique = []

    def analyser_complet(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse complète d'un assemblage.

        Args:
            config: Configuration assemblage avec liste de vis

        Returns:
            Résultat complet avec toutes les vérifications
        """
        resultats = {
            "vis": [],
            "assemblage_ok": True,
            "recommandations": []
        }

        # Analyse de chaque vis
        for vis_config in config["vis"]:
            vis = Vis(
                diametre=vis_config["diametre"],
                materiau=vis_config.get("materiau", "S235")
            )

            res_traction = vis.calculer_contrainte_traction(vis_config["force"])

            resultats["vis"].append({
                "nom": vis_config["nom"],
                "resultats": res_traction
            })

            if res_traction["statut"] != "OK":
                resultats["assemblage_ok"] = False
                resultats["recommandations"].append(
                    f"Augmenter diamètre de {vis_config['nom']}"
                )

        return resultats
```

**mecapy.package.yaml** :
```yaml
functions:
  analyse-assemblage-complet:
    handler: "boulonnerie.workflows.WorkflowAssemblage:analyser_complet"
    description: "Analyse complète assemblage multi-vis"
    runtime:
      timeout: 600  # Plus long pour workflow complexe
      memory_limit: 4096
```

## 🔧 Syntaxe Import Path

### Format Standard : `module.path:callable`

| Syntaxe | Description | Exemple |
|---------|-------------|---------|
| `module:function` | Fonction simple | `calculs:contrainte` |
| `module.Class:method` | Méthode d'instance | `vis.Vis:calculer_contrainte` |
| `module.Class:classmethod` | Méthode de classe | `vis.Vis:depuis_norme` |
| `module.Class:staticmethod` | Méthode statique | `utils.Math:arrondir` |
| `module.Class` | Callable (\_\_call\_\_) | `optimisation.Optimiseur` |
| `module.submodule:func` | Sous-module | `calculs.avances:nonlineaire` |

### Gestion Automatique par MecaPy

1. **Fonction simple** : Appel direct
   ```python
   # handler: "calculs:contrainte"
   result = calculs.contrainte(inputs["force"], inputs["diametre"])
   ```

2. **Méthode d'instance** : Instanciation automatique
   ```python
   # handler: "vis.Vis:calculer_contrainte"
   # MecaPy extrait les paramètres du __init__ depuis inputs
   obj = vis.Vis(diametre=inputs["diametre"])
   result = obj.calculer_contrainte(inputs["force"])
   ```

3. **Méthode de classe** : Appel direct
   ```python
   # handler: "vis.Vis:depuis_norme"
   result = vis.Vis.depuis_norme(inputs["designation"])
   ```

4. **Callable** : Instanciation puis appel
   ```python
   # handler: "optimisation.Optimiseur"
   optimiseur = optimisation.Optimiseur()
   result = optimiseur(inputs)
   ```

## 🎯 Avantages de cette Approche

### ✅ Pour l'Utilisateur

1. **Code inchangé** : Pas de refactoring nécessaire
2. **POO respecté** : Classes, héritage, tout fonctionne
3. **Flexible** : N'importe quelle structure de projet
4. **Patterns familiers** : Comme FastAPI, Celery, Click

### ✅ Pour le Développement

1. **Découplage** : Code métier ≠ code MecaPy
2. **Testable** : Tests unitaires normaux Python
3. **Évolutif** : Ajout de fonctions sans changer le code
4. **Versionning** : Tout le package versionné ensemble

### ✅ Exemples Concrets

**FastAPI** (même principe) :
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    # FastAPI trouve la fonction par path
    pass
```

**Celery** :
```python
# celeryconfig.py
task_routes = {
    'myapp.tasks.add': {'queue': 'math'},
}
# Référence par import path !
```

**AWS SAM / Serverless.yml** :
```yaml
functions:
  hello:
    handler: src/handlers.hello  # module.path:function
```

## 🚀 Migration du Code Existant

### Avant (fonction isolée)
```
boulonnerie/
└── handler.py  # Une seule fonction
```

### Après (package flexible)
```
boulonnerie/
├── mecapy.package.yaml
├── vis.py           # Vos classes existantes
├── materiau.py      # Vos classes existantes
└── handlers.py      # Nouvelles fonctions wrapper (optionnel)
```

**Pas besoin de wrapper si POO** :
```yaml
# mecapy.package.yaml
functions:
  contrainte:
    handler: "vis.Vis:calculer_contrainte"  # Directement la méthode
```

**Avec wrapper si nécessaire** :
```python
# handlers.py (optionnel)
from .vis import Vis

def contrainte_wrapper(force, diametre, materiau="S235"):
    """Wrapper simple si besoin d'adapter l'interface."""
    vis = Vis(diametre=diametre, materiau=materiau)
    return vis.calculer_contrainte(force)
```

## 🔍 Détection Automatique

MecaPy inspecte le callable pour détecter :

1. **Type** : fonction, méthode, classe, callable
2. **Signature** : paramètres, types hints, defaults
3. **Constructor params** : si méthode d'instance
4. **Docstring** : pour documentation auto

```python
import inspect

# MecaPy fait automatiquement :
sig = inspect.signature(callable_obj)
params = sig.parameters
# → Génère inputs_schema automatiquement !
```

## 📝 Rétrocompatibilité

Les fonctions standalone actuelles continuent de fonctionner :

```yaml
# Ancien format (toujours supporté)
POST /functions/from-git
{
  "git_url": "...",
  "handler": "handler.py"  # Cherche handler() dans handler.py
}

# Nouveau format (package)
POST /packages/from-git
{
  "git_url": "...",
  # Lit mecapy.package.yaml automatiquement
}
```

---

**Cette approche est beaucoup plus flexible et respecte le code existant !** 🎯
