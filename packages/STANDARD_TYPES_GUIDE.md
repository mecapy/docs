# 📐 MecaPy Standard Types Guide

> Complete reference for writing type-safe function parameters

## Overview

MecaPy enforces a **restricted set of well-defined types** for function parameters to ensure:

- **Consistent documentation** across all packages
- **Robust validation** at the API level
- **Predictable UI generation** for function inputs
- **Full JSON Schema compatibility**

## Supported Standard Types

| Type | JSON Schema | Use Case | Example |
|------|-------------|----------|---------|
| `int` | `integer` | Countable quantities, iterations | `nb_bolts: int` |
| `int` (≥0) | `integer` + `minimum: 0` | Non-negative counts | `quantity: Annotated[int, Field(ge=0)]` |
| `float` | `number` | Measurements, forces, dimensions | `force: float` |
| `float` (≥0) | `number` + `minimum: 0` | Physical quantities (≥0) | `diameter: Annotated[float, Field(ge=0)]` |
| `str` | `string` | Text, designations, labels | `designation: str` |
| `Literal[...]` | `string` + `enum` | Fixed choice list | `material: Literal["S235", "S355"]` |
| `list[T]` | `array` | Collections of values | `forces: list[float]` |

---

## Type 1: Integer

### Basic Integer

```python
def calculate(
    nb_iterations: int
) -> dict:
    """
    Run iterative calculation.

    Parameters
    ----------
    nb_iterations : int
        Number of iterations to perform
    """
    ...
```

**Generated JSON Schema:**
```json
{
  "nb_iterations": {
    "type": "integer"
  }
}
```

### Constrained Integer

```python
from typing import Annotated
from pydantic import Field

def calculate(
    nb_iterations: Annotated[int, Field(
        description="Number of iterations to perform",
        ge=1,        # Greater or equal (minimum)
        le=1000,     # Less or equal (maximum)
        examples=[10, 50, 100]
    )]
) -> dict:
    """
    Run iterative calculation.

    Parameters
    ----------
    nb_iterations : int
        Number of iterations (1-1000)
    """
    ...
```

**Generated JSON Schema:**
```json
{
  "nb_iterations": {
    "type": "integer",
    "description": "Number of iterations to perform",
    "minimum": 1,
    "maximum": 1000,
    "examples": [10, 50, 100]
  }
}
```

### Integer with Default Value

```python
def calculate(
    nb_iterations: Annotated[int, Field(ge=1, le=1000)] = 10
) -> dict:
    """Calculate with default iterations."""
    ...
```

**JSON Schema:**
```json
{
  "nb_iterations": {
    "type": "integer",
    "minimum": 1,
    "maximum": 1000,
    "default": 10
  }
}
```

---

## Type 2: Non-negative Integer

For quantities that cannot be negative (counts, indices, etc.)

```python
def calculate_bolts(
    nb_bolts: Annotated[int, Field(
        description="Number of bolts in assembly",
        ge=0,        # Non-negative
        le=100,
        examples=[4, 8, 12]
    )]
) -> dict:
    """
    Calculate bolted assembly.

    Parameters
    ----------
    nb_bolts : int
        Number of bolts (0-100)
    """
    ...
```

**JSON Schema:**
```json
{
  "nb_bolts": {
    "type": "integer",
    "description": "Number of bolts in assembly",
    "minimum": 0,
    "maximum": 100,
    "examples": [4, 8, 12]
  }
}
```

---

## Type 3: Float (Decimal Number)

### Basic Float

```python
def calculate_stress(
    force: float
) -> dict:
    """
    Calculate stress.

    Parameters
    ----------
    force : float
        Applied force in Newton
    """
    ...
```

**JSON Schema:**
```json
{
  "force": {
    "type": "number"
  }
}
```

### Constrained Float

