// Checks the JS port against js/test/fixtures.json, written by
// tools/export_fixtures.py from the Python library.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const { load } = require("./load");

const { p5, flowfields, close } = load();
test.after(close);

const { cases } = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures.json"), "utf8"));
const TOL = 1e-9;

const camel = (s) => s.replace(/_([a-z])/g, (_, c) => c.toUpperCase());

/** Builds a JS object from a fixture spec (see tools/export_fixtures.py). */
function build(spec) {
  if (Array.isArray(spec)) return spec.map(build);
  if (spec !== null && typeof spec === "object") {
    if ("vec" in spec) return new p5.Vector(spec.vec[0], spec.vec[1]);
    if ("array" in spec) return spec.array;
    if ("type" in spec) {
      const Cls = flowfields[spec.type];
      assert.ok(Cls, `flowfields.${spec.type} is missing`);
      const args = {};
      for (const [k, v] of Object.entries(spec.args)) args[camel(k)] = build(v);
      return new Cls(args);
    }
  }
  return spec;
}

/** Turns a JS result into plain numbers, like the Python side's to_json. */
function plain(value) {
  if (value instanceof p5.Vector) return [value.x, value.y];
  if (Array.isArray(value)) return value.map(plain);
  return value;
}

function close_(actual, expected, where) {
  if (Array.isArray(expected)) {
    assert.ok(Array.isArray(actual), `${where}: expected an array, got ${actual}`);
    assert.equal(actual.length, expected.length, `${where}: length`);
    expected.forEach((e, i) => close_(actual[i], e, `${where}[${i}]`));
    return;
  }
  const ok = Math.abs(actual - expected) <= TOL * Math.max(1, Math.abs(expected));
  assert.ok(ok, `${where}: got ${actual}, expected ${expected}`);
}

for (const c of cases) {
  if (c.kind === "scalar" || c.kind === "vector") {
    test(`${c.kind} ${c.name}`, () => {
      const field = build(c.spec);
      c.points.forEach((pt, i) => {
        const x = new p5.Vector(pt[0], pt[1]);
        const result = plain(field.at(x));
        close_(result, c.expected[i], `at (${pt})`);
        assert.deepEqual([x.x, x.y], pt, `at (${pt}): the input point was changed`);
      });
    });
  } else if (c.kind === "util") {
    test(`util ${c.name}(${JSON.stringify(c.args)})`, () => {
      const fn = flowfields[camel(c.fn)];
      assert.ok(fn, `flowfields.${camel(c.fn)} is missing`);
      const args = build(c.args);
      const before = JSON.stringify(plain(args));
      close_(plain(fn(...args)), c.expected, c.fn);
      assert.equal(JSON.stringify(plain(args)), before, "the arguments were changed");
    });
  } else if (c.kind === "stats") {
    test(`stats ${c.name}`, () => {
      const field = build(c.spec);
      const x = new p5.Vector(c.point[0], c.point[1]);
      const s = [];
      for (let k = 0; k < c.n; k++) s.push(plain(field.at(x)));
      const mean = (a) => a.reduce((p, q) => p + q, 0) / a.length;
      const variance = (a) => { const m = mean(a); return mean(a.map((v) => (v - m) ** 2)); };
      const norms = s.map(([a, b]) => Math.hypot(a, b));
      const got = {
        mean: [mean(s.map((v) => v[0])), mean(s.map((v) => v[1]))],
        var: [variance(s.map((v) => v[0])), variance(s.map((v) => v[1]))],
        mean_norm: mean(norms),
        var_norm: variance(norms),
      };
      // Different random streams, so only up to sampling error
      const e = c.expected;
      for (let i = 0; i < 2; i++) {
        const tolMean = 5 * Math.sqrt((e.var[i] + got.var[i]) / c.n) + 1e-12;
        assert.ok(Math.abs(got.mean[i] - e.mean[i]) <= tolMean, `mean[${i}]: got ${got.mean[i]}, expected ${e.mean[i]}`);
        assert.ok(Math.abs(got.var[i] - e.var[i]) <= 0.05 * e.var[i] + 1e-12, `var[${i}]: got ${got.var[i]}, expected ${e.var[i]}`);
      }
      assert.ok(Math.abs(got.mean_norm - e.mean_norm) <= 0.02 * e.mean_norm + 1e-9, `mean_norm: got ${got.mean_norm}, expected ${e.mean_norm}`);
      assert.ok(Math.abs(got.var_norm - e.var_norm) <= 0.05 * e.var_norm + 1e-9, `var_norm: got ${got.var_norm}, expected ${e.var_norm}`);

      // The same seed gives the same draws
      const a = build(c.spec), b = build(c.spec);
      for (let k = 0; k < 20; k++) assert.deepEqual(plain(a.at(x)), plain(b.at(x)), "same seed, different draws");
    });
  }
}
