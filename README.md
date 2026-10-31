# tstudio

A generative-art toolkit built around composable **vector fields** and **scalar fields**.  Fields form trees (similar to syntax trees): leaf nodes are primitives and internal nodes are combinators.

See the [demos](demos/README.md) for a small script and a figure for each feature.

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
