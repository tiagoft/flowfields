# flowfields

Generative-art library of composable fields (`src/flowfields`), with demos in
`demos/` and the Genuary 2026 pieces in `artwork/genuary2026/`. Run Python
with `uv run`. Do not add other artworks to `artwork/`.

The library gives fields and nothing that follows them: no line tracing,
particles or integrators. People use flow fields for lines,
movement, physics and more, with their own tools. Helpers for that belong
in the demos, not in `src/flowfields`.

## The JS port

`js/flowfields.js` is a p5.js version of `src/flowfields`, generated with the
`/port-js` skill (`.claude/skills/port-js/SKILL.md`). Never edit it by hand;
change the Python and run `/port-js`. Tests: `uv run pytest` for Python and
`cd js && npm test` for the port.

## Writing Python that ports well

- Randomness goes through `np.random.Generator`: a class that draws numbers
  takes `rng: np.random.Generator | int | None = None` and stores
  `self.rng = np.random.default_rng(rng)`. Do not use the global
  `np.random.*` functions in `src/flowfields`.
- Fields work on a single 2D point at a time (`__call__(x)` with `x` of
  shape `(2,)`). Avoid numpy broadcasting tricks that have no direct
  translation to `p5.Vector`.
- Keep plotting and file I/O in separate methods or in `utils.py`, so the
  rest of a class can be ported without them.

## Commits

Commit messages follow Conventional Commits: a type, a colon and a short
summary in the imperative or descriptive form, such as
`feat: NoiseField chooses its distribution`. Types in use:

- `feat:` new behavior in the library, the JS port or a demo
- `fix:` a bug fix
- `doc:` documentation and docstrings only
- `demo:` demos and their figures
- `test:` tests and fixtures only
- `refactor:` code changes that keep the behavior
- `chore:` tooling, dependencies, config, repository housekeeping

Keep each commit to one kind of change; split a change that mixes types.

## Branches and versions

Every change is made on its own branch, named after its type (such as
`feat/noise-distribution` or `fix/fieldselect-weights`), and enters main
with `git merge --no-ff`. Do not commit directly on main. The merge commit's
message follows the same Conventional Commits form and summarizes the branch.

Each commit on main bumps the patch number of the version (0.1.0 becomes
0.1.1) through the hooks in `.githooks/`, which run `tools/bump_version.py`
and update `pyproject.toml`, `uv.lock`, `js/package.json` and
`js/package-lock.json`. Do not change the version on a branch, except to set
a new minor or major version (such as 0.3.0) when the user asks: a commit
that changes the version by hand keeps it, with no bump on top. Change it in
all four files. After cloning, turn the hooks on and keep merges into main from
fast-forwarding, since a fast-forward makes no commit and skips the bump:

```sh
git config core.hooksPath .githooks
git config branch.main.mergeOptions --no-ff
git config pull.ff only
```

## Releasing

Pushing a tag `v` + the version in `pyproject.toml` runs
`.github/workflows/publish.yml`, which tests, builds and publishes to PyPI
and npm:

```sh
git tag "v$(sed -n 's/^version = "\(.*\)"$/\1/p' pyproject.toml)"
git push origin --tags
```

Tag `main` after the merge that should be released. The JS examples, the
READMEs and `js/README.md` load `flowfields.js` from jsDelivr at a fixed tag
(`@v0.2.0`); after a release, move those URLs to the new tag if they should
use it. Do not create or push
tags unless the user asks: a pushed tag publishes, and PyPI never accepts the
same version twice.
