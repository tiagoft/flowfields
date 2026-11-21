// The same idea as demos/_common.py strokes(): random starting points that
// follow the field for a few steps. Field coordinates are [-1, 1]², and
// toScreen maps them to the canvas (y up, as in the Python demos).
const { RotationField, ExpansionField, NoiseField, FieldSum, GaussianField, Generator, vec } = flowfields;

let field;
let rng;

function setup() {
  createCanvas(600, 600);
  background("#f5f2eb");
  rng = new Generator(0);

  const a = vec(-0.4, 0.2);
  const b = vec(0.5, -0.3);
  field = new FieldSum({
    fields: [
      new RotationField({ center: a }),
      new ExpansionField({ center: b, direction: -1 }),
      new NoiseField({ rng }),
    ],
    weights: [
      new GaussianField({ center: a, sigma: 0.6 }),
      new GaussianField({ center: b, sigma: 0.5 }),
      0.15,
    ],
  });
  stroke(50, 82, 123, 120);
  strokeWeight(0.7);
  noFill();
}

function toScreen(p) {
  return [map(p.x, -1, 1, 0, width), map(p.y, -1, 1, height, 0)];
}

function draw() {
  // a few lines per frame, so the drawing builds up
  for (let n = 0; n < 20; n++) {
    let x = vec(rng.uniform(-1, 1), rng.uniform(-1, 1));
    beginShape();
    for (let i = 0; i < 60; i++) {
      vertex(...toScreen(x));
      x = p5.Vector.add(x, p5.Vector.mult(field.at(x), 0.01));
    }
    endShape();
  }
  if (frameCount >= 200) noLoop();
}