```python
def calculate_stress(
    force: Annotated[float, Field(
        description="Applied force in Newton",
        ge=0,           # Non-negative
        le=500000,      # Maximum 500 kN
        examples=[1000, 5000, 10000]
    )]
) -> dict:
    """
    Calculate stress from applied force.

    Parameters
    ----------
    force : float
        Applied force in Newton (0-500,000 N)
    """
    ...
```

**JSON Schema:**
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

### Float with Strict Bounds

```python
def calculate(
    temperature: Annotated[float, Field(
        description="Temperature in Celsius",
        gt=-273.15,     # Greater than (exclusive)
        lt=1000,        # Less than (exclusive)
        examples=[20, 100, 500]
    )]
) -> dict:
    """
    Temperature-dependent calculation.

    Parameters
    ----------
    temperature : float
        Temperature in °C (above absolute zero, below 1000°C)
    """
    ...
```

**JSON Schema:**
```json
{
  "temperature": {
    "type": "number",
    "description": "Temperature in Celsius",
    "exclusiveMinimum": -273.15,
    "exclusiveMaximum": 1000,
    "examples": [20, 100, 500]
  }
}
```

---

## Type 4: String

### Basic String

```python
def create_element(
    designation: str
) -> dict:
    """
    Create structural element.

    Parameters
    ----------
    designation : str
        Element designation (e.g., HEA200, IPE300)
    """
    ...
```

**JSON Schema:**
```json
{
  "designation": {
    "type": "string"
  }
}
```

### Constrained String

```python
def create_element(
    designation: Annotated[str, Field(
        description="Element designation (e.g., HEA200, IPE300)",
        min_length=1,
        max_length=50,
        examples=["HEA200", "IPE300", "M12"]
    )]
) -> dict:
    """
    Create structural element.

    Parameters
    ----------
    designation : str
        Element designation (1-50 characters)
    """
    ...
```

**JSON Schema:**
```json
{
  "designation": {
    "type": "string",
    "description": "Element designation (e.g., HEA200, IPE300)",
    "minLength": 1,
    "maxLength": 50,
    "examples": ["HEA200", "IPE300", "M12"]
  }
}
```

### String with Pattern (Use sparingly - prefer Literal)

```python
def create_bolt(
    designation: Annotated[str, Field(
        description="Bolt designation in M format",
        pattern="^M[0-9]{1,3}$",
        examples=["M8", "M12", "M16", "M20"]
    )]
) -> dict:
    """
    Create bolt from designation.

    Parameters
    ----------
    designation : str
        Metric designation (M8, M12, etc.)
    """
    ...
```

**JSON Schema:**
```json
{
  "designation": {
    "type": "string",
    "description": "Bolt designation in M format",
    "pattern": "^M[0-9]{1,3}$",
    "examples": ["M8", "M12", "M16", "M20"]
  }
}
```

**⚠️ Note:** Prefer `Literal` over `pattern` when choices are fixed.

---

## Type 5: Literal (Enum - Fixed Choices)

### Basic Literal

```python
from typing import Literal

def calculate_assembly(
    material: Literal["S235", "S355", "S460"]
) -> dict:
    """
    Calculate assembly with steel material.

    Parameters
    ----------
    material : {"S235", "S355", "S460"}
        Steel grade according to EN 10025
    """
    ...
```

**JSON Schema:**
```json
{
  "material": {
    "type": "string",
    "enum": ["S235", "S355", "S460"]
  }
}
```

### Literal with Description and Default

```python
def calculate_assembly(
    material: Annotated[Literal["S235", "S355", "S460"], Field(
        description="Steel grade according to EN 10025"
    )] = "S235",
    bolt_class: Literal["4.6", "5.6", "8.8", "10.9"] = "8.8"
) -> dict:
    """
    Calculate bolted assembly.

    Parameters
    ----------
    material : {"S235", "S355", "S460"}
        Steel grade (default: S235)
    bolt_class : {"4.6", "5.6", "8.8", "10.9"}
        Bolt property class (default: 8.8)
    """
    ...
```

