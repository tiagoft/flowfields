# Backlog

Ideas that are planned but not started. Move an item out of here when its
work begins.

## Publishing to PyPI

The name `flowfields` was free on PyPI and npm on 2026-11-21. `uv build` and
`twine check` already pass; the wheel holds only `src/flowfields` and the
LICENSE.

### The repository goes public

- [x] Keep the GitHub repository rather than recreate it: the old commits
      that stay reachable by hash hold only drafts and experiments.
- [x] Make the repository public (2026-11-21).
- [x] Make the links in `README.md` and `js/README.md` absolute, for the
      PyPI and npm pages.

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
- [x] `matplotlib` is the optional extra `flowfields[plot]`, needed only by
      `MatrixField.plot_figure`.

### Checks

- [x] Python tests with `pytest`, at least one per field and per helper.
- [x] A GitHub Action that runs `pytest` on Python 3.10 to 3.13 and
      `npm test` in `js/`.
- [x] `uv build`, `uvx twine check dist/*`, then install the wheel in a new
      virtual environment and run the README example there.

### Publishing

- [x] The first public version is 0.2.0.
- [x] Create a PyPI account with two-factor authentication.
- [x] Set up trusted publishing: a GitHub Action publishes when a `v*` tag
      is pushed, with no token stored anywhere.
- [x] Register the workflow as a trusted publisher on PyPI: owner
      `tiagoft`, repository `flowfields`, workflow `publish.yml`, environment
      `pypi`. Releases go straight to PyPI, without TestPyPI.
- [ ] Decide how tags are created: by hand when releasing, or by the version
      hook on every merge. jsDelivr needs the tags to serve a fixed version
      of `flowfields.js`.
- [x] Publish to PyPI, and check `pip install flowfields` in a clean
      environment: 0.2.0 is on https://pypi.org/project/flowfields/
      (2026-11-21).

## JS

- [x] The publish workflow has an npm job, with trusted publishing.
- [ ] Publish `flowfields` on npm by hand once, from the `v0.2.2` tag
      (`cd js && npm login && npm publish`): npm configures trusted
      publishing only on a package that exists.
- [ ] On npmjs.com, in the package's Settings, add the trusted publisher:
      GitHub Actions, user `tiagoft`, repository `flowfields`, workflow
      `publish.yml`, environment `npm`, and tick `npm publish` under the
      allowed actions. From then on, each `v*` tag publishes to npm too.
- [ ] Publish `js/examples/` on GitHub Pages, so the sketches run in the
      browser from a link.

## Library

- [ ] A Perlin or simplex noise field: a noise that is coherent in space,
      unlike `NoiseField`, which draws a new vector at every call. It is
      the classic flow field.
- [ ] Plain functions as fields and weights, such as
      `weights=[lambda x: x[0] ** 2]`, without writing a subclass.
- [ ] `MatrixField` puts the first row of the matrix at the highest y and
      `MatrixColorField` at the lowest. Both are documented, but the same
      image gives flipped results in the two fields.
- [ ] `MatrixColorField.__call__` takes a `random_state` argument it does not
      use, and `get_probs` prints before raising on NaN.
- [ ] `KernelProbabilisticMatrixField.__call__` repeats the bilinear
      interpolation of `MatrixField` instead of reusing it.
- [ ] The `MatrixColorField` docstring should say that every color missing
      from the window counts as one pixel, so a window of a few pixels makes
      all colors about equally likely.

## Decided against

- **Tracing lines through a field** (`trace`, starting points, SVG export,
  evenly spaced lines). People use flow fields in many ways: lines, moving
  particles, Newtonian physics and more. The library gives the fields;
  following them is left to each user's own tools.
