# Backlog

Ideas that are planned but not started. Move an item out of here when its
work begins.

## Publishing to PyPI

The name `flowfields` was free on PyPI and npm on 2026-11-21. `uv build` and
`twine check` already pass; the wheel holds only `src/flowfields` and the
LICENSE.

### The repository goes public

- [ ] Decide whether to recreate the GitHub repository first. Commits from
      before the history rewrite, with private artwork, may still be reachable
      by hash on GitHub.
- [ ] Make the repository public.
- [ ] Make the README links absolute
      (`https://raw.githubusercontent.com/tiagoft/flowfields/main/...` for
      images, `https://github.com/tiagoft/flowfields/blob/main/...` for
      files). The README becomes the PyPI page, where relative links break.
      Do it only after the repository is public: while it is private,
      absolute links break on GitHub itself, because GitHub loads images
      through a proxy that has no access to it.

### Package contents

- [x] Delete `src/flowfields/main.py`, a placeholder that prints a greeting,
      and the commented `[project.scripts]` in `pyproject.toml`.
- [x] Delete the empty `src/flowfields/color_fields/utils.py`.
- [x] `__version__` in `flowfields/__init__.py`, read with
      `importlib.metadata.version("flowfields")` so the version hook stays the
      only place that changes it.
- [x] Imports at the package level, so `import flowfields as ff` gives
      `ff.RotationField`, `ff.GaussianField` and so on.
- [x] An empty `py.typed`, so type checkers use the annotations.

### Metadata in `pyproject.toml`

- [x] `requires-python = ">=3.10"`: the code needs nothing newer.
- [x] `authors`.
- [x] `[project.urls]`: Homepage, Source, Issues and the demos.
- [x] `keywords`: generative art, flow field, vector field, creative coding,
      p5.js.
- [x] `classifiers`: development status, Python versions,
      `Topic :: Artistic Software`, `Topic :: Multimedia :: Graphics`. No
      license classifier: `license = "AGPL-3.0-or-later"` replaces it.
- [x] `scikit-learn` is gone: `flowfields.utils.kmeans` replaces it.
- [ ] Decide whether `matplotlib` (only `MatrixField.plot_figure`) becomes an
      optional extra. Its import is already inside `plot_figure`.

### Checks

- [ ] Python tests with `pytest`, at least one per field and per helper.
- [ ] A GitHub Action that runs `pytest` on Python 3.10 to 3.13 and
      `npm test` in `js/`.
- [ ] `uv build`, `uvx twine check dist/*`, then install the wheel in a new
      virtual environment and run the README example there.

### Publishing

- [ ] Choose the first public version: the current `0.1.x`, or `0.2.0` to
      mark the release.
- [ ] Create a PyPI account with two-factor authentication, and a TestPyPI
      account.
- [ ] Set up trusted publishing: a GitHub Action publishes when a `v*` tag
      is pushed, with no token stored anywhere.
- [ ] Decide how tags are created: by hand when releasing, or by the version
      hook on every merge. jsDelivr needs the tags to serve a fixed version
      of `flowfields.js`.
- [ ] Publish to TestPyPI first, and install from there with
      `pip install -i https://test.pypi.org/simple/ flowfields`.
- [ ] Publish to PyPI, and check `pip install flowfields` in a clean
      environment.

## Tracing lines through a field

Today the library gives a vector for each point, but following the field to
draw a line is left to each user: `strokes()` in `demos/_common.py`, every
Genuary piece and `js/examples/flow/sketch.js` each write the same loop.

### `trace`

A pure function that follows the field from **one** starting point and
returns **one** line. It draws nothing; drawing stays with matplotlib, cairo,
p5 or SVG. The loop over many lines stays with the user, so each line can
have its own `n_steps`, color or width.

```python
def trace(
    field,                  # FlowField, or any callable x -> vector
    start,                  # starting point, shape (2,)
    n_steps: int = 50,
    step: float = 0.01,
    transform=None,         # v -> v applied at each step (rotate, quantize...)
    bounds=None,            # (min_corner, max_corner): stop on leaving the box
    backward: bool = False, # also follow the field backward from start
) -> np.ndarray:            # points of the line, shape (n, 2)
```

Use:

```python
for start in ff.random_points(n=800, bounds=box, rng=0):
    line = ff.trace(field, start, n_steps=40, step=0.01,
                    transform=lambda v: ff.utils.quantize_vector(v, 4))
    ax.plot(*line.T)
```

In JS: `flowfields.trace(field, start, { nSteps, step, ... })`, returning an
array of `p5.Vector`.

Decisions:

- `transform` is what `strokes()` does today, and is how `rotate_vector`,
  `quantize_vector` and `clamp_vector` reach the lines.
- `backward=True` puts the starting point in the middle of the line, so lines
  do not all begin at the random starting points.
- Euler integration first, as the artwork uses. A `method="rk2"` can come
  later; it calls the field several times per step, which makes no sense for
  `NoiseField` and `FieldSelect`.
- The field is called once per step and in order, so stateful fields stay
  reproducible with the same `rng`.

### Starting points

`random_points(n, bounds, rng)` and `grid_points(nx, ny, bounds)`, which
return the starting points for `trace`.

### Later

- `trace_many(field, starts, **kw)` for convenience; it does not replace
  `trace`.
- SVG export of the lines, for pen plotters.
- `even_lines(field, separation, ...)`: evenly spaced lines that do not cross
  (Jobard and Lefer), built on `trace` with a grid of the lines drawn so far.

### Plan

`trace`, `random_points` and `grid_points` in Python with tests, then
`/port-js`. SVG right after.