**JSON Schema:**
```json
{
  "material": {
    "type": "string",
    "description": "Steel grade according to EN 10025",
    "enum": ["S235", "S355", "S460"],
    "default": "S235"
  },
  "bolt_class": {
    "type": "string",
    "enum": ["4.6", "5.6", "8.8", "10.9"],
    "default": "8.8"
  }
}
```

### Boolean as Literal (Recommended)

```python
def calculate(
    preloaded: Literal["yes", "no"] = "yes"
) -> dict:
    """
    Calculate assembly.

    Parameters
    ----------
    preloaded : {"yes", "no"}
        Whether assembly is preloaded
    """
    ...
```

**💡 Tip:** Use `Literal["yes", "no"]` instead of `bool` for clearer UI representation.

---

## Type 6: Array (List)

### Basic Array

```python
def calculate(
    forces: list[float]
) -> dict:
    """
    Calculate resultant force.

    Parameters
    ----------
    forces : list of float
        List of forces in Newton
    """
    ...
```

**JSON Schema:**
```json
{
  "forces": {
    "type": "array",
    "items": {
      "type": "number"
    }
  }
}
```

### Constrained Array

```python
def calculate(
    forces: Annotated[list[float], Field(
        description="List of forces in Newton",
        min_length=1,      # At least 1 element
        max_length=10,     # Maximum 10 elements
    )]
) -> dict:
    """
    Calculate resultant force.

    Parameters
    ----------
    forces : list of float
        List of forces (1-10 values)
    """
    ...
```

**JSON Schema:**
```json
{
  "forces": {
    "type": "array",
    "description": "List of forces in Newton",
    "items": {
      "type": "number"
    },
    "minItems": 1,
    "maxItems": 10
  }
}
```

### Array with Default Value

```python
def calculate(
    coefficients: list[float] = [1.0, 1.5, 2.0]
) -> dict:
    """
    Calculate with safety coefficients.

    Parameters
    ----------
    coefficients : list of float
        Safety coefficients (default: [1.0, 1.5, 2.0])
    """
    ...
```

**JSON Schema:**
```json
{
  "coefficients": {
    "type": "array",
    "items": {
      "type": "number"
    },
    "default": [1.0, 1.5, 2.0]
  }
}
```

### Array of Integers

```python
def calculate(
    node_ids: Annotated[list[int], Field(
        description="List of node IDs",
        min_length=2,
        max_length=100
    )]
) -> dict:
    """
    Calculate from mesh nodes.

    Parameters
    ----------
    node_ids : list of int
        Mesh node identifiers (2-100 nodes)
    """
    ...
```

**JSON Schema:**
```json
{
  "node_ids": {
    "type": "array",
    "description": "List of node IDs",
    "items": {
      "type": "integer"
    },
    "minItems": 2,
    "maxItems": 100
  }
}
```

---

## Complete Real-World Example

```python
from typing import Annotated, Literal
from pydantic import Field

def calculate_bolted_connection(
    # Non-negative float with bounds
    diameter: Annotated[float, Field(
        description="Nominal bolt diameter in mm",
        ge=6,
        le=100,
        examples=[8, 10, 12, 16, 20, 24]
    )],

    # Literal (enum) for material
    material: Annotated[Literal["S235", "S355", "S460"], Field(
        description="Steel grade according to EN 10025"
    )],

    # Literal for bolt class
    bolt_class: Literal["4.6", "5.6", "8.8", "10.9"] = "8.8",

    # Non-negative integer
    nb_bolts: Annotated[int, Field(
        description="Number of bolts in connection",
        ge=1,
        le=100,
        examples=[4, 6, 8, 12]
    )],

    # Array of forces
    forces: Annotated[list[float], Field(
        description="Applied forces in Newton",
        min_length=1,
        max_length=10
    )],

    # Boolean as Literal
    preloaded: Literal["yes", "no"] = "yes"

) -> dict:
    """
    Calculate bolted connection according to Eurocode 3.

    Parameters
    ----------
    diameter : float
        Nominal bolt diameter in mm (6-100 mm)
    material : {"S235", "S355", "S460"}
        Steel grade according to EN 10025
    bolt_class : {"4.6", "5.6", "8.8", "10.9"}
        Bolt property class (default: 8.8)
    nb_bolts : int
        Number of bolts (1-100)
    forces : list of float
        Applied forces in Newton (1-10 values)
    preloaded : {"yes", "no"}
        Whether connection is preloaded (default: yes)

    Returns
    -------
    dict
        Calculation results with resistance and utilization
    """
    ...
```

