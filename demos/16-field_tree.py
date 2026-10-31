import numpy as np
import tstudio.scalar_fields as sf
import tstudio.vector_fields as vf
from tstudio.color_fields import MatrixColorField
from _common import EIFFEL_MAX, EIFFEL_MIN, EIFFEL_X, EIFFEL_Y, eiffel, panels, save, strokes

# Fields nest: this tree blends a spiral and a FieldMax, and the image decides
# where each branch counts. The same image gives the colors.
center = (EIFFEL_MIN + EIFFEL_MAX) / 2
spiral = vf.FieldSum(
    fields=[vf.RotationField(center), vf.ExpansionField(center)],
    weights=[1.0, 0.3],
)
regions = vf.FieldMax(
    fields=[vf.RotationField(np.array([0.3, 0.7]), direction=-1), vf.ExpansionField(np.array([1.2, 0.2]))],
    weights=[sf.GaussianField(np.array([0.3, 0.7]), sigma=0.4), sf.GaussianField(np.array([1.2, 0.2]), sigma=0.4)],
)
field = vf.FieldSum(
    fields=[spiral, regions, vf.NoiseField()],
    weights=[
        sf.MatrixField(EIFFEL_MIN, EIFFEL_MAX, eiffel("L"), normalize=True),
        sf.ConstantField(0.5),
        sf.ConstantField(0.2),
    ],
)

color_field = MatrixColorField(EIFFEL_MIN, EIFFEL_MAX, eiffel(), n_colors=16, temperature=0.05)
# MatrixColorField has y=0 at the top of the image, so y is flipped here.
color = lambda x: color_field(np.array([x[0], EIFFEL_MAX[1] - x[1]]))

fig, axes = panels(["image, fields and colors together"], EIFFEL_X, EIFFEL_Y)
strokes(axes[0], field, n_lines=6000, n_steps=8, color=color, alpha=0.8)
save(fig, __file__)
