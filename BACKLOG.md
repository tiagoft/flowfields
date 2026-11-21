# Backlog

Ideas that are planned but not started. Move an item out of here when its
work begins.

## Before publishing to PyPI

The README becomes the PyPI page, where relative links break. Make its links
absolute (`https://raw.githubusercontent.com/tiagoft/flowfields/main/...` for
images, `https://github.com/tiagoft/flowfields/blob/main/...` for files) once
the repository is public. While it is private, absolute links break on GitHub
itself, because GitHub loads images through a proxy that has no access to it.

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
