// Loads p5.js and flowfields.js inside jsdom, as a browser page would, and
// returns { p5, flowfields, window, close }.
const fs = require("fs");
const path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

/** An object whose properties and calls all return more of the same. */
function anything() {
  const f = function () {};
  return new Proxy(f, {
    get: (_, key) => (key === Symbol.toPrimitive ? () => 0 : anything()),
    set: () => true,
    apply: () => anything(),
  });
}

function load() {
  const virtualConsole = new VirtualConsole(); // drops jsdom's canvas warnings
  const dom = new JSDOM("<body></body>", {
    pretendToBeVisual: true,
    runScripts: "outside-only",
    virtualConsole,
  });
  // jsdom has no canvas, so the sketch gets a context that accepts anything
  dom.window.HTMLCanvasElement.prototype.getContext = () => anything();
  const p5Source = fs.readFileSync(path.join(__dirname, "..", "node_modules", "p5", "lib", "p5.min.js"), "utf8");
  dom.window.eval(p5Source + ";window.p5 = p5;");
  // p5 2.x installs the argument handling of p5.Vector when the first sketch
  // starts, so an empty sketch is created before using the library.
  const sketch = new dom.window.p5(() => {});
  const flowfieldsSource = fs.readFileSync(path.join(__dirname, "..", "flowfields.js"), "utf8");
  dom.window.eval(flowfieldsSource);
  return {
    p5: dom.window.p5,
    flowfields: dom.window.flowfields,
    window: dom.window,
    close: () => { sketch.remove(); dom.window.close(); },
  };
}

module.exports = { load };
