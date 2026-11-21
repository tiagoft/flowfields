// FieldSelect behavior that the fixtures cannot reach, the same checks as
// TestFieldSelect in tests/test_vector_fields.py.
const test = require("node:test");
const assert = require("node:assert/strict");
const { load } = require("./load");

const { p5, flowfields: ff, close } = load();
test.after(close);

const v = (x, y) => new p5.Vector(x, y);
const near = (a, b, where) =>
  assert.ok(Math.abs(a.x - b.x) < 1e-12 && Math.abs(a.y - b.y) < 1e-12, `${where}: ${a} != ${b}`);
const blend = (a, b, t) => p5.Vector.mult(a, 1 - t).add(p5.Vector.mult(b, t));

test("a transition blends over lerpLen calls and ends on the new field", () => {
  const rot = new ff.RotationField({ center: [0, 0] });
  const exp = new ff.ExpansionField({ center: [0, 0] });
  const f = new ff.FieldSelect({ fields: [rot, exp], changeIdProb: 0.0, lerpLen: 4, normalize: false, rng: 0 });
  // Start on the rotation and force a switch to the expansion
  f.lastIdx = [0];
  f.currentField = new ff.FieldSum({ fields: [rot] });
  f.nextField = new ff.FieldSum({ fields: [exp] });
  const x = v(1, 0);
  const steps = [];
  for (let k = 0; k < 6; k++) steps.push(f.at(x));
  [0.0, 0.25, 0.5, 0.75].forEach((t, k) => near(steps[k], blend(rot.at(x), exp.at(x), t), `step ${k}`));
  near(steps[4], exp.at(x), "step 4");
  near(steps[5], exp.at(x), "step 5");
});

test("without lerpLen the switch is immediate", () => {
  const rot = new ff.RotationField({ center: [0, 0] });
  const exp = new ff.ExpansionField({ center: [0, 0] });
  const f = new ff.FieldSelect({ fields: [rot, exp], changeIdProb: 0.0, normalize: false, rng: 0 });
  f.lastIdx = [0];
  f.currentField = new ff.FieldSum({ fields: [rot] });
  f.nextField = new ff.FieldSum({ fields: [exp] });
  near(f.at(v(1, 0)), exp.at(v(1, 0)), "first call");
});

test("the first selection uses the weights at the first point", () => {
  const rot = new ff.RotationField({ center: [0, 0] });
  const exp = new ff.ExpansionField({ center: [1, 0] });
  const weights = [new ff.GaussianField({ center: [-1, 0], sigma: 0.3 }),
                   new ff.GaussianField({ center: [1, 0], sigma: 0.3 })];
  for (let seed = 0; seed < 10; seed++) {
    const f = new ff.FieldSelect({ fields: [rot, exp], weights, changeIdProb: 0.0, rng: seed });
    f.at(v(1, 0.1));
    assert.deepEqual([...f.lastIdx], [1], `seed ${seed}`);
  }
});

test("fields with weight 0 are never selected", () => {
  const rot = new ff.RotationField({ center: [0, 0] });
  const exp = new ff.ExpansionField({ center: [1, 0] });
  const f = new ff.FieldSelect({ fields: [rot, exp], weights: [0.0, 1.0], selectN: 2, rng: 0 });
  for (let k = 0; k < 20; k++) assert.deepEqual([...f.selectIndex(v(0.3, 0.4))], [1]);
});

test("all-zero weights do not crash", () => {
  const rot = new ff.RotationField({ center: [0, 0] });
  const exp = new ff.ExpansionField({ center: [1, 0] });
  const f = new ff.FieldSelect({ fields: [rot, exp], weights: [0.0, 0.0], changeIdProb: 1.0, rng: 0 });
  for (const x of [v(0.3, 0.4), v(-1, 2), v(2, 0.5)]) {
    const y = f.at(x);
    assert.ok(Number.isFinite(y.x) && Number.isFinite(y.y));
  }
});

test("the same seed gives the same sequence", () => {
  const fields = [new ff.RotationField({ center: [0, 0] }), new ff.ExpansionField({ center: [1, 0] }),
                  new ff.RotationField({ center: [1, 1] })];
  const run = (seed) => {
    const f = new ff.FieldSelect({ fields, changeIdProb: 0.3, lerpLen: 3, selectN: 2, rng: seed });
    const out = [];
    for (let k = 0; k < 40; k++) out.push(f.at(v(Math.cos(k), Math.sin(k))).array());
    return JSON.stringify(out);
  };
  assert.equal(run(5), run(5));
  assert.notEqual(run(5), run(6));
});
