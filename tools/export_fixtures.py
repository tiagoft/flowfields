"""
Writes js/test/fixtures.json: cases evaluated with the Python library, which
the JS port must reproduce (see .claude/skills/port-js).

Each case describes a field as a JSON spec that both languages can build:

    {"type": "RotationField", "args": {"center": {"vec": [0, 0]}}}

Inside ``args``, ``{"vec": [x, y]}`` is a 2D vector, ``{"array": ...}`` is a
matrix, and any dict with a ``"type"`` is another field.  Argument names are
the Python ones; the JS test converts them to camelCase.

Case kinds:
    "scalar" / "vector": the field at each of ``points`` must equal ``expected``.
    "util": the function ``fn`` applied to ``args`` must return ``expected``.
    "stats": random fields.  The two languages draw different numbers, so
        only statistics over ``n`` draws at ``point`` are compared.

Run with:  uv run python tools/export_fixtures.py
"""

import json
from pathlib import Path

import numpy as np

import tstudio.scalar_fields as sf
import tstudio.utils as utils
import tstudio.vector_fields as vf

OUTPUT = Path(__file__).parent.parent / "js" / "test" / "fixtures.json"

# Fields that the JS port does not have yet.  Cases for them are not exported.
NOT_PORTED = {"FieldSelect", "MatrixColorField"}

CLASSES = {
    name: getattr(module, name)
    for module in (sf, vf)
    for name in module.__all__
}


def vec(x, y):
    return {"vec": [x, y]}


def field(type_, **args):
    return {"type": type_, "args": args}


def build(spec):
    """Builds a Python object from a JSON spec."""
    if isinstance(spec, list):
        return [build(s) for s in spec]
    if isinstance(spec, dict):
        if "vec" in spec:
            return np.array(spec["vec"], dtype=float)
        if "array" in spec:
            return np.array(spec["array"], dtype=float)
        if "type" in spec:
            args = {k: build(v) for k, v in spec["args"].items()}
            return CLASSES[spec["type"]](**args)
    return spec


def to_json(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, tuple):
        return [to_json(v) for v in value]
    return float(value)


def uses_unported(spec):
    if isinstance(spec, list):
        return any(uses_unported(s) for s in spec)
    if isinstance(spec, dict):
        if spec.get("type") in NOT_PORTED:
            return True
        return any(uses_unported(v) for v in spec.values())
    return False


# A grid, plus points on the centres and borders used below
GRID = [[x, y] for x in np.linspace(-1.5, 1.5, 7) for y in np.linspace(-1.5, 1.5, 7)]
POINTS = GRID + [[0.3, -0.2], [-0.5, -0.2], [0.5, 0.5], [-1.0, -1.0], [1.0, 0.5], [0.0, -0.25], [0.37, 0.11]]

MATRIX = {"array": [[0.0, 0.2, 0.4, 0.6, 0.8],
                    [1.0, 0.5, 0.25, 0.1, 0.0],
                    [0.3, 0.3, 0.9, 0.3, 0.3],
                    [0.7, 0.1, 0.0, 0.5, 1.0]]}

SCALAR_CASES = {
    "constant": field("ConstantField", value=0.7),
    "gaussian": field("GaussianField", center=vec(0.3, -0.2), sigma=0.5, scale=2.0),
    "box_swapped_corners": field("BoxField", min_corner=vec(0.5, 0.5), max_corner=vec(-0.5, -0.2),
                                 inside_value=2.0, outside_value=-1.0),
    "matrix": field("MatrixField", min_corner=vec(-1.0, -1.0), max_corner=vec(1.0, 0.5), data=MATRIX),
    "matrix_normalized": field("MatrixField", min_corner=vec(1.0, 0.5), max_corner=vec(-1.0, -1.0),
                               data={"array": [[2.0, 4.0], [6.0, 3.0], [5.0, 2.5]]}, normalize=True),
    "kernel_matrix": field("KernelProbabilisticMatrixField", min_corner=vec(-1.0, -1.0),
                           max_corner=vec(1.0, 0.5), data=MATRIX, sigma=0.7),
}

C = vec(0.37, 0.11)
GAUSS_A = field("GaussianField", center=vec(-0.5, 0.0), sigma=0.6)
GAUSS_B = field("GaussianField", center=vec(0.5, 0.3), sigma=0.4, scale=1.5)

