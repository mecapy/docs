# 📦 FORMAT DE FONCTION MECAPY

## 🎯 Structure recommandée

### **Format : Archive ZIP avec structure standardisée**

```
function-calcul-contrainte.zip
├── mecapy.yaml              # Manifeste (metadata + config)
├── handler.py               # Point d'entrée OBLIGATOIRE
├── requirements.txt         # Dépendances Python (optionnel)
├── tests/                   # Tests unitaires (optionnel)
│   └── test_handler.py
├── data/                    # Données statiques (optionnel)
│   └── material_db.json
└── README.md                # Documentation (optionnel)
```

---

## 📄 1. MANIFESTE `mecapy.yaml`

**Fichier de configuration obligatoire** décrivant la fonction :

```yaml
# mecapy.yaml
version: "1.0"

metadata:
  name: "calcul-contrainte-vis"
  description: "Calcul de contrainte dans une vis selon Eurocode 3"
  author: "Jean Dupont"
  email: "jean@example.com"
  tags: ["mécanique", "eurocode", "assemblage"]
  category: "structures"

runtime:
  python_version: "3.12"          # 3.9, 3.10, 3.11, 3.12
  base_image: "python-scientific" # python-base, python-scientific, python-cfd
  timeout: 300                    # secondes (max 600)
  memory_limit: 2048              # MB (max 4096)
  cpu_limit: 2                    # cores (max 4)

dependencies:
  requirements: "requirements.txt"  # Fichier requirements.txt
  # OU inline:
  # packages:
  #   - "numpy==1.24.0"
  #   - "scipy==1.10.0"

io:
  # Schéma inputs (validation automatique)
  inputs_schema:
    type: object
    properties:
      force:
        type: number
        description: "Force appliquée (N)"
        minimum: 0
        maximum: 100000
      section:
        type: number
        description: "Section de la vis (mm²)"
        minimum: 1
    required: [force, section]

  # Schéma outputs (documentation)
  outputs_schema:
    type: object
    properties:
      contrainte:
        type: number
        description: "Contrainte calculée (MPa)"
      coefficient_securite:
        type: number
        description: "Coefficient de sécurité"
      statut:
        type: string
        enum: ["OK", "LIMITE", "RUPTURE"]

quality:
  # Tests de validation (exécutés lors du déploiement)
  test_cases:
    - inputs: {force: 1000, section: 10}
      expected_outputs: {contrainte: 100}
    - inputs: {force: 5000, section: 25}
      expected_outputs: {contrainte: 200}

versioning:
  version: "1.2.3"
  changelog: |
    v1.2.3: Fix coefficient sécurité
    v1.2.2: Ajout validation inputs
    v1.2.0: Support Eurocode 3 rev 2024
```

---

## 🐍 2. HANDLER `handler.py`

**Point d'entrée standardisé** avec fonction `calculate()` :

```python
# handler.py
"""
Calcul de contrainte dans une vis.
Conforme à Eurocode 3.
"""
import numpy as np
from typing import Dict, Any


def calculate(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Point d'entrée principal de la fonction MecaPy.

    Cette fonction DOIT s'appeler 'calculate' et accepter un dict en entrée.
    Elle DOIT retourner un dict en sortie.

    Parameters
    ----------
    inputs : dict
        Dictionnaire contenant les paramètres d'entrée.
        Structure définie dans mecapy.yaml > io.inputs_schema

    Returns
    -------
    dict
        Dictionnaire contenant les résultats.
        Structure définie dans mecapy.yaml > io.outputs_schema

    Examples
    --------
    >>> calculate({"force": 1000, "section": 10})
    {'contrainte': 100.0, 'coefficient_securite': 2.35, 'statut': 'OK'}
    """

    # 1. Extraction inputs (avec validation implicite par schema)
    force = inputs['force']  # N
    section = inputs['section']  # mm²

    # 2. Calcul
    contrainte = force / section  # MPa

    # Limites matériau (exemple acier S235)
    limite_elastique = 235  # MPa
    coefficient_securite = limite_elastique / contrainte

    # Statut
    if coefficient_securite > 1.5:
        statut = "OK"
    elif coefficient_securite > 1.0:
        statut = "LIMITE"
    else:
        statut = "RUPTURE"

    # 3. Retour outputs
    return {
        "contrainte": float(contrainte),
        "coefficient_securite": float(coefficient_securite),
        "statut": statut
    }


# Fonctions auxiliaires (optionnel)
def _compute_safety_factor(stress: float, material: str) -> float:
    """Calcul du coefficient de sécurité selon matériau."""
    limits = {
        'S235': 235,
        'S355': 355,
        'S460': 460
    }
    return limits.get(material, 235) / stress
```

---

## 📦 3. SÉRIALISATION I/O

### **Format : JSON uniquement**

