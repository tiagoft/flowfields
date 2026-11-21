# flowfields

Generative-art library of composable fields (`src/flowfields`), with demos in
`demos/` and the Genuary 2026 pieces in `artwork/genuary2026/`. Run Python
with `uv run`. Do not add other artworks to `artwork/`.

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
and update `pyproject.toml` and `uv.lock`. Do not change the version on a
branch. After cloning, turn the hooks on and keep merges into main from
fast-forwarding, since a fast-forward makes no commit and skips the bump:

```sh
git config core.hooksPath .githooks
git config branch.main.mergeOptions --no-ff
git config pull.ff only
```