**Generated JSON Schema:**
```json
{
  "type": "object",
  "properties": {
    "diameter": {
      "type": "number",
      "description": "Nominal bolt diameter in mm",
      "minimum": 6,
      "maximum": 100,
      "examples": [8, 10, 12, 16, 20, 24]
    },
    "material": {
      "type": "string",
      "description": "Steel grade according to EN 10025",
      "enum": ["S235", "S355", "S460"]
    },
    "bolt_class": {
      "type": "string",
      "enum": ["4.6", "5.6", "8.8", "10.9"],
      "default": "8.8"
    },
    "nb_bolts": {
      "type": "integer",
      "description": "Number of bolts in connection",
      "minimum": 1,
      "maximum": 100,
      "examples": [4, 6, 8, 12]
    },
    "forces": {
      "type": "array",
      "description": "Applied forces in Newton",
      "items": {"type": "number"},
      "minItems": 1,
      "maxItems": 10
    },
    "preloaded": {
      "type": "string",
      "enum": ["yes", "no"],
      "default": "yes"
    }
  },
  "required": ["diameter", "material", "nb_bolts", "forces"]
}
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Complex Nested Types

```python
# ❌ BAD: Nested dict with tuples
def calculate(
    config: dict[str, list[tuple[int, float]]]
) -> dict:
    ...
```

**Problem:** Cannot be reliably introspected and validated.

**✅ Solution:** Flatten to simple types
```python
def calculate(
    node_ids: list[int],
    node_values: list[float]
) -> dict:
    ...
```

### ❌ Pattern When Literal Exists

```python
# ❌ BAD: Regex for fixed choices
material: Annotated[str, Field(
    pattern="^(S235|S355|S460)$"
)]
```

**✅ Solution:** Use Literal
```python
material: Literal["S235", "S355", "S460"]
```

### ❌ Boolean Instead of Literal

```python
# ❌ ACCEPTABLE but not ideal
preloaded: bool = True
```

**✅ Better:** Explicit choices
```python
preloaded: Literal["yes", "no"] = "yes"
```

### ❌ Missing Constraints

```python
# ❌ BAD: No validation
diameter: float
```

**✅ Solution:** Add sensible bounds
```python
diameter: Annotated[float, Field(
    description="Diameter in mm",
    ge=0,
    le=1000
)]
```

---

## Validation Checklist

Before publishing a package, verify:

- [ ] All parameters use **standard types** (int, float, str, Literal, list)
- [ ] **Numeric constraints** are coherent (ge ≤ le, gt < lt)
- [ ] **Descriptions** are clear and concise
- [ ] **Examples** cover typical use cases
- [ ] **Default values** are sensible
- [ ] No **complex types** (nested dict, tuple, Union, etc.)
- [ ] **Literal** is preferred over regex patterns
- [ ] **Physical units** are documented in descriptions
- [ ] **Bounds** reflect realistic engineering values
- [ ] **NumPy docstrings** match type annotations

---

## References

- [MANIFEST_FORMAT.md](./MANIFEST_FORMAT.md) - Full manifest specification
- [Pydantic Field Documentation](https://docs.pydantic.dev/latest/concepts/fields/)
- [JSON Schema Specification](https://json-schema.org/understanding-json-schema/)
- [NumPy Docstring Standard](https://numpydoc.readthedocs.io/en/latest/format.html)

---

**Keep it simple. Use standard types. Document clearly. Validate properly.** 🚀