**Pourquoi JSON** :
- ✅ Standard universel
- ✅ Human-readable
- ✅ Support types de base (number, string, boolean, array, object)
- ✅ Validation facile (JSON Schema)

### **Types supportés**

```python
# Types Python → JSON
inputs = {
    # Primitifs
    "force": 1000,              # number (int/float)
    "nom": "Vis M12",           # string
    "actif": True,              # boolean

    # Collections
    "valeurs": [1, 2, 3],       # array
    "parametres": {             # object
        "E": 210000,
        "nu": 0.3
    },

    # null
    "optionnel": None           # null
}
```

### **Types avancés (sérialisation custom)**

Pour NumPy arrays, DataFrames, etc. :

```python
# handler.py
import numpy as np
import json

def calculate(inputs: dict) -> dict:
    # Désérialiser array NumPy depuis JSON
    if "matrice" in inputs:
        matrice = np.array(inputs["matrice"])  # [[1,2],[3,4]] → np.ndarray

    # Calculs
    result_array = np.linalg.inv(matrice)

    # Sérialiser pour JSON
    return {
        "inverse": result_array.tolist(),  # np.ndarray → list
        "determinant": float(np.linalg.det(matrice))
    }
```

### **Fichiers binaires (gros fichiers)**

Pour meshes, images, etc. :

```python
# Approche: Références S3 dans inputs/outputs
def calculate(inputs: dict) -> dict:
    # Input = référence S3
    mesh_s3_key = inputs["mesh_file"]  # "meshes/model-123.msh"

    # Download depuis S3 (géré par worker)
    # mesh_data = download_from_s3(mesh_s3_key)

    # Calculs...

    # Output = upload vers S3, retourner clé
    result_s3_key = upload_to_s3(result_mesh, "results/mesh-456.msh")

    return {
        "result_mesh_file": result_s3_key,
        "volume": 123.45
    }
```

---

## 🧪 4. TESTS `tests/test_handler.py`

**Tests unitaires exécutés lors du déploiement** :

```python
# tests/test_handler.py
import pytest
from handler import calculate


def test_calculate_basic():
    """Test cas nominal."""
    result = calculate({
        "force": 1000,
        "section": 10
    })

    assert result["contrainte"] == 100.0
    assert result["statut"] == "OK"


def test_calculate_edge_cases():
    """Test cas limites."""
    # Force nulle
    result = calculate({"force": 0, "section": 10})
    assert result["contrainte"] == 0

    # Section minimale
    result = calculate({"force": 1000, "section": 1})
    assert result["contrainte"] == 1000


def test_calculate_invalid_inputs():
    """Test validation inputs."""
    with pytest.raises(KeyError):
        calculate({"force": 1000})  # Section manquante
```

---

## 📥 5. UPLOAD FONCTION (API)

### **Endpoint : `POST /functions`**

```http
POST /api/functions
Content-Type: multipart/form-data
Authorization: Bearer <token>

--boundary
Content-Disposition: form-data; name="archive"; filename="function.zip"
Content-Type: application/zip

[binary data]
--boundary--
```

**Traitement backend** :

```python
# api/routes/functions.py
@router.post("/functions")
async def create_function(
    archive: UploadFile,
    user: User = Depends(get_current_user)
):
    # 1. Valider ZIP
    validate_zip(archive)

    # 2. Extraire et parser mecapy.yaml
    manifest = extract_manifest(archive)

    # 3. Valider manifest (schema, version Python supportée, etc.)
    validate_manifest(manifest)

    # 4. Extraire handler.py
    handler_code = extract_file(archive, "handler.py")

    # 5. Valider code (blacklist imports)
    validate_code(handler_code)

    # 6. Build image Docker
    dockerfile = generate_dockerfile(manifest)
    image_tag = build_docker_image(dockerfile, archive, manifest)

    # 7. Push vers Container Registry
    push_to_registry(image_tag)

    # 8. Exécuter tests (si définis)
    if manifest.get("quality", {}).get("test_cases"):
        test_results = run_tests(image_tag, manifest["quality"]["test_cases"])
        if not test_results.success:
            raise ValidationError("Tests échoués", details=test_results)

    # 9. Sauvegarder metadata
    function = Function(
        user_id=user.id,
        name=manifest["metadata"]["name"],
        version=manifest["versioning"]["version"],
        docker_image=image_tag,
        manifest=manifest
    )
    db.add(function)

    return {
        "function_id": function.id,
        "status": "deployed",
        "docker_image": image_tag
    }
```

---

## 🔗 6. INTÉGRATION GIT (futur)

### **Workflow GitHub/GitLab**

```yaml
# .github/workflows/deploy-mecapy.yml
name: Deploy to MecaPy

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Create archive
        run: |
          zip -r function.zip \
            mecapy.yaml \
            handler.py \
            requirements.txt \
            tests/

      - name: Deploy to MecaPy
        run: |
          curl -X POST https://api.mecapy.com/functions \
            -H "Authorization: Bearer ${{ secrets.MECAPY_TOKEN }}" \
            -F "archive=@function.zip"
```

