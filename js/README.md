# flowfields for p5.js

The [flowfields](https://github.com/tiagoft/flowfields) library for
[p5.js](https://p5js.org): composable vector, scalar and color fields for
generative art. It has the same fields as the Python library, generated from
it, and gives the same numbers for the same inputs.

## Loading it

`flowfields.js` needs p5.js 2.x. Load it after p5:

```html
<script src="https://cdn.jsdelivr.net/npm/p5@2.4.0/lib/p5.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/tiagoft/flowfields@main/js/flowfields.js"></script>
```

It defines the global `flowfields`. In node, `require("flowfields")` gives the
same object, but p5 must already be loaded as the global `p5`.

Build fields inside `setup()` or later: p5 2.x only finishes setting up
`p5.Vector` when the sketch starts.

## Example

```js
const { RotationField, ExpansionField, FieldSum, GaussianField, vec } = flowfields;

let field;

function setup() {
  createCanvas(600, 600);
  noFill();
  const a = vec(200, 300);
  const b = vec(400, 300);
  field = new FieldSum({
    fields: [new RotationField({ center: a }), new ExpansionField({ center: b, direction: -1 })],
    weights: [new GaussianField({ center: a, sigma: 120 }), new GaussianField({ center: b, sigma: 100 })],
  });
}

function draw() {
  let x = vec(random(width), random(height));
  beginShape();
  for (let i = 0; i < 50; i++) {
    vertex(x.x, x.y);
    x = p5.Vector.add(x, p5.Vector.mult(field.at(x), 3));
  }
  endShape();
}
```

The library gives the fields; following them, as this sketch does with
lines, is up to you.

More in [`examples/`](https://github.com/tiagoft/flowfields/tree/main/js/examples):

- [`flow`](https://github.com/tiagoft/flowfields/tree/main/js/examples/flow): lines through a sum of fields with Gaussian
  weights.
- [`colors`](https://github.com/tiagoft/flowfields/tree/main/js/examples/colors): lines colored from an image with
  `MatrixColorField`.

The examples load files, so open them through a local server, such as
`python3 -m http.server` from the root of the repository, and not as
`file://` pages.

## From Python to JS

The [Python documentation](https://github.com/tiagoft/flowfields#readme) and
its [demos](https://github.com/tiagoft/flowfields/blob/main/demos/README.md)
describe every field. In JS:

| Python | JS |
| --- | --- |
| `RotationField(center, direction=-1)` | `new RotationField({ center, direction: -1 })` |
| `min_corner`, `n_colors`, `lerp_len` | `minCorner`, `nColors`, `lerpLen` |
| `field(x)` | `field.at(x)` |
| `np.array([x, y])` | `vec(x, y)` (a `p5.Vector`), or `[x, y]` when building a field |
| `utils.normalize_vector(v)` | `normalizeVector(v)` |
| `np.random.default_rng(0)` | `new Generator(0)`, with `random()`, `uniform()`, `normal()`, `integers()`, `choice()` |
| `rng=0` | `rng: 0`, or `rng: generator` |
| `utils.open_image("a.png")` | `imageToMatrix(img)`, on a `p5.Image` from `loadImage` |

Constructors take one object with the Python argument names in camelCase and
the same defaults. Fields return new vectors and never change the vectors
they receive.

Differences from Python:

- The same seed gives different random numbers in each language, so random
  fields have the same statistics but not the same draws.
- `MatrixField.plot_figure` exists only in Python.
- Options a field does not use give an `UnusedArgumentWarning` in the
  console, as in Python, but without the "did you mean" suggestion. To swap
  field types on purpose without it:

  ```js
  flowfields.warnings.unusedArguments = false;
  ```

## Tests

`flowfields.js` is generated from the Python library in `src/flowfields`, and
the tests compare the two with values computed in Python:

```bash
npm install
npm test
```

## License

[GNU Affero General Public License v3.0 or later](https://github.com/tiagoft/flowfields/blob/main/LICENSE).
