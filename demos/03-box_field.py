import numpy as np
import tstudio.scalar_fields as sf
import tstudio.vector_fields as vf
from _common import heatmap, panels, save, strokes

box = sf.BoxField(np.array([-0.5, -0.3]), np.array([0.6, 0.5]))

# Used as a weight, the box turns a field on only inside of it.
field = vf.FieldSum(
    fields=[vf.RotationField(np.array([0.05, 0.1])), vf.ExpansionField(np.array([-1.0, -1.0]))],
    weights=[box, sf.ConstantField(0.1)],
)

fig, axes = panels(["the box", "rotation only inside the box"])
heatmap(axes[0], box)
strokes(axes[1], field, n_steps=60)
save(fig, __file__)