**OU via SDK Python** :

```python
# deploy.py
from mecapy import MecaPy

client = MecaPy(token="your-token")

# Déployer depuis repo Git
function = client.functions.deploy_from_git(
    repo_url="https://github.com/user/my-function",
    branch="main"
)

print(f"Deployed: {function.id}")
```

---

## 📊 FORMATS ALTERNATIFS (validation)

### **Option A : Python package (pyproject.toml)**

```toml
# pyproject.toml
[project]
name = "mecapy-calcul-contrainte"
version = "1.2.3"
description = "Calcul contrainte vis"
authors = [{name = "Jean Dupont", email = "jean@example.com"}]
dependencies = ["numpy>=1.24", "scipy>=1.10"]

[tool.mecapy]
runtime.python_version = "3.12"
runtime.timeout = 300
runtime.memory_limit = 2048
```

**Inconvénient** : Moins lisible que YAML pour non-développeurs

---

### **Option B : Dockerfile custom**

Utilisateur fournit son propre Dockerfile :

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# Code
COPY handler.py .

# Metadata
LABEL mecapy.name="calcul-contrainte"
LABEL mecapy.version="1.2.3"

CMD ["python", "-c", "from handler import calculate; import json; print(json.dumps(calculate(json.loads(input()))))"]
```

**Inconvénient** : Complexe pour utilisateurs non-Docker

---

## ✅ FORMAT RECOMMANDÉ FINAL

### **ZIP avec structure standardisée + mecapy.yaml**

**Avantages** :
- ✅ Simple pour utilisateurs (upload ZIP via UI)
- ✅ Flexible (support tests, data, documentation)
- ✅ Versionnable (Git-friendly)
- ✅ Validable (schema YAML + tests)
- ✅ Portable (migration facile entre environnements)

**Structure minimale** :
```
function.zip
├── mecapy.yaml       # Obligatoire
└── handler.py        # Obligatoire
```

**Structure complète** :
```
function.zip
├── mecapy.yaml
├── handler.py
├── requirements.txt
├── tests/
│   └── test_handler.py
├── data/
│   └── coefficients.json
├── README.md
└── examples/
    └── example_usage.py
```

---

## 🎯 EXEMPLE COMPLET : Fonction de calcul RDM

```yaml
# mecapy.yaml
version: "1.0"
metadata:
  name: "rdm-poutre-flexion"
  description: "Calcul flèche poutre en flexion simple"
  tags: ["rdm", "poutre", "flexion"]
runtime:
  python_version: "3.12"
  timeout: 60
io:
  inputs_schema:
    type: object
    properties:
      longueur: {type: number, minimum: 0.1, maximum: 100}
      charge: {type: number, minimum: 0}
      inertie: {type: number, minimum: 1e-12}
      module_young: {type: number, default: 210000}
    required: [longueur, charge, inertie]
  outputs_schema:
    type: object
    properties:
      fleche_max: {type: number, description: "Flèche maximale (mm)"}
      position_fleche_max: {type: number, description: "Position (m)"}
```

```python
# handler.py
def calculate(inputs):
    L = inputs['longueur']  # m
    q = inputs['charge']    # N/m
    I = inputs['inertie']   # m⁴
    E = inputs.get('module_young', 210000)  # MPa

    # Flèche max poutre bi-appuyée charge uniforme
    fleche_max = (5 * q * L**4) / (384 * E * I) * 1000  # mm
    position = L / 2  # m

    return {
        'fleche_max': fleche_max,
        'position_fleche_max': position
    }
```

---

## 📋 RÉSUMÉ

### **Fichiers obligatoires**
1. `mecapy.yaml` - Configuration et métadonnées
2. `handler.py` - Code avec fonction `calculate(inputs) -> outputs`

### **Fichiers optionnels**
3. `requirements.txt` - Dépendances Python
4. `tests/` - Tests unitaires (recommandé)
5. `data/` - Données statiques
6. `README.md` - Documentation

### **Format I/O**
- **Entrée** : `dict` JSON (validation via `inputs_schema`)
- **Sortie** : `dict` JSON (documentation via `outputs_schema`)
- **Fichiers binaires** : Références S3 (clés dans inputs/outputs)

### **Validation**
- Schéma YAML validé au déploiement
- Code Python analysé (blacklist imports)
- Tests exécutés automatiquement
- Image Docker buildée et pushée au registry

---

**🎯 Ce format couvre tous vos besoins : validation, sérialisation, versioning, tests, et préparation Git !**

**Document généré le** : 2025-09-30
**Version** : 1.0
**Auteur** : MecaPy Architecture Team