VECTOR_CASES = {
    "rotation": field("RotationField", center=C),
    "rotation_cw_raw": field("RotationField", center=C, direction=-1, normalize=False),
    "expansion": field("ExpansionField", center=C),
    "expansion_in_raw": field("ExpansionField", center=C, direction=-1, normalize=False),
    "sum_no_weights": field("FieldSum", fields=[field("RotationField", center=C),
                                                field("ExpansionField", center=vec(0, 0))]),
    "sum_float_weights_raw": field("FieldSum", fields=[field("RotationField", center=C),
                                                       field("ExpansionField", center=vec(0, 0))],
                                   weights=[1.0, 0.3], normalize=False),
    "sum_scalar_weights_raw": field("FieldSum", fields=[field("RotationField", center=vec(-0.5, 0.0)),
                                                        field("ExpansionField", center=vec(0.5, 0.3), direction=-1)],
                                    weights=[GAUSS_A, GAUSS_B], normalize=False),
    "sum_nested": field("FieldSum", fields=[
        field("FieldSum", fields=[field("RotationField", center=C), field("ExpansionField", center=C)],
              weights=[1.0, 0.3]),
        field("RotationField", center=vec(-1, -1), direction=-1),
    ], weights=[field("ConstantField", value=0.5), GAUSS_B]),
    "max_no_weights": field("FieldMax", fields=[field("RotationField", center=C),
                                                field("ExpansionField", center=C)]),
    "max_float_weights": field("FieldMax", fields=[field("RotationField", center=C),
                                                   field("ExpansionField", center=C)],
                               weights=[0.2, 0.9]),
    "max_scalar_weights_raw": field("FieldMax", fields=[field("RotationField", center=vec(-0.5, 0.0)),
                                                        field("ExpansionField", center=vec(0.5, 0.3))],
                                    weights=[GAUSS_A, GAUSS_B], normalize=False),
}

VECTORS = [vec(3.0, 4.0), vec(0.0, 0.0), vec(-0.2, 0.7), vec(-1.0, -1e-3), vec(0.5, -2.0)]

UTIL_CASES = (
    [("normalize_vector", [v]) for v in VECTORS]
    + [("clamp_vector", [v, 0.5, 1.0]) for v in VECTORS]
    + [("clamp_vector", [v, 2.0, 3.0]) for v in VECTORS]
    + [("lerp", [vec(1, 2), vec(-3, 0.5), t]) for t in (0.0, 0.25, 1.0)]
    + [("clamp", [v, -1.0, 2.0]) for v in (-3.0, 0.5, 2.0, 7.0)]
    + [("cartesian_to_polar", [v]) for v in VECTORS]
    + [("polar_to_cartesian", [r, a]) for r, a in ((1.0, 0.0), (2.0, 2.5), (0.5, -1.0))]
    + [("rotate_vector", [v, a]) for v in VECTORS for a in (0.3, -2.0)]
    + [("quantize_vector", [v, n]) for v in VECTORS for n in (4, 6, 8)]
)

STATS_N = 20000
STATS_CASES = {
    "noise_gaussian": field("NoiseField", rng=1),
    "noise_gaussian_raw": field("NoiseField", normalize=False, rng=2),
    "noise_uniform": field("NoiseField", distribution="uniform", rng=3),
    "noise_uniform_raw": field("NoiseField", distribution="uniform", normalize=False, rng=4),
    "rotation_plus_noise_raw": field("FieldSum", fields=[field("RotationField", center=vec(0, 0)),
                                                         field("NoiseField", normalize=False, rng=5)],
                                     weights=[1.0, 0.5], normalize=False),
}


def stats(samples):
    samples = np.array(samples)
    norms = np.linalg.norm(samples, axis=1)
    return {
        "mean": samples.mean(axis=0).tolist(),
        "var": samples.var(axis=0).tolist(),
        "mean_norm": float(norms.mean()),
        "var_norm": float(norms.var()),
    }


def main():
    cases = []
    for kind, specs in (("scalar", SCALAR_CASES), ("vector", VECTOR_CASES)):
        for name, spec in specs.items():
            if uses_unported(spec):
                continue
            f = build(spec)
            expected = [to_json(f(np.array(p, dtype=float))) for p in POINTS]
            cases.append({"name": name, "kind": kind, "spec": spec, "points": POINTS, "expected": expected})

    for fn, args in UTIL_CASES:
        result = getattr(utils, fn)(*build(args))
        cases.append({"name": fn, "kind": "util", "fn": fn, "args": args, "expected": to_json(result)})

    point = [0.4, -0.3]
    for name, spec in STATS_CASES.items():
        if uses_unported(spec):
            continue
        f = build(spec)
        samples = [f(np.array(point)) for _ in range(STATS_N)]
        cases.append({"name": name, "kind": "stats", "spec": spec, "point": point,
                      "n": STATS_N, "expected": stats(samples)})

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"cases": cases}, indent=1))
    print(f"Wrote {len(cases)} cases to {OUTPUT}")


if __name__ == "__main__":
    main()
