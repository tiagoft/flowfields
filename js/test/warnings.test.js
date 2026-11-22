// Fields warn about options they do not use, like UnusedArgumentWarning in
// src/flowfields/utils.py.
const test = require("node:test");
const assert = require("node:assert/strict");
const { load } = require("./load");

const { flowfields: ff, window, close } = load();
test.after(close);

/** Runs fn and returns what it sent to console.warn. */
function warnings(fn) {
  const sent = [];
  const original = window.console.warn;
  window.console.warn = (w) => sent.push(w);
  try {
    fn();
  } finally {
    window.console.warn = original;
  }
  return sent;
}

const IMAGE = [
  [[0.9, 0.1, 0.1], [0.9, 0.1, 0.1], [0.1, 0.2, 0.9]],
  [[0.9, 0.1, 0.1], [0.1, 0.2, 0.9], [0.1, 0.2, 0.9]],
];

// Each field with the options it needs
const FIELDS = {
  ScalarField: () => ({}),
  GaussianField: () => ({ center: [0, 0] }),
  ConstantField: () => ({}),
  BoxField: () => ({ minCorner: [0, 0], maxCorner: [1, 1] }),
  MatrixField: () => ({ minCorner: [0, 0], maxCorner: [1, 1], data: [[0, 1], [1, 0]] }),
  KernelProbabilisticMatrixField: () => ({ minCorner: [0, 0], maxCorner: [1, 1], data: [[0, 1], [1, 0]] }),
  FlowField: () => ({}),
  RotationField: () => ({ center: [0, 0] }),
  ExpansionField: () => ({ center: [0, 0] }),
  NoiseField: () => ({ rng: 0 }),
  FieldSum: () => ({ fields: [new ff.RotationField({ center: [0, 0] })] }),
  FieldMax: () => ({ fields: [new ff.RotationField({ center: [0, 0] })] }),
  FieldSelect: () => ({ fields: [new ff.RotationField({ center: [0, 0] })], rng: 0 }),
  ColorField: () => ({}),
  MatrixColorField: () => ({ minCorner: [0, 0], maxCorner: [1, 1], data: IMAGE, nColors: 2 }),
};

for (const [name, options] of Object.entries(FIELDS)) {
  test(`${name}: known options give no warning`, () => {
    assert.deepEqual(warnings(() => new ff[name](options())), []);
  });

  test(`${name}: unknown options warn`, () => {
    const sent = warnings(() => new ff[name]({ ...options(), zzz: 1 }));
    assert.equal(sent.length, 1);
    assert.ok(sent[0] instanceof ff.UnusedArgumentWarning);
    assert.equal(sent[0].message, `${name} ignores the argument 'zzz'`);
  });
}

test("several unknown options are listed in one warning", () => {
  const sent = warnings(() => new ff.RotationField({ center: [0, 0], sigma: 2, foo: 1 }));
  assert.equal(sent.length, 1);
  assert.equal(sent[0].message, "RotationField ignores the arguments 'sigma', 'foo'");
});

test("the unknown option is ignored", () => {
  let field;
  warnings(() => { field = new ff.RotationField({ center: [0, 0], normalise: false }); });
  assert.equal(field.normalize, true);
});

test("flowfields.warnings.unusedArguments = false silences the warning", () => {
  ff.warnings.unusedArguments = false;
  try {
    const sent = warnings(() => {
      for (const Cls of [ff.RotationField, ff.ExpansionField, ff.GaussianField]) {
        new Cls({ center: [1, 1], direction: -1, sigma: 0.5 });
      }
    });
    assert.deepEqual(sent, []);
  } finally {
    ff.warnings.unusedArguments = true;
  }
});

test("kmeans warns when sampleSize is larger than the data, and uses all the points", () => {
  const data = [[0, 0], [0, 0.1], [5, 5], [5, 5.1]];
  let got;
  const sent = warnings(() => { got = ff.kmeans(data, 2, 0, 100, 1e-4, 5); });
  assert.equal(sent.length, 1);
  assert.match(String(sent[0]), /larger than the 4 points/);
  assert.equal(JSON.stringify(got), JSON.stringify(ff.kmeans(data, 2, 0)));
});

test("MatrixColorField's default sampleSize gives no warning on a small image", () => {
  assert.deepEqual(warnings(() => new ff.MatrixColorField(FIELDS.MatrixColorField())), []);
  const sent = warnings(() => new ff.MatrixColorField({ ...FIELDS.MatrixColorField(), sampleSize: 7 }));
  assert.equal(sent.length, 1);
});

test("choice without replacement and without p gives distinct values in range", () => {
  const rng = new ff.Generator(3);
  const out = rng.choice(1000000, { size: 5000, replace: false });
  assert.equal(new Set(out).size, 5000);
  assert.ok(out.every((i) => Number.isInteger(i) && i >= 0 && i < 1000000));
  const all = new ff.Generator(4).choice(10, { size: 10, replace: false });
  assert.deepEqual([...all].sort((a, b) => a - b), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);
});
