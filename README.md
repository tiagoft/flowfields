# tstudio

A generative-art toolkit built around composable **vector fields** and **scalar fields**.  Fields form trees (similar to syntax trees): leaf nodes are primitives and internal nodes are combinators.  Trees can be saved to human-readable YAML files, edited by hand, and loaded back — no Python required for tweaking parameters.

---

## Concepts

### Scalar fields — `tstudio.scalar_fields`

A scalar field maps a 2-D point to a single float: `f(x) → float`.  They are used as spatial weights inside composite vector fields.

| Class | Equation |
| --- | --- |
| `GaussianField(center, sigma, scale)` | `f(x) = scale · exp(−‖x − center‖² / 2σ²)` |
| `ConstantField(value)` | `f(x) = value` |
| `BoxField(min_corner, max_corner, inside_value, outside_value)` | `inside_value` if `x` is inside the box, else `outside_value` |

### Vector fields — `tstudio.vector_fields`

A vector field maps a 2-D point to a 2-D vector: `F(x) → np.ndarray`.  Most fields accept `normalize=True` (default) to return a unit vector.

#### Primitive fields

| Class | Equation |
| --- | --- |
| `RotationField(center, direction)` | `v(x) = direction · [−rᵧ, rₓ]` where `r = x − center` |
| `ExpansionField(center, direction)` | `v(x) = direction · (x − center)` |
| `NoiseField()` | `v ~ Uniform(−1, 1)ⁿ` (fresh sample every call) |

#### Composite fields — combine other fields into a tree

| Class | Behaviour |
| --- | --- |
| `FieldSum(fields, weights)` | `v(x) = Σᵢ wᵢ(x) · Fᵢ(x)` — weighted linear blend |
| `FieldMax(fields, weights)` | `v(x) = F_{argmax wᵢ(x)}(x)` — hard winner-take-all |
| `FieldSelect(fields, weights, ...)` | probabilistic selection; switches fields over time with optional linear interpolation |

Weights can be a plain `float`, a `ScalarField` instance (position-dependent), or `None` (equal weights).

---

## Basic usage

```python
import numpy as np
import tstudio.scalar_fields as sf
import tstudio.vector_fields as vf

field = vf.FieldSum(
    fields=[
        vf.RotationField(np.array([2.0, 0.0])),
        vf.RotationField(np.array([-5.0, 0.0]), direction=-1),
        vf.ExpansionField(np.array([2.0, -6.0])),
    ],
    weights=[
        sf.GaussianField(np.array([1.0, 0.0]), sigma=3.0),
        sf.ConstantField(0.2),
        sf.ConstantField(0.5),
    ],
)

x = np.array([1.0, 0.5])
v = field(x)   # unit vector at point x
```

---

## YAML serialization

Every field tree can be saved to a YAML file and loaded back.  The format is human-readable and human-editable — you can tweak parameters (centers, sigmas, weights, …) in any text editor without touching Python.

### Saving and loading

```python
from tstudio.utils import save_field_yaml, load_field_yaml

save_field_yaml(field, "my_field.yaml")   # serialize to disk
field = load_field_yaml("my_field.yaml")  # reconstruct from disk
```

Scalar fields have equivalent helpers:

```python
from tstudio.utils import save_scalar_yaml, load_scalar_yaml
```

### Dict representation

Fields also expose `to_dict()` / `from_dict()` for in-memory use:

```python
d = field.to_dict()                         # → plain Python dict
field = vf.field_from_dict(d)               # reconstruct
field = sf.scalar_from_dict(d)              # for scalar fields
```

### Example YAML

A `FieldSum` with a Gaussian weight and a constant weight:

```yaml
type: FieldSum
normalize: true
fields:
  - type: RotationField
    center: [2.0, 0.0]
    direction: 1
    normalize: true
  - type: RotationField
    center: [-5.0, 0.0]
    direction: -1
    normalize: true
  - type: ExpansionField
    center: [2.0, -6.0]
    direction: 1
    normalize: true
weights:
  - type: GaussianField      # spatially-varying weight — peak near [1, 0]
    center: [1.0, 0.0]
    sigma: 3.0
    scale: 1.0
  - type: ConstantField      # fixed weight for field 2
    value: 0.2
  - type: ConstantField
    value: 0.5
```

A `FieldSelect` with temperature and interpolation:

```yaml
type: FieldSelect
normalize: true
select_n: 1
change_id_prob: 0.01
temperature: 1.5
lerp_len: 30
fields:
  - type: RotationField
    center: [0.0, 0.0]
    direction: 1
    normalize: true
  - type: NoiseField
    normalize: true
weights:
  - type: GaussianField
    center: [0.0, 0.0]
    sigma: 2.0
    scale: 1.0
  - type: ConstantField
    value: 0.3
```

### Supported types

Any combination of the following can appear in a YAML tree:

**Vector fields:** `RotationField`, `ExpansionField`, `NoiseField`, `FieldSum`, `FieldMax`, `FieldSelect`

**Scalar fields (as weights):** `GaussianField`, `ConstantField`, `BoxField`

Trees can be arbitrarily deep — a `FieldSum` can contain `FieldSelect` nodes whose weights are `GaussianField` instances, and so on.
