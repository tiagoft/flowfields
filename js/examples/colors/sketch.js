// Lines that take their colors from an image, with MatrixColorField. Each
// line gets a color drawn from the palette of the image around its starting
// point. Field coordinates are pixels, with y growing downward as on the
// canvas, which matches MatrixColorField: the first row of the image is at
// the lowest y.
const {
  RotationField, NoiseField, FieldSum, GaussianField, MatrixColorField,
  Generator, imageToMatrix, vec,
} = flowfields;

let field;
let colors;
let rng;

async function setup() {
  const img = await loadImage("../../../demos/eiffel.jpeg");
  createCanvas(img.width, img.height);
  background("#f5f2eb");
  rng = new Generator(0);

  const center = vec(width * 0.5, height * 0.4);
  field = new FieldSum({
    fields: [
      new RotationField({ center }),
      new NoiseField({ rng }),
    ],
    weights: [
      new GaussianField({ center, sigma: width * 0.35 }),
      0.3,
    ],
  });

  // 12 colors from the image, drawn mostly from the most common color
  // around each point
  colors = new MatrixColorField({
    minCorner: [0, 0],
    maxCorner: [width - 1, height - 1],
    data: imageToMatrix(img, "RGB"),
    nColors: 12,
    temperature: 0.05,
    rng,
  });

  strokeWeight(0.8);
  noFill();
}

function draw() {
  if (!colors) return; // setup is still loading the image

  // a few lines per frame, so the drawing builds up
  for (let n = 0; n < 40; n++) {
    let x = vec(rng.uniform(0, width), rng.uniform(0, height));
    const [r, g, b] = colors.at(x);
    stroke(255 * r, 255 * g, 255 * b, 170);
    beginShape();
    for (let i = 0; i < 40; i++) {
      vertex(x.x, x.y);
      x = p5.Vector.add(x, p5.Vector.mult(field.at(x), 2));
    }
    endShape();
  }
  if (frameCount >= 150) noLoop();
}
