// flowfields.js — p5.js port of the flowfields Python library.
//
// GENERATED from src/flowfields by the port-js skill (.claude/skills/port-js).
// Do not edit by hand: change the Python code and run /port-js again.
//
// source-commit: 3c95674
//
// Not ported yet:     FieldSelect
// Python-only:        utils.open_image (use imageToMatrix), MatrixField.plot_figure
//
// Usage: load p5.js, then this file, and build fields inside setup() or later
// (p5 2.x only finishes setting up p5.Vector when the sketch starts).
//
//   const { RotationField, GaussianField, FieldSum } = flowfields;

(function (root) {
  "use strict";

  // ---------------------------------------------------------------------------
  // Helpers shared by the port (no Python counterpart)
  // ---------------------------------------------------------------------------

  /** Makes a 2D p5.Vector. */
  function vec(x, y) {
    return new p5.Vector(x, y);
  }

  /** Accepts a p5.Vector or an [x, y] array and returns a new p5.Vector. */
  function asVector(v) {
    if (Array.isArray(v)) return vec(v[0], v[1]);
    return vec(v.x, v.y);
  }

  /** Rounds half to even, like Python's round(). */
  function roundHalfEven(x) {
    const r = Math.round(x);
    if (Math.abs(x % 1) === 0.5 && r % 2 !== 0) return r - 1;
    return r;
  }

  // ---------------------------------------------------------------------------
  // Random generator — stands in for numpy.random.Generator.
  // Same method names as numpy, so ported code reads the same. The streams are
  // different from numpy's: the same seed gives different numbers in each
  // language.
  // ---------------------------------------------------------------------------

  class Generator {
    constructor(seed) {
      if (seed === undefined || seed === null) {
        seed = Math.floor(Math.random() * 2 ** 32);
      }
      // splitmix32 spreads the seed over the four sfc32 words
      let s = seed >>> 0;
      const next = () => {
        s = (s + 0x9e3779b9) >>> 0;
        let z = s;
        z = Math.imul(z ^ (z >>> 16), 0x85ebca6b);
        z = Math.imul(z ^ (z >>> 13), 0xc2b2ae35);
        return (z ^ (z >>> 16)) >>> 0;
      };
      this._s = [next(), next(), next(), next()];
      this._spare = null;
    }

    /** Uniform float in [0, 1). sfc32. */
    random() {
      const s = this._s;
      const t = (((s[0] + s[1]) >>> 0) + s[3]) >>> 0;
      s[3] = (s[3] + 1) >>> 0;
      s[0] = s[1] ^ (s[1] >>> 9);
      s[1] = (s[2] + (s[2] << 3)) >>> 0;
      s[2] = (s[2] << 21) | (s[2] >>> 11);
      s[2] = (s[2] + t) >>> 0;
      return t / 4294967296;
    }

    /** Uniform float in [low, high). */
    uniform(low = 0.0, high = 1.0) {
      return low + (high - low) * this.random();
    }

    /** Normal float with mean loc and standard deviation scale. Box–Muller. */
    normal(loc = 0.0, scale = 1.0) {
      if (this._spare !== null) {
        const z = this._spare;
        this._spare = null;
        return loc + scale * z;
      }
      let u = 0;
      while (u === 0) u = this.random();
      const v = this.random();
      const r = Math.sqrt(-2.0 * Math.log(u));
      this._spare = r * Math.sin(2 * Math.PI * v);
      return loc + scale * r * Math.cos(2 * Math.PI * v);
    }

    /** Integer in [low, high), or in [0, low) when high is omitted, like numpy. */
    integers(low, high) {
      if (high === undefined || high === null) {
        high = low;
        low = 0;
      }
      return low + Math.floor(this.random() * (high - low));
    }

    /**
     * Draws integers from range(n), like numpy's choice(n, size, replace, p).
     * Returns one integer when size is undefined, otherwise an array.
     */
    choice(n, { size, replace = true, p } = {}) {
      const probs = p ? p.slice() : new Array(n).fill(1.0 / n);
      const drawOne = () => {
        const total = probs.reduce((a, b) => a + b, 0);
        let u = this.random() * total;
        let last = -1;
        for (let i = 0; i < n; i++) {
          if (probs[i] <= 0) continue;
          last = i;
          u -= probs[i];
          if (u < 0) return i;
        }
        return last; // only reached through rounding
      };
      if (size === undefined) return drawOne();
      const out = [];
      for (let k = 0; k < size; k++) {
        const i = drawOne();
        out.push(i);
        if (!replace) probs[i] = 0;
      }
      return out;
    }
  }

  /**
   * Like numpy.random.default_rng: a Generator stays as it is, a number is
   * used as a seed, and undefined/null takes a fresh seed.
   */
  function defaultRng(rng) {
    if (rng instanceof Generator) return rng;
    return new Generator(rng);
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/utils.py
  // ---------------------------------------------------------------------------

  function _sqDist(a, b) {
    let s = 0;
    for (let d = 0; d < a.length; d++) {
      const t = a[d] - b[d];
      s += t * t;
    }
    return s;
  }

  /** Index of the nearest center to each point; ties go to the first one. */
  function _nearestCenter(data, centers) {
    return data.map((point) => {
      let best = Infinity;
      let label = 0;
      centers.forEach((center, k) => {
        const d = _sqDist(point, center);
        if (d < best) {
          best = d;
          label = k;
        }
      });
      return label;
    });
  }

  /**
   * k-means++ initialization, then Lloyd's algorithm. data is an array of
   * points (arrays of numbers). Returns [centers, labels].
   */
  function kmeans(data, nClusters, rng = null, maxIter = 100, tol = 1e-4) {
    rng = defaultRng(rng);
    const nPoints = data.length;
    if (!(nClusters >= 1 && nClusters <= nPoints)) {
      throw new Error(`n_clusters must be between 1 and ${nPoints}, got ${nClusters}`);
    }
    const nDims = data[0].length;

    // k-means++ initialization
    const centers = [data[rng.integers(nPoints)].slice()];
    const distances = data.map((point) => _sqDist(point, centers[0]));
    for (let k = 1; k < nClusters; k++) {
      const total = distances.reduce((a, b) => a + b, 0);
      let idx;
      if (total > 0) {
        idx = rng.choice(nPoints, { p: distances.map((d) => d / total) });
      } else { // every point is already on a center
        idx = rng.integers(nPoints);
      }
      centers.push(data[idx].slice());
      data.forEach((point, i) => {
        distances[i] = Math.min(distances[i], _sqDist(point, centers[k]));
      });
    }

    // Lloyd's algorithm
    let meanVar = 0;
    for (let d = 0; d < nDims; d++) {
      let m = 0;
      for (const point of data) m += point[d];
      m /= nPoints;
      let v = 0;
      for (const point of data) v += (point[d] - m) ** 2;
      meanVar += v / nPoints;
    }
    const threshold = tol * (meanVar / nDims);
    let labels = _nearestCenter(data, centers);
    for (let iter = 0; iter < maxIter; iter++) {
      const sums = centers.map(() => new Array(nDims).fill(0));
      const counts = new Array(nClusters).fill(0);
      data.forEach((point, i) => {
        counts[labels[i]] += 1;
        for (let d = 0; d < nDims; d++) sums[labels[i]][d] += point[d];
      });
      let moved = 0.0;
      for (let k = 0; k < nClusters; k++) {
        if (counts[k] > 0) {
          const newCenter = sums[k].map((s) => s / counts[k]);
          moved += _sqDist(newCenter, centers[k]);
          centers[k] = newCenter;
        }
      }
      const newLabels = _nearestCenter(data, centers);
      if (newLabels.every((l, i) => l === labels[i])) break;
      labels = newLabels;
      if (moved <= threshold) break;
    }

    return [centers, labels];
  }

  /** Normalize a vector. A zero vector is returned unchanged. */
  function normalizeVector(v) {
    const norm = v.mag();
    if (norm === 0) return v.copy();
    return p5.Vector.div(v, norm);
  }

  /** Clamp a vector's length between minLength and maxLength. */
  function clampVector(v, minLength, maxLength) {
    const norm = v.mag();
    if (norm === 0) return v.copy();
    const clampedNorm = clamp(norm, minLength, maxLength);
    return p5.Vector.mult(v, clampedNorm / norm);
  }

  /** Linear interpolation between two vectors. */
  function lerp(a, b, t) {
    return p5.Vector.add(p5.Vector.mult(a, 1 - t), p5.Vector.mult(b, t));
  }

  /** Clamp a value between minValue and maxValue. */
  function clamp(value, minValue, maxValue) {
    return Math.max(minValue, Math.min(value, maxValue));
  }

  /** Returns [radius, angle] of a 2D vector. */
  function cartesianToPolar(v) {
    const radius = v.mag();
    const angle = Math.atan2(v.y, v.x);
    return [radius, angle];
  }

  /** Converts polar coordinates to a 2D vector. */
  function polarToCartesian(radius, angle) {
    return vec(radius * Math.cos(angle), radius * Math.sin(angle));
  }

  /** Rotate a 2D vector by angle radians. */
  function rotateVector(v, angle) {
    const c = Math.cos(angle);
    const s = Math.sin(angle);
    return vec(c * v.x - s * v.y, s * v.x + c * v.y);
  }

  /** Round the angle of a 2D vector to one of nLevels directions. */
  function quantizeVector(v, nLevels) {
    const [radius, angle] = cartesianToPolar(v);
    const quantizedAngle =
      roundHalfEven((angle / (2 * Math.PI)) * nLevels) * ((2 * Math.PI) / nLevels);
    return polarToCartesian(radius, quantizedAngle);
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/scalar_fields/base.py
  // ---------------------------------------------------------------------------

  /** Abstract base class for scalar fields. Subclasses implement at(x). */
  class ScalarField {
    at(x) {
      throw new Error("Subclasses should implement this method.");
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/scalar_fields/constant.py
  // ---------------------------------------------------------------------------

  /** f(x) = value */
  class ConstantField extends ScalarField {
    constructor({ value = 1.0 } = {}) {
      super();
      this.value = value;
    }

    at(x) {
      return this.value;
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/scalar_fields/gaussian.py
  // ---------------------------------------------------------------------------

  /** f(x) = scale * exp(-||x - center||^2 / (2 * sigma^2)) */
  class GaussianField extends ScalarField {
    constructor({ center, sigma = 1.0, scale = 1.0 }) {
      super();
      this.center = asVector(center);
      this.sigma = sigma;
      this.scale = scale;
    }

    at(x) {
      const d = p5.Vector.sub(x, this.center);
      return this.scale * Math.exp(-d.magSq() / (2 * this.sigma ** 2));
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/scalar_fields/box.py
  // ---------------------------------------------------------------------------

  /** insideValue inside the box (borders included), outsideValue elsewhere. */
  class BoxField extends ScalarField {
    constructor({ minCorner, maxCorner, insideValue = 1.0, outsideValue = 0.0 }) {
      super();
      const a = asVector(minCorner);
      const b = asVector(maxCorner);
      this.minCorner = vec(Math.min(a.x, b.x), Math.min(a.y, b.y));
      this.maxCorner = vec(Math.max(a.x, b.x), Math.max(a.y, b.y));
      this.insideValue = insideValue;
      this.outsideValue = outsideValue;
    }

    at(x) {
      if (
        x.x >= this.minCorner.x && x.y >= this.minCorner.y &&
        x.x <= this.maxCorner.x && x.y <= this.maxCorner.y
      ) {
        return this.insideValue;
      }
      return this.outsideValue;
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/scalar_fields/matrix.py
  // ---------------------------------------------------------------------------

  /**
   * Bilinear interpolation of a matrix (array of rows) over a box. The first
   * row is at the top of the box (highest y). The field is 0 outside the box.
   */
  class MatrixField extends ScalarField {
    constructor({ minCorner, maxCorner, data, normalize = false }) {
      super();
      const a = asVector(minCorner);
      const b = asVector(maxCorner);
      this.minCorner = vec(Math.min(a.x, b.x), Math.min(a.y, b.y));
      this.maxCorner = vec(Math.max(a.x, b.x), Math.max(a.y, b.y));
      this.data = data;
      this.normalize = normalize;
      if (this.normalize) {
        let lo = Infinity;
        for (const row of this.data) for (const v of row) lo = Math.min(lo, v);
        this.data = this.data.map((row) => row.map((v) => v - lo));
        let hi = -Infinity;
        for (const row of this.data) for (const v of row) hi = Math.max(hi, v);
        if (hi > 0) this.data = this.data.map((row) => row.map((v) => v / hi));
      }
    }

    _inside(x) {
      return (
        x.x >= this.minCorner.x && x.y >= this.minCorner.y &&
        x.x <= this.maxCorner.x && x.y <= this.maxCorner.y
      );
    }

    _interpolate(x) {
      const tx = clamp((x.x - this.minCorner.x) / (this.maxCorner.x - this.minCorner.x), 0.0, 1.0);
      const ty = clamp((x.y - this.minCorner.y) / (this.maxCorner.y - this.minCorner.y), 0.0, 1.0);
      // data is indexed [row][col]: row grows downward (cartesian y, flipped)
      // and col grows rightward (cartesian x).
      const r = (1.0 - ty) * (this.data.length - 1);
      const c = tx * (this.data[0].length - 1);
      const r0 = Math.floor(r), r1 = Math.ceil(r);
      const c0 = Math.floor(c), c1 = Math.ceil(c);
      const wr = r - r0, wc = c - c0;
      const v00 = this.data[r0][c0];
      const v01 = this.data[r0][c1];
      const v10 = this.data[r1][c0];
      const v11 = this.data[r1][c1];
      return (
        (1 - wr) * (1 - wc) * v00 +
        (1 - wr) * wc * v01 +
        wr * (1 - wc) * v10 +
        wr * wc * v11
      );
    }

    at(x) {
      if (this._inside(x)) return this._interpolate(x);
      return 0.0;
    }
  }

  /** A MatrixField multiplied by a Gaussian centred on its box. */
  class KernelProbabilisticMatrixField extends MatrixField {
    constructor({ minCorner, maxCorner, data, normalize = false, sigma = 1.0 }) {
      super({ minCorner, maxCorner, data, normalize });
      this.sigma = sigma;
    }

    at(x) {
      if (this._inside(x)) {
        const center = p5.Vector.add(this.minCorner, this.maxCorner).div(2);
        const distance = p5.Vector.sub(x, center).mag();
        const weight = Math.exp(-0.5 * (distance / this.sigma) ** 2);
        return weight * this._interpolate(x);
      }
      return 0.0;
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/vector_fields/base.py
  // ---------------------------------------------------------------------------

  /** Abstract base class for 2D vector fields. Subclasses implement at(x). */
  class FlowField {
    at(x) {
      throw new Error("Subclasses should implement this method.");
    }
  }

  /** Evaluates a weight that is either a number or a ScalarField. */
  function weightAt(weight, x) {
    return weight instanceof ScalarField ? weight.at(x) : weight;
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/vector_fields/rotation.py
  // ---------------------------------------------------------------------------

  /** v(x) = direction * [-r_y, r_x], r = x - center */
  class RotationField extends FlowField {
    constructor({ center, direction = 1, normalize = true }) {
      super();
      this.center = asVector(center);
      this.direction = direction;
      this.normalize = normalize;
    }

    at(x) {
      const r = p5.Vector.sub(x, this.center);
      let y = vec(-r.y * this.direction, r.x * this.direction);
      if (this.normalize) y = normalizeVector(y);
      return y;
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/vector_fields/expansion.py
  // ---------------------------------------------------------------------------

  /** v(x) = direction * (x - center) */
  class ExpansionField extends FlowField {
    constructor({ center, direction = 1, normalize = true }) {
      super();
      this.center = asVector(center);
      this.direction = direction;
      this.normalize = normalize;
    }

    at(x) {
      let y = p5.Vector.sub(x, this.center).mult(this.direction);
      if (this.normalize) y = normalizeVector(y);
      return y;
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/vector_fields/noise.py
  // ---------------------------------------------------------------------------

  /** A fresh random vector at every call, regardless of x. */
  class NoiseField extends FlowField {
    constructor({ normalize = true, distribution = "gaussian", rng } = {}) {
      super();
      if (distribution !== "gaussian" && distribution !== "uniform") {
        throw new Error(`Unknown distribution: ${distribution}`);
      }
      this.normalize = normalize;
      this.distribution = distribution;
      this.rng = defaultRng(rng);
    }

    at(x) {
      let noise;
      if (this.distribution === "gaussian") {
        noise = vec(this.rng.normal(), this.rng.normal());
      } else {
        noise = vec(this.rng.uniform(-1.0, 1.0), this.rng.uniform(-1.0, 1.0));
      }
      if (this.normalize) noise = normalizeVector(noise);
      return noise;
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/vector_fields/sum.py
  // ---------------------------------------------------------------------------

  /** v(x) = sum_i w_i(x) * F_i(x) */
  class FieldSum extends FlowField {
    constructor({ fields, weights = null, normalize = true }) {
      super();
      this.listOfFields = fields;
      this.weights = weights;
      this.normalize = normalize;
    }

    at(x) {
      let y = vec(0, 0);
      this.listOfFields.forEach((field, idx) => {
        const y_ = field.at(x).copy();
        if (this.weights !== null) y_.mult(weightAt(this.weights[idx], x));
        y.add(y_);
      });
      if (this.normalize) y = normalizeVector(y);
      return y;
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/vector_fields/max.py
  // ---------------------------------------------------------------------------

  /** v(x) = F_i*(x), i* = argmax_i w_i(x) (first one on ties) */
  class FieldMax extends FlowField {
    constructor({ fields, weights = null, normalize = true }) {
      super();
      this.listOfFields = fields;
      this.weights = weights;
      this.normalize = normalize;
    }

    at(x) {
      let best = 0;
      let bestValue = -Infinity;
      this.listOfFields.forEach((field, idx) => {
        const value = this.weights !== null ? weightAt(this.weights[idx], x) : 1.0;
        if (value > bestValue) {
          bestValue = value;
          best = idx;
        }
      });
      let y = this.listOfFields[best].at(x);
      if (this.normalize) y = normalizeVector(y);
      return y;
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/color_fields/base.py
  // ---------------------------------------------------------------------------

  /** Abstract base: at(x) returns an [r, g, b] color. */
  class ColorField {
    at(x) {
      throw new Error("ColorField is an abstract class and cannot be called directly.");
    }
  }

  // ---------------------------------------------------------------------------
  // src/flowfields/color_fields/matrixcolorfield.py
  // ---------------------------------------------------------------------------

  /**
   * p_k(x) ∝ exp(z_k(x) / temperature), z_k(x) = fraction of the window's
   * pixels in palette color k. data is an array of rows of [r, g, b], as from
   * imageToMatrix(img, "RGB"); the first row is at the lowest y.
   */
  class MatrixColorField extends ColorField {
    constructor({
      minCorner, maxCorner, data, nColors, randomState = 0, kernelSize = 0.05,
      temperature = 1.0, rng,
    }) {
      super();
      this.minCorner = asVector(minCorner);
      this.maxCorner = asVector(maxCorner);
      this.data = data;
      this.nColors = nColors;
      this.randomState = randomState;
      this.kernelSize = kernelSize;
      this.temperature = temperature;
      this.rng = defaultRng(rng);

      // The palette: the nColors centers of the image's pixels, and the
      // palette color of every pixel
      const h = data.length;
      const w = data[0].length;
      const [palette, labels] = kmeans(data.flat(), nColors, this.randomState);
      this.palette = palette;

      // One integral image (2D prefix sum) per palette color, so windowed
      // pixel counts can be looked up in O(1) on every getProbs call.
      this._h = h;
      this._w = w;
      this.integralImages = [];
      for (let k = 0; k < nColors; k++) {
        const ii = new Int32Array((h + 1) * (w + 1));
        for (let r = 0; r < h; r++) {
          let rowSum = 0;
          for (let c = 0; c < w; c++) {
            rowSum += labels[r * w + c] === k ? 1 : 0;
            ii[(r + 1) * (w + 1) + (c + 1)] = ii[r * (w + 1) + (c + 1)] + rowSum;
          }
        }
        this.integralImages.push(ii);
      }
    }

    /** Probability of each palette color at x; points outside use the nearest point inside. */
    getProbs(x) {
      const tx = clamp((x.x - this.minCorner.x) / (this.maxCorner.x - this.minCorner.x), 0.0, 1.0);
      const ty = clamp((x.y - this.minCorner.y) / (this.maxCorner.y - this.minCorner.y), 0.0, 1.0);

      const h = this._h, w = this._w;
      const centerX = Math.trunc(tx * (w - 1));
      const centerY = Math.trunc(ty * (h - 1));
      const halfK = Math.trunc(this.kernelSize * Math.max(w, h) / 2);
      const xMin = Math.max(centerX - halfK, 0);
      const xMax = Math.min(centerX + halfK + 1, w);
      const yMin = Math.max(centerY - halfK, 0);
      const yMax = Math.min(centerY + halfK + 1, h);

      const at = (ii, r, c) => ii[r * (w + 1) + c];
      let z = this.integralImages.map((ii) =>
        at(ii, yMax, xMax) - at(ii, yMin, xMax) - at(ii, yMax, xMin) + at(ii, yMin, xMin));
      z = z.map((v) => Math.max(v, 1));
      const zSum = z.reduce((a, b) => a + b, 0);
      z = z.map((v) => v / zSum);
      const logits = z.map((v) => v / this.temperature);
      const maxLogit = Math.max(...logits);
      let probs = logits.map((v) => Math.exp(v - maxLogit));
      const pSum = probs.reduce((a, b) => a + b, 0);
      probs = probs.map((v) => v / pSum);
      if (probs.some(Number.isNaN)) throw new Error("NaN values found in probabilities.");
      return probs;
    }

    /** Draws a palette color for x and returns it as [r, g, b]. */
    at(x) {
      const probs = this.getProbs(x);
      const sample = this.rng.choice(this.nColors, { p: probs });
      return this.palette[sample].slice();
    }
  }

  // ---------------------------------------------------------------------------
  // p5 extras (no Python counterpart)
  // ---------------------------------------------------------------------------

  /**
   * Turns a loaded p5.Image into a matrix of floats in [0, 1], the JS
   * counterpart of utils.open_image. mode "L" gives an array of rows of
   * grayscale values (same weights as Pillow), and "RGB" gives rows of
   * [r, g, b].
   */
  function imageToMatrix(img, mode = "RGB") {
    img.loadPixels();
    const d = img.pixelDensity ? img.pixelDensity() : 1;
    const w = img.width * d;
    const h = img.height * d;
    const rows = [];
    for (let j = 0; j < h; j++) {
      const row = [];
      for (let i = 0; i < w; i++) {
        const k = 4 * (j * w + i);
        const r = img.pixels[k], g = img.pixels[k + 1], b = img.pixels[k + 2];
        if (mode === "L") {
          row.push(Math.round((r * 299 + g * 587 + b * 114) / 1000) / 255);
        } else {
          row.push([r / 255, g / 255, b / 255]);
        }
      }
      rows.push(row);
    }
    return rows;
  }

  const flowfields = {
    // random
    Generator, defaultRng,
    // utils
    normalizeVector, clampVector, lerp, clamp, cartesianToPolar,
    polarToCartesian, rotateVector, quantizeVector, kmeans,
    // scalar fields
    ScalarField, ConstantField, GaussianField, BoxField, MatrixField,
    KernelProbabilisticMatrixField,
    // vector fields
    FlowField, RotationField, ExpansionField, NoiseField, FieldSum, FieldMax,
    // color fields
    ColorField, MatrixColorField,
    // p5 extras
    vec, asVector, imageToMatrix,
  };

  root.flowfields = flowfields;
  if (typeof module !== "undefined" && module.exports) module.exports = flowfields;
})(typeof globalThis !== "undefined" ? globalThis : this);
