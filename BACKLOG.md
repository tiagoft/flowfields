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
      files), including the two badges, which climb out of the file with
      `../../`. The README becomes the PyPI page, where relative links break.
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
- [x] `matplotlib` is the optional extra `flowfields[plot]`, needed only by
      `MatrixField.plot_figure`.

### Checks

- [x] Python tests with `pytest`, at least one per field and per helper.
- [x] A GitHub Action that runs `pytest` on Python 3.10 to 3.13 and
      `npm test` in `js/`.
- [x] `uv build`, `uvx twine check dist/*`, then install the wheel in a new
      virtual environment and run the README example there.

### Publishing

- [ ] Choose the first public version: the current `0.1.x`, or `0.2.0` to
      mark the release.
- [ ] Create a PyPI account with two-factor authentication, and a TestPyPI
      account.
- [x] Set up trusted publishing: a GitHub Action publishes when a `v*` tag
      is pushed, with no token stored anywhere.
- [ ] Register the workflow as a trusted publisher, on PyPI and on TestPyPI
      (for a project that does not exist yet, as a "pending publisher"):
      owner `tiagoft`, repository `flowfields`, workflow `publish.yml`,
      environment `pypi` on PyPI and `testpypi` on TestPyPI.
- [ ] Decide how tags are created: by hand when releasing, or by the version
      hook on every merge. jsDelivr needs the tags to serve a fixed version
      of `flowfields.js`.
- [ ] Publish to TestPyPI first, and install from there with
      `pip install -i https://test.pypi.org/simple/ flowfields`.
- [ ] Publish to PyPI, and check `pip install flowfields` in a clean
      environment.

## JS

- [ ] Publish `flowfields` on npm (the name was free on 2026-11-21). The
      package is ready: `npm pack` gives `flowfields.js`, the README and the
      LICENSE. Make the links in `js/README.md` absolute first, since npm
      shows it as the package page.
- [ ] Publish `js/examples/` on GitHub Pages once the repository is public,
      so the sketches run in the browser from a link.

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
