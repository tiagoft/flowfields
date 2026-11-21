# tstudio

Generative-art library of composable fields (`src/tstudio`), with demos in
`demos/` and the Genuary 2026 pieces in `artwork/genuary2026/`. Run Python
with `uv run`. Do not add other artworks to `artwork/`.

## The JS port

`js/tstudio.js` is a p5.js version of `src/tstudio`, generated with the
`/port-js` skill (`.claude/skills/port-js/SKILL.md`). Never edit it by hand;
change the Python and run `/port-js`. Tests: `cd js && npm test`.

## Writing Python that ports well

- Randomness goes through `np.random.Generator`: a class that draws numbers
  takes `rng: np.random.Generator | int | None = None` and stores
  `self.rng = np.random.default_rng(rng)`. Do not use the global
  `np.random.*` functions in `src/tstudio`.
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
