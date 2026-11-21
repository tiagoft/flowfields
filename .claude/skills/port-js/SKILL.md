---
name: port-js
description: Port changes in the Python library (src/tstudio) to its p5.js version (js/tstudio.js), and check them with fixtures computed in Python. Use when the user runs /port-js or asks to sync, update or port the JS / p5.js version.
---

# Port src/tstudio to js/tstudio.js

The Python code in `src/tstudio` is the source of truth. `js/tstudio.js` is
generated from it and is never edited by hand. Python and JS must give the
same numbers for the same inputs, and `js/test/fixtures.json` (made by
`tools/export_fixtures.py`) is how we check that.

## Steps

1. **Find what changed.** Read the `source-commit:` line at the top of
   `js/tstudio.js`, then run
   `git diff <source-commit> -- src/tstudio` (this includes uncommitted
   changes) and `git status src/tstudio` for new files. If the diff is
   empty, say so and stop.
2. **Port each change** into the section of `js/tstudio.js` that is named
   after the Python file (`// src/tstudio/vector_fields/sum.py`). A new
   Python module gets a new section, in the same order as the `__init__.py`
   imports, and its names go in the `tstudio` object at the end of the file.
   Follow the conventions below.
3. **Update the fixtures** in `tools/export_fixtures.py`:
   - a new or changed class gets cases in `SCALAR_CASES`, `VECTOR_CASES` or,
     if it draws random numbers, `STATS_CASES`. Cover every option, with
     `normalize=False` in at least one case so lengths are checked too;
   - a new function in `utils.py` gets cases in `UTIL_CASES`;
   - remove from `NOT_PORTED` what has just been ported.
   Then run `uv run python tools/export_fixtures.py` from the repo root.
4. **Test:** `cd js && npm test` (run `npm install` first if
   `node_modules` is missing). Fix the port until everything passes. Never
   fix a failure by changing the expected values or loosening `TOL` — if
   you think the Python side is wrong, stop and tell the user.
5. **Update the header** of `js/tstudio.js`: `source-commit:` becomes the
   output of `git rev-parse --short HEAD`, and the "Not ported yet" /
   "Python-only" lines list what is still missing. If `src/tstudio` has
   uncommitted changes, add `+uncommitted` after the hash and tell the user
   to commit, then update the hash.
6. **Report** what was ported, what was left out and why, and the test
   result. Do not commit unless the user asks.

## Conventions

**Structure**
- One file, `js/tstudio.js`, wrapped in an IIFE that sets the global
  `tstudio` (for `<script>` tags) and `module.exports` (for node).
- Names: classes keep their Python names; functions, methods, attributes
  and arguments become camelCase (`normalize_vector` → `normalizeVector`,
  `min_corner` → `minCorner`, `list_of_fields` → `listOfFields`).
- A Python `__call__(self, x)` becomes `at(x)`. Other methods keep their
  name in camelCase. Private helpers start with `_`.
- Constructors take a single options object with the Python argument names
  in camelCase, and the same defaults:
  `def __init__(self, center, direction=1)` →
  `constructor({ center, direction = 1 })`. Arguments without a default
  stay without one. Drop `**kwargs`.
- `isinstance(w, ScalarField)` → `w instanceof ScalarField`.
- `raise ValueError(msg)` → `throw new Error(msg)`.
- Keep the Python docstring's formula as a one-line JSDoc comment; do not
  copy whole docstrings.

**Vectors**
- 2D points and vectors are `p5.Vector`. Make them with `vec(x, y)`.
  Vector arguments given by the user go through `asVector()`, which also
  accepts `[x, y]`.
- `p5.Vector` is mutable and numpy arrays in our code are not mutated, so
  **never change a vector you did not create in the same function**: use
  the static forms (`p5.Vector.sub(a, b)`, `p5.Vector.mult(v, s)`) or
  `.copy()` first. Calling `.add()`, `.mult()`, `.normalize()` in place is
  fine only on a vector the function just made. The tests check that
  inputs are not changed.
- Python's `np.linalg.norm(v)` → `v.mag()`; `np.sum((a - b)**2)` →
  `p5.Vector.sub(a, b).magSq()`; element-wise comparisons on a point
  (`np.all(x >= lo)`) are written out for `.x` and `.y`.
- Python functions that return tuples return arrays (`[radius, angle]`).

**Numbers**
- Python's `round()` rounds half to even: use `roundHalfEven`, not
  `Math.round`. `int(v)` truncates toward zero: use `Math.trunc`.
  `np.argmax` takes the first maximum: compare with a strict `>`.
- Matrices (`data` in `MatrixField`) are arrays of rows: `data[row][col]`,
  `data.length` rows, `data[0].length` columns.

**Randomness**
- In Python, a class that draws random numbers takes
  `rng: np.random.Generator | int | None = None` and stores
  `self.rng = np.random.default_rng(rng)`. Nothing in `src/tstudio` uses the
  global `np.random.*` functions; if a diff adds one, point it out to the
  user instead of porting it.
- In JS, the same argument is stored as `this.rng = defaultRng(rng)`, and
  the `Generator` in `tstudio.js` has numpy's method names:
  `random()`, `uniform(low, high)`, `normal(loc, scale)`,
  `choice(n, { size, replace, p })`. A draw of `size=x.shape` becomes one
  draw per coordinate. If a port needs a numpy method that `Generator` lacks,
  add it to `Generator` with numpy's name and arguments.
- The two languages draw different numbers from the same seed, so random
  classes are checked only by statistics (`STATS_CASES`) plus a JS check
  that the same seed repeats the same draws.

**What not to port**
- Plotting, file reading and anything that needs matplotlib, PIL, sklearn
  or scipy: list it under "Python-only" in the header. If the class cannot
  work without it (`MatrixColorField` needs k-means), ask the user before
  writing a JS replacement, and keep it in "Not ported yet" meanwhile.
- Things only a sketch needs (such as `imageToMatrix`) go in the
  "p5 extras" section, which has no Python counterpart.

## p5.js notes
- p5 2.x only finishes setting up `p5.Vector` when the first sketch starts,
  so `p5.Vector.add(a, b)` gives `NaN` before that. Fields are built inside
  `setup()` or later; `js/test/load.js` creates an empty sketch for the
  tests.
- `js/examples/` has sketches that use the library. When a port changes a
  constructor that an example uses, update the example too.
