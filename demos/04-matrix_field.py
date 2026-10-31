from pathlib import Path

import numpy as np
import tstudio.scalar_fields as sf
import tstudio.vector_fields as vf
from _common import EIFFEL_MAX, EIFFEL_MIN, EIFFEL_X, EIFFEL_Y, eiffel, heatmap, panels, save, strokes

brightness = sf.MatrixField(EIFFEL_MIN, EIFFEL_MAX, eiffel("L"), normalize=True)
field = vf.ExpansionField(np.array([0.75, 0.2]))

fig, axes = panels(["the matrix", "lines fade where the image is bright"], EIFFEL_X, EIFFEL_Y)
heatmap(axes[0], brightness)
strokes(axes[1], field, n_lines=15000, n_steps=3, alpha=lambda x: (1 - brightness(x)) ** 2)
save(fig, __file__)

# MatrixField can also plot its own data.
brightness.plot_figure(Path(__file__).parent / "outputs" / f"{Path(__file__).stem}_plot.png")
